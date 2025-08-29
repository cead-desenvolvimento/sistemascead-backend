from rest_framework import serializers
from cead.models import TrEspacoFisico, TrTermo, TrTransmissao, TrTransmissaoHorario


class TermoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrTermo
        fields = ["termo"]


class EspacoFisicoSelecionarSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrEspacoFisico
        fields = ["id", "espaco_fisico"]


class DiasDisponiveisSerializer(serializers.Serializer):
    inicio_periodo = serializers.DateField()
    fim_periodo = serializers.DateField()
    datas_disponiveis = serializers.ListField(child=serializers.DateField())


# Para HorariosDisponiveisAPIView(APIView)
class HorarioSerializer(serializers.Serializer):
    inicio = serializers.CharField()
    fim = serializers.CharField()


class DiaDisponivelSerializer(serializers.Serializer):
    data = serializers.DateField()
    dia_semana = serializers.CharField()
    horarios = HorarioSerializer(many=True)


class ListaDiasDisponiveisSerializer(serializers.Serializer):
    dias = DiaDisponivelSerializer(many=True)


# Para ConfirmacaoTransmissaoAPIView(APIView)
class TrTransmissaoHorarioSerializer(serializers.ModelSerializer):
    inicio = serializers.DateTimeField(format="%Y-%m-%dT%H:%M")
    fim = serializers.DateTimeField(format="%Y-%m-%dT%H:%M")

    class Meta:
        model = TrTransmissaoHorario
        fields = ["inicio", "fim"]


class TransmissaoConfirmacaoSerializer(serializers.ModelSerializer):
    requisitante_nome = serializers.CharField(source="cm_pessoa.nome", read_only=True)
    requisitante_email = serializers.CharField(source="cm_pessoa.email", read_only=True)
    requisitante_cpf = serializers.SerializerMethodField()
    espaco_fisico = serializers.CharField(
        source="tr_espaco_fisico.espaco_fisico", read_only=True
    )
    horarios = serializers.SerializerMethodField()
    observacao = serializers.CharField()

    class Meta:
        model = TrTransmissao
        fields = [
            "requisitante_nome",
            "requisitante_email",
            "requisitante_cpf",
            "espaco_fisico",
            "horarios",
            "observacao",
        ]

    def get_requisitante_cpf(self, obj):
        return obj.cm_pessoa.cpf_com_pontos_e_traco()

    def get_horarios(self, obj):
        qs = TrTransmissaoHorario.objects.filter(tr_transmissao=obj).order_by("inicio")
        return TrTransmissaoHorarioSerializer(qs, many=True).data
