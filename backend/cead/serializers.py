import regex
from rest_framework import serializers

from cead.messages import ERRO_CPF_INVALIDO
from cead.models import (
    AcCurso,
    AcCursoOferta,
    CmPessoa,
    CmMunicipio,
    CmUf,
)

# ------------------------------
# Serializers relacionados a Curso
# ------------------------------


class AcCursoOfertaIdDescricaoSerializer(serializers.ModelSerializer):
    descricao = serializers.SerializerMethodField()

    class Meta:
        model = AcCursoOferta
        fields = ["id", "descricao"]

    def get_descricao(self, obj) -> str:
        return str(obj)


class AcCursoIdNomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcCurso
        fields = ["id", "nome"]


# ------------------------------
# Serializers relacionados a Pessoa
# ------------------------------


class CmPessoaNomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmPessoa
        fields = ["nome"]


class CmPessoaIdNomeCpfSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmPessoa
        fields = ["id", "nome", "cpf"]


class GetPessoaEmailSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = CmPessoa
        fields = ["nome", "email"]

    def get_nome(self, obj) -> str:
        return obj.nome.split(" ")[0]

    def get_email(self, obj) -> str:
        usuario, dominio = regex.split("@", obj.email)
        return f"{usuario[:2]}{'*' * len(usuario[2:])}@{dominio[:2]}{'*' * len(dominio[2:])}"


# ------------------------------
# Utilitários / Validações
# ------------------------------


class CPFSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=11)

    def validate_cpf(self, value):
        cpf = [int(char) for char in value if char.isdigit()]

        if len(cpf) != 11 or cpf == cpf[::-1]:
            raise serializers.ValidationError(ERRO_CPF_INVALIDO)

        for i in range(9, 11):
            val = sum((cpf[num] * ((i + 1) - num) for num in range(0, i)))
            digit = ((val * 10) % 11) % 10
            if digit != cpf[i]:
                raise serializers.ValidationError(ERRO_CPF_INVALIDO)

        return "".join(map(str, cpf))
