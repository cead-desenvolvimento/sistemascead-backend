import regex
import requests

from django.db import transaction
from rest_framework import serializers

from cead.models import (
    AcCursoOferta,
    CmMunicipio,
    CmPessoa,
    CmPessoaBanco,
    CmPessoaEndereco,
    CmPessoaTelefone,
    CmUf,
    FiEditalFuncaoOferta,
    FiFuncaoBolsista,
    FiPessoaFicha,
)
from cead.utils import maiusculas_nomes

from .messages import *


## BLOCO: Município e UF
class CmUfSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmUf
        fields = ["sigla", "uf"]


class CmMunicipioSerializer(serializers.ModelSerializer):
    cm_uf = CmUfSerializer()

    class Meta:
        model = CmMunicipio
        fields = ["municipio", "cm_uf"]


class CmMunicipioIdSerializer(serializers.ModelSerializer):
    cm_uf = CmUfSerializer()

    class Meta:
        model = CmMunicipio
        fields = ["id", "municipio", "cm_uf"]


## BLOCO: pessoa
class CmPessoaNomeCpfFormatadoEmailGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmPessoa
        fields = ["nome", "cpf_com_pontos_e_traco", "email"]


## BLOCO: banco
class CmPessoaBancoGetSerializer(serializers.ModelSerializer):
    nome_banco = serializers.SerializerMethodField()

    class Meta:
        model = CmPessoaBanco
        fields = [
            "codigo_banco",
            "agencia",
            "conta",
            "digito_verificador_conta",
            "nome_banco",
        ]

    def get_nome_banco(self, obj) -> str:
        request_api_nome_banco = requests.get(
            f"https://brasilapi.com.br/api/banks/v1/{obj.codigo_banco}"
        ).json()
        return request_api_nome_banco.get("fullName", "")


class CmPessoaBancoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmPessoaBanco
        exclude = ["cm_pessoa"]

    def create(self, validated_data):
        cm_pessoa = self.context.get("cm_pessoa")
        return CmPessoaBanco.objects.create(cm_pessoa=cm_pessoa, **validated_data)


## BLOCO: endereço
class CmPessoaEnderecoGetSerializer(serializers.ModelSerializer):
    cm_municipio = CmMunicipioSerializer(read_only=True)
    cep_formatado = serializers.SerializerMethodField()

    class Meta:
        model = CmPessoaEndereco
        exclude = ["id", "cm_pessoa"]

    def get_cep_formatado(self, obj):
        return obj.cep_formatado()


class CmPessoaEnderecoPostSerializer(serializers.ModelSerializer):
    cm_municipio = CmMunicipioSerializer(read_only=True)

    class Meta:
        model = CmPessoaEndereco
        fields = "__all__"

    # Revisitar isso aqui: nao sei como vai fazer na tela
    def validate_numero(self, value):
        if value == "":
            return None
        return value

    def validate_complemento(self, value):
        if value == "":
            return None
        return value

    def create(self, validated_data):
        cm_municipio_data = validated_data.pop("cm_municipio")
        cm_uf_data = cm_municipio_data.pop("cm_uf")

        try:
            cm_uf = CmUf.objects.get(sigla=cm_uf_data["sigla"], uf=cm_uf_data["uf"])
        except CmUf.DoesNotExist:
            raise serializers.ValidationError(ERRO_UF_INVALIDA)
        try:
            cm_municipio = CmMunicipio.objects.get(
                municipio=cm_municipio_data["municipio"], cm_uf=cm_uf
            )
        except CmMunicipio.DoesNotExist:
            raise serializers.ValidationError({"cm_municipio": ERRO_MUNICIPIO_INVALIDO})

        return CmPessoaEndereco.objects.create(
            cm_municipio=cm_municipio,
            cm_pessoa=self.context.get("cm_pessoa"),
            **validated_data,
        )


## BLOCO: telefone
class CmPessoaTelefoneGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmPessoaTelefone
        fields = ["ddd", "numero"]


class CmPessoaTelefonePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmPessoaTelefone
        exclude = ["cm_pessoa"]  # Passa a pessoa explicitamente na chamada

    def create(self, validated_data):
        return CmPessoaTelefone.objects.create(
            cm_pessoa=self.context.get("cm_pessoa"), **validated_data
        )


## BLOCO: dados complementares da ficha
class FiFuncaoBolsistaGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiFuncaoBolsista
        # Vai com id para facilitar POST, ja que nao tem como mudar na tela
        fields = ["id", "funcao"]


