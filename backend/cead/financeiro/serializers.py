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
    edital = serializers.SerializerMethodField()
    funcao = serializers.SerializerMethodField()
    oferta = serializers.SerializerMethodField()

    ed_edital = serializers.IntegerField(source="ed_edital_id")
    fi_funcao_bolsista = serializers.IntegerField(source="fi_funcao_bolsista_id")
    ac_curso_oferta = serializers.IntegerField(
        source="ac_curso_oferta_id", allow_null=True
    )

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

    def get_edital(self, obj):
        return obj.ed_edital.numero_ano_edital()

    def get_funcao(self, obj):
        return str(obj.fi_funcao_bolsista) if obj.fi_funcao_bolsista_id else None

    def get_oferta(self, obj):
        return str(obj.ac_curso_oferta) if obj.ac_curso_oferta_id else None


class FiPostEditalFuncaoOfertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiEditalFuncaoOferta
        fields = ["ed_edital", "fi_funcao_bolsista", "ac_curso_oferta"]
        # Desabilita validadores do DRF: NULL = NULL e' indefinido no SQL92
        validators = []

    def validate(self, data):
        ed_edital = data.get("ed_edital")
        fi_funcao_bolsista = data.get("fi_funcao_bolsista")
        ac_curso_oferta = data.get("ac_curso_oferta")

        qs = FiEditalFuncaoOferta.objects.filter(
            ed_edital=ed_edital, fi_funcao_bolsista=fi_funcao_bolsista
        )
        # Faz a validacao da regra, como em NULLS NOT DISTINCT
        edital_funcao_oferta_exists = (
            qs.filter(ac_curso_oferta__isnull=True).exists()
            if ac_curso_oferta is None
            else qs.filter(ac_curso_oferta=ac_curso_oferta).exists()
        )

        if edital_funcao_oferta_exists:
            raise serializers.ValidationError(
                ERRO_FINANCEIRO_EDITAL_ASSOCIADO_FI_EDITAL_FUNCAO_OFERTA
            )

        return data
