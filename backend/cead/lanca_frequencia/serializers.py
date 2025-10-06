from rest_framework import serializers

from cead.models import (
    AcCurso,
    AcDisciplina,
    FiDatafrequencia,
    FiFrequencia,
    FiFrequenciaDisciplina,
    FiFuncaoBolsista,
    FiPessoaFicha,
)
from cead.serializers import CmPessoaNomeSerializer
from .utils import get_datafrequencia_mes_anterior, get_datafrequencia_mes_atual


# Para imprimir em relatorio nao precisa de id
class AcCursoNomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcCurso
        fields = ["nome"]


# Para levar para uma tela de selecao simples de disciplinas
# Utilizado em FrequenciaMesAnteriorSerializer
class AcDisciplinaIdNomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcDisciplina
        fields = ["id", "nome"]


class AcDisciplinaNomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcDisciplina
        fields = ["nome"]


# Para GET na tela onde eu ja tenho um curso selecionado
class AcDisciplinaSemCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcDisciplina
        exclude = ["ac_curso"]


# Nao preciso do id para o POST, busca do kwargs
class AcDisciplinaSemIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcDisciplina
        exclude = ["id"]


# Para o mixin de PUT e DELETE
class AcDisciplinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcDisciplina
        fields = "__all__"


class FiDatafrequenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiDatafrequencia
        fields = "__all__"


class FiFuncaoBolsistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiFuncaoBolsista
        fields = ["funcao"]


# Associa os bolsistas com funcao e disciplinas lancadas para get_datafrequencia_mes_anterior()
# Serve para marcar na tela com mais facilidade as disciplinas do mes passado
# Tem uma funcao do mes atual, a diferenca e' que nao vem o id na outra, p/ proteger relatorio
class FiPessoaFichaFuncaoDisciplinaMesAnteriorSerializer(serializers.ModelSerializer):
    cm_pessoa = serializers.CharField(source="cm_pessoa.nome")
    cpf = serializers.SerializerMethodField()
    fi_funcao_bolsista = serializers.CharField(source="fi_funcao_bolsista.funcao")
    disciplinas = serializers.SerializerMethodField()

    class Meta:
        model = FiPessoaFicha
        fields = ["id", "cm_pessoa", "cpf", "fi_funcao_bolsista", "disciplinas"]

    def get_cpf(self, obj):
        return obj.cm_pessoa.cpf_com_pontos_e_traco()

    def get_disciplinas(self, obj):
        datafrequencia_ref = get_datafrequencia_mes_anterior()
        if not datafrequencia_ref:
            return []

        ref_id = datafrequencia_ref.id

        # Verifica nos ultimos 4 meses se há frequência lançada
        datafrequencias_candidatas = FiDatafrequencia.objects.filter(
            id__lte=ref_id,
            id__gte=ref_id - 3
        ).order_by("-id")

        ultimo_datafrequencia_valido = None

        # Percorre do mais recente ao mais antigo e acha o último lançamento válido
        for datafrequencia in datafrequencias_candidatas:
            if FiFrequencia.objects.filter(
                fi_datafrequencia=datafrequencia,
                cm_pessoa=obj.cm_pessoa,
            ).exists():
                ultimo_datafrequencia_valido = datafrequencia
                break

        if not ultimo_datafrequencia_valido:
            return []

        # Busca disciplinas lançadas naquele mês
        disciplinas_ids = FiFrequenciaDisciplina.objects.filter(
            fi_frequencia__fi_datafrequencia=ultimo_datafrequencia_valido,
            fi_frequencia__cm_pessoa=obj.cm_pessoa,
        ).values_list("ac_disciplina_id", flat=True)

        # Filtra disciplinas ativas e do curso em questão
        curso = getattr(getattr(obj, "ac_curso_oferta", None), "ac_curso", None)
        if not curso:
            return list(disciplinas_ids)

        disciplinas_filtradas = AcDisciplina.objects.filter(
            id__in=disciplinas_ids,
            ativa=True,
            ac_curso=curso,
        ).values_list("id", flat=True)

        return list(disciplinas_filtradas)


class FrequenciaMesAnteriorSerializer(serializers.Serializer):
    coordenador = CmPessoaNomeSerializer()
    curso = AcCursoNomeSerializer()
    bolsistas = serializers.SerializerMethodField()
    disciplinas_do_curso = AcDisciplinaIdNomeSerializer(many=True)

    def get_bolsistas(self, obj):
        return FiPessoaFichaFuncaoDisciplinaMesAnteriorSerializer(
            self.context.get("bolsistas", []), many=True
        ).data


class FiPessoaFichaFuncaoDisciplinaMesAtualSerializer(serializers.ModelSerializer):
    cm_pessoa = serializers.CharField(source="cm_pessoa.nome")
    cpf = serializers.SerializerMethodField()
    fi_funcao_bolsista = serializers.CharField(source="fi_funcao_bolsista.funcao")
    disciplinas = serializers.SerializerMethodField()

    class Meta:
        model = FiPessoaFicha
        fields = ["cm_pessoa", "cpf", "fi_funcao_bolsista", "disciplinas"]

    def get_cpf(self, obj):
        return obj.cm_pessoa.cpf_com_pontos_e_traco()

    def get_disciplinas(self, obj):
        frequencias_disciplinas = FiFrequenciaDisciplina.objects.filter(
            fi_frequencia__fi_datafrequencia=get_datafrequencia_mes_atual(),
            fi_frequencia__cm_pessoa=obj.cm_pessoa,
            fi_frequencia__cm_pessoa_coordenador=obj.ac_curso_oferta.ac_curso.cm_pessoa_coordenador,
        ).select_related("ac_disciplina")

        return AcDisciplinaNomeSerializer(
            [freq.ac_disciplina for freq in frequencias_disciplinas], many=True
        ).data


class FrequenciaMesAtualSerializer(serializers.Serializer):
    coordenador = CmPessoaNomeSerializer()
    curso = AcCursoNomeSerializer()
    bolsistas = serializers.SerializerMethodField()

    def get_bolsistas(self, obj):
        return FiPessoaFichaFuncaoDisciplinaMesAtualSerializer(
            self.context.get("bolsistas", []), many=True
        ).data