class FiPessoaFichaGetSerializer(serializers.ModelSerializer):
    AREA_ULTIMO_CURSO_CHOICES = [("B", "Biológicas"), ("E", "Exatas"), ("H", "Humanas")]

    ESTADO_CIVIL_CHOICES = [
        ("S", "Solteiro(a)"),
        ("C", "Casado(a)"),
        ("D", "Divorciado(a)"),
        ("V", "Viúvo(a)"),
        ("U", "União Estável"),
    ]

    SEXO_CHOICES = [("M", "Masculino"), ("F", "Feminino")]

    TIPO_DOCUMENTO_CHOICES = [("RG", "RG"), ("CNH", "CNH")]

    area_ultimo_curso_superior = serializers.SerializerMethodField()
    estado_civil = serializers.SerializerMethodField()
    sexo = serializers.SerializerMethodField()
    tipo_documento = serializers.SerializerMethodField()
    fi_funcao_bolsista = FiFuncaoBolsistaGetSerializer(read_only=True)
    cm_municipio = CmMunicipioIdSerializer(read_only=True)

    class Meta:
        model = FiPessoaFicha
        # Como está buscando os dados da última ficha, obviamente dados
        # que serão substituídos serão descartados
        exclude = [
            "id",
            # Pessoa e edital estão na sessão
            "cm_pessoa",
            "ed_edital",
            # CadastroFiPessoaFichaAPIView.get substitui
            # pela associação em models.FiEditalFuncaoOferta
            "ac_curso_oferta",
            # Não precisa trazer as datas de vínculo antigo
            "data_inicio_vinculacao",
            "data_fim_vinculacao",
        ]

    def get_area_ultimo_curso_superior(self, obj) -> str:
        return dict(self.AREA_ULTIMO_CURSO_CHOICES).get(
            obj.area_ultimo_curso_superior, obj.area_ultimo_curso_superior
        )

    def get_estado_civil(self, obj) -> str:
        return dict(self.ESTADO_CIVIL_CHOICES).get(obj.estado_civil, obj.estado_civil)

    def get_sexo(self, obj) -> str:
        return dict(self.SEXO_CHOICES).get(obj.sexo, obj.sexo)

    def get_tipo_documento(self, obj) -> str:
        return dict(self.TIPO_DOCUMENTO_CHOICES).get(
            obj.tipo_documento, obj.tipo_documento
        )


