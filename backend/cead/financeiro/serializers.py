from datetime import date

from rest_framework import serializers

from cead.models import (
    EdEdital,
    FiEditalFuncaoOferta,
    FiFuncaoBolsista,
    FiPessoaFicha,
)

from .messages import (
    ERRO_DATA_INVALIDA,
    ERRO_FINANCEIRO_EDITAL_ASSOCIADO_FI_EDITAL_FUNCAO_OFERTA,
)


class BolsistaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nome = serializers.SerializerMethodField()
    edital = serializers.SerializerMethodField()
    data_inicio_vinculacao = serializers.DateField()
    data_fim_vinculacao = serializers.DateField(allow_null=True)

    def get_nome(self, obj) -> str:
        return str(obj.cm_pessoa)

    def get_edital(self, obj) -> str:
        if obj.ed_edital:
            return obj.ed_edital.numero_ano_edital()
        return "-"


class AtualizarDataVinculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiPessoaFicha
        fields = ["id", "data_inicio_vinculacao", "data_fim_vinculacao"]

    def validate(self, data):
        data_inicio = data.get("data_inicio_vinculacao")
        data_fim = data.get("data_fim_vinculacao")

        limite_inferior = date(2005, 1, 1)
        limite_superior = date(2050, 12, 31)

        if data_inicio < limite_inferior or data_inicio > limite_superior:
            raise serializers.ValidationError(ERRO_DATA_INVALIDA)
        if data_fim:
            if data_fim < limite_inferior or data_fim > limite_superior:
                raise serializers.ValidationError(ERRO_DATA_INVALIDA)
            if data_fim < data_inicio:
                raise serializers.ValidationError(ERRO_DATA_INVALIDA)

        return data


class EdEditalSerializer(serializers.ModelSerializer):
    descricao = serializers.SerializerMethodField()

    class Meta:
        model = EdEdital
        fields = ["id", "descricao"]

    def get_descricao(self, obj) -> str:
        return str(obj)


class ListarFuncoesComFichaUABSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiFuncaoBolsista
        fields = ["id", "funcao"]


# Precisa dos IDs para fazer a edicao, e das strings para mostrar na tela
class FiGetEditalFuncaoOfertaSerializer(serializers.ModelSerializer):
    edital = serializers.CharField(source="ed_edital.numero_ano_edital")
    funcao = serializers.CharField(source="fi_funcao_bolsista.__str__")
    oferta = serializers.CharField(source="ac_curso_oferta.__str__")

    ed_edital = serializers.IntegerField(source="ed_edital.id")
    fi_funcao_bolsista = serializers.IntegerField(source="fi_funcao_bolsista.id")
    ac_curso_oferta = serializers.IntegerField(source="ac_curso_oferta.id")

    class Meta:
        model = FiEditalFuncaoOferta
        fields = [
            "id",
            "ed_edital",
            "fi_funcao_bolsista",
            "ac_curso_oferta",
            "edital",
            "funcao",
            "oferta",
        ]


class FiPostEditalFuncaoOfertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiEditalFuncaoOferta
        fields = ["ed_edital", "fi_funcao_bolsista", "ac_curso_oferta"]

    def validate(self, data):
        ed_edital = data.get("ed_edital")
        instance_id = self.instance.id if self.instance else None

        # Verifica se ja existe outro registro com o mesmo ed_edital
        edital_funcao_oferta = FiEditalFuncaoOferta.objects.filter(ed_edital=ed_edital)

        if instance_id:
            # PUT (edicao): ignora a propria instancia
            edital_funcao_oferta = edital_funcao_oferta.exclude(id=instance_id)

        if edital_funcao_oferta.exists():
            raise serializers.ValidationError(
                ERRO_FINANCEIRO_EDITAL_ASSOCIADO_FI_EDITAL_FUNCAO_OFERTA
            )

        return data
