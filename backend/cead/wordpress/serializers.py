from rest_framework import serializers
from cead.models import AcCurso, AcPolo
from cead.serializers import CmPessoaNomeSerializer


class AcCursoAtivoSerializer(serializers.ModelSerializer):
    cm_pessoa_coordenador = CmPessoaNomeSerializer()

    class Meta:
        model = AcCurso
        fields = ["nome", "cm_pessoa_coordenador"]


class AcCursoContatoSerializer(serializers.ModelSerializer):
    cm_pessoa_coordenador = CmPessoaNomeSerializer()
    telefone_formatado = serializers.SerializerMethodField()

    class Meta:
        model = AcCurso
        fields = ["nome", "email", "cm_pessoa_coordenador", "telefone_formatado"]

    def get_telefone_formatado(self, obj):
        return obj.telefone_formatado()


class AcCursoDescricaoPerfilEgressoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcCurso
        fields = ["descricao", "perfil_egresso"]


class AcPoloSerializer(serializers.ModelSerializer):
    cm_pessoa_coordenador = serializers.CharField(
        source="cm_pessoa_coordenador.nome", read_only=True
    )
    cep_formatado = serializers.SerializerMethodField()
    telefone_formatado = serializers.SerializerMethodField()
    municipio_uf = serializers.SerializerMethodField()

    class Meta:
        model = AcPolo
        fields = [
            "id",
            "cm_pessoa_coordenador",
            "nome",
            "email",
            "ativo",
            "latitude",
            "longitude",
            "apresentacao",
            "telefone_formatado",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cep_formatado",
            "municipio_uf",
        ]

    def get_cep_formatado(self, obj):
        return obj.cep_formatado()

    def get_telefone_formatado(self, obj):
        return obj.telefone_formatado()

    def get_municipio_uf(self, obj):
        if obj.cm_municipio:
            return obj.cm_municipio.get_municipio_uf()
        return None


class AcPoloApresentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcPolo
        fields = ["apresentacao"]


class AcPoloInformacoesSerializer(serializers.ModelSerializer):
    cep_formatado = serializers.SerializerMethodField()
    telefone_formatado = serializers.SerializerMethodField()
    municipio_uf = serializers.SerializerMethodField()

    class Meta:
        model = AcPolo
        fields = [
            "nome",
            "email",
            "ativo",
            "latitude",
            "longitude",
            "apresentacao",
            "telefone_formatado",
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "cep_formatado",
            "municipio_uf",
        ]

    def get_cep_formatado(self, obj):
        return obj.cep_formatado()

    def get_telefone_formatado(self, obj):
        if obj.ddd and obj.telefone:
            return obj.telefone_formatado()
        return None

    def get_municipio_uf(self, obj):
        if obj.cm_municipio:
            return obj.cm_municipio.get_municipio_uf()
        return None


class AcPoloNomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcPolo
        fields = ["nome"]