class FiPessoaFichaPostSerializer(serializers.ModelSerializer):
    AREA_ULTIMO_CURSO_CHOICES = {"Biológicas": "B", "Exatas": "E", "Humanas": "H"}

    ESTADO_CIVIL_CHOICES = {
        "Solteiro(a)": "S",
        "Casado(a)": "C",
        "Divorciado(a)": "D",
        "Viúvo(a)": "V",
        "União Estável": "U",
    }

    SEXO_CHOICES = {"Masculino": "M", "Feminino": "F"}

    TIPO_DOCUMENTO_CHOICES = {"RG": "RG", "CNH": "CNH"}

    area_ultimo_curso_superior = serializers.CharField()
    estado_civil = serializers.CharField()
    sexo = serializers.CharField()
    tipo_documento = serializers.CharField()
    cm_municipio = serializers.PrimaryKeyRelatedField(
        queryset=CmMunicipio.objects.all(), required=False, allow_null=True
    )
    fi_funcao_bolsista = serializers.PrimaryKeyRelatedField(
        queryset=FiFuncaoBolsista.objects.all()
    )
    ac_curso_oferta = serializers.PrimaryKeyRelatedField(
        queryset=AcCursoOferta.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )

    class Meta:
        model = FiPessoaFicha
        exclude = [
            # Ja tem a validacao (que tem a pessoa e o edital) na sessao
            "cm_pessoa",
            "ed_edital",
            # Financeiro deveria preencher o inicio e fim efetivos da bolsa
            "data_inicio_vinculacao",
            "data_fim_vinculacao",
        ]

    def validate_area_ultimo_curso_superior(self, value):
        return self.AREA_ULTIMO_CURSO_CHOICES.get(value, value)

    def validate_estado_civil(self, value):
        return self.ESTADO_CIVIL_CHOICES.get(value, value)

    def validate_sexo(self, value):
        return self.SEXO_CHOICES.get(value, value)

    def validate_tipo_documento(self, value):
        return self.TIPO_DOCUMENTO_CHOICES.get(value, value)

    def validate_nome_mae(self, value):
        if not value:
            raise serializers.ValidationError(ERRO_NOME_MAE_OBRIGATORIO)

        nome_mae = maiusculas_nomes(value)

        if not regex.match(r"^.{2,15} .{2,}$", nome_mae):
            raise serializers.ValidationError(ERRO_NOME_MAE_INVALIDO)

        return nome_mae

    def validate_nome_pai(self, value):
        if not value:
            return None

        nome_pai = maiusculas_nomes(value)

        if not regex.match(r"^.{2,15} .{2,}$", nome_pai):
            raise serializers.ValidationError(ERRO_NOME_PAI_INVALIDO)

        return nome_pai

    def validate_nome_conjuge(self, value):
        if not value:
            return None

        nome_conjuge = maiusculas_nomes(value)

        if not regex.match(r"^.{2,15} .{2,}$", nome_conjuge):
            raise serializers.ValidationError(ERRO_NOME_CONJUGE_INVALIDO)

        return nome_conjuge

    def validate(self, data):
        ed_pessoa_vaga_validacao = self.context.get("ed_pessoa_vaga_validacao")
        ed_edital = ed_pessoa_vaga_validacao.ed_vaga.ed_edital

        fi_funcao_bolsista = data.get("fi_funcao_bolsista")
        ac_curso_oferta = data.get("ac_curso_oferta")

        # Use filter + first (banco do legado pode ter zuada)
        fi_edital_funcao_oferta = (
            FiEditalFuncaoOferta.objects.filter(
                ed_edital=ed_edital,
                fi_funcao_bolsista=fi_funcao_bolsista,
                ac_curso_oferta=ac_curso_oferta,
            )
            .order_by("-id")
            .first()
        )
        if not fi_edital_funcao_oferta:
            raise serializers.ValidationError(
                {"detail": ERRO_GET_FI_EDITAL_FUNCAO_OFERTA}
            )

        self._fi_edital_funcao_oferta = fi_edital_funcao_oferta
        return data

    @transaction.atomic
    def create(self, validated_data):
        # 1) Remove campos que serão forçados manualmente
        validated_data.pop("fi_funcao_bolsista", None)
        validated_data.pop("ac_curso_oferta", None)

        # 2) Insere valores consistentes
        validated_data["fi_funcao_bolsista"] = (
            self._fi_edital_funcao_oferta.fi_funcao_bolsista
        )
        validated_data["ac_curso_oferta"] = (
            self._fi_edital_funcao_oferta.ac_curso_oferta
        )

        # ⚡ Definir cm_pessoa antes da gambiarra
        cm_pessoa = self.context["ed_pessoa_vaga_validacao"].cm_pessoa
        ed_edital = self.context["ed_pessoa_vaga_validacao"].ed_vaga.ed_edital

        # Gambiarra edital 40: pessoa 180 sempre função 60
        if cm_pessoa.id == 180:
            validated_data["fi_funcao_bolsista"] = FiFuncaoBolsista.objects.get(id=60)

        # 3) Se solteiro/divorciado → zera cônjuge
        if validated_data.get("estado_civil") in ["S", "D"]:
            validated_data["nome_conjuge"] = None

        cm_pessoa = self.context["ed_pessoa_vaga_validacao"].cm_pessoa
        ed_edital = self.context["ed_pessoa_vaga_validacao"].ed_vaga.ed_edital

        # 4) Procura ficha existente para a mesma pessoa + edital + função/oferta
        ficha_existente = FiPessoaFicha.objects.filter(
            cm_pessoa=cm_pessoa,
            ed_edital=ed_edital,
            fi_funcao_bolsista=validated_data["fi_funcao_bolsista"],
            ac_curso_oferta=validated_data["ac_curso_oferta"],
        ).last()

        if ficha_existente:
            # Atualiza os campos que vieram do formulário
            for field, value in validated_data.items():
                setattr(ficha_existente, field, value)
            ficha_existente.save()
            return ficha_existente

        # 5) Se não existe, cria
        return super().create(validated_data)


## BLOCO: documentação OpenAPI
class CadastroEnderecoTelefoneBancoRequestSerializer(serializers.Serializer):
    endereco = CmPessoaEnderecoPostSerializer()
    telefones = CmPessoaTelefonePostSerializer(many=True)
    banco = CmPessoaBancoPostSerializer()
