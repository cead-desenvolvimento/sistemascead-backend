import unicodedata

import regex
from email_validator import EmailNotValidError, validate_email
from django.utils import timezone
from rest_framework import serializers

from cead.models import (
    CmFormacao,
    CmPessoa,
    EdCota,
    EdEdital,
    EdPessoaFormacao,
    EdPessoaVagaCampoCheckbox,
    EdPessoaVagaCampoCheckboxUpload,
    EdPessoaVagaCampoCombobox,
    EdPessoaVagaCampoComboboxUpload,
    EdPessoaVagaCampoDatebox,
    EdPessoaVagaCampoDateboxUpload,
    EdPessoaVagaInscricao,
    EdVaga,
    EdVagaCampoCheckbox,
    EdVagaCampoCombobox,
    EdVagaCampoDatebox,
)
from cead.utils import maiusculas_nomes

from .messages import (
    ERRO_EMAIL_INVALIDO,
    ERRO_EMAIL_JA_REGISTRADO,
    ERRO_NOME_INVALIDO,
    ERRO_NOME_OBRIGATORIO,
)


class GetVagasSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdVaga
        fields = ["id", "descricao", "quantidade"]


class PostVagasSerializer(serializers.Serializer):
    vaga_id = serializers.IntegerField()


class GetEditaisSerializer(serializers.ModelSerializer):
    vagas = GetVagasSerializer(many=True, read_only=True)

    class Meta:
        model = EdEdital
        fields = ["id", "numero", "ano", "descricao", "vagas"]

    # # Retorna so o que estao em fase de inscricao
    # def to_representation(self, instance):
    #     if (instance.data_inicio_inscricao <= timezone.now() <= instance.data_fim_inscricao):
    #         return super().to_representation(instance)
    #     return None


class CmPessoaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CmPessoa
        fields = ["cpf", "nome", "email"]

    def validate_nome(self, value):
        nome = unicodedata.normalize("NFC", value)
        nome = regex.sub(r"[^\w\s\'´-]", " ", nome).lower().strip().replace(" +", " ")

        if not nome:
            raise serializers.ValidationError(ERRO_NOME_OBRIGATORIO)
        if not regex.match(r"^.{2,15} .{2,}$", nome):
            raise serializers.ValidationError(ERRO_NOME_INVALIDO)
        return maiusculas_nomes(nome)

    def validate_email(self, value):
        try:
            valid = validate_email(value, check_deliverability=False)
            email = valid.email.lower()
        except EmailNotValidError as e:
            raise serializers.ValidationError(ERRO_EMAIL_INVALIDO + " " + str(e))

        if CmPessoa.objects.filter(email=email).exists():
            raise serializers.ValidationError(ERRO_EMAIL_JA_REGISTRADO)

        return email


class GetPessoaFormacaoSerializer(serializers.ModelSerializer):
    titulacao = serializers.CharField(
        source="cm_formacao.cm_titulacao.nome", read_only=True
    )
    formacao = serializers.CharField(source="cm_formacao.nome", read_only=True)

    class Meta:
        model = EdPessoaFormacao
        fields = ["id", "titulacao", "formacao", "inicio", "fim"]


class PostPessoaFormacaoSerializer(serializers.Serializer):
    ed_pessoa_formacao_id = serializers.IntegerField()
    inicio = serializers.DateField()
    fim = serializers.DateField(required=False, allow_null=True)


class GetFormacaoSerializer(serializers.ModelSerializer):
    titulacao_nome = serializers.SerializerMethodField()

    class Meta:
        model = CmFormacao
        fields = ["id", "titulacao_nome"]

    def get_titulacao_nome(self, obj):
        return f"{obj.nome} ({obj.cm_titulacao.nome})"


class CheckboxSerializer(serializers.ModelSerializer):
    descricao = serializers.CharField(source="ed_campo.descricao")

    class Meta:
        model = EdVagaCampoCheckbox
        fields = ["id", "descricao", "pontuacao", "obrigatorio"]


class ComboboxSerializer(serializers.ModelSerializer):
    descricao = serializers.CharField(source="ed_campo.descricao")

    class Meta:
        model = EdVagaCampoCombobox
        fields = ["id", "descricao", "ordem", "pontuacao"]


class DateboxSerializer(serializers.ModelSerializer):
    descricao = serializers.CharField(source="ed_campo.descricao")

    class Meta:
        model = EdVagaCampoDatebox
        fields = [
            "id",
            "descricao",
            "fracao_pontuacao",
            "multiplicador_fracao_pontuacao",
            "pontuacao_maxima",
        ]


class CheckboxPessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdPessoaVagaCampoCheckbox
        fields = ["ed_vaga_campo_checkbox_id"]


class ComboboxPessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdPessoaVagaCampoCombobox
        fields = ["ed_vaga_campo_combobox_id"]


class DateboxPessoaSerializer(serializers.ModelSerializer):
    periodos = serializers.SerializerMethodField()

    class Meta:
        model = EdPessoaVagaCampoDatebox
        fields = ["ed_vaga_campo_datebox_id", "periodos"]

    def get_periodos(self, obj):
        return [
            {"inicio": p.inicio, "fim": p.fim} for p in obj.periodos.order_by("inicio")
        ]


class UploadArquivoCheckboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdPessoaVagaCampoCheckboxUpload
        fields = ["ed_pessoa_vaga_campo_checkbox_id", "caminho_arquivo", "validado"]


class UploadArquivoComboboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdPessoaVagaCampoComboboxUpload
        fields = ["ed_pessoa_vaga_campo_combobox_id", "caminho_arquivo", "validado"]


class UploadArquivoDateboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdPessoaVagaCampoDateboxUpload
        fields = ["ed_pessoa_vaga_campo_datebox_id", "caminho_arquivo", "validado"]


class CotaDisponivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdCota
        fields = ["id", "cota"]


class CotaMarcadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdCota
        fields = ["id", "cota"]


# Agrega os dois serializers para enviar na resposta dessa forma:
# {
#   "cotas_disponiveis": [
#     {"id": 1, "cota": "Piloto de helicóptero"},
#     {"id": 2, "cota": "Jovem dinâmico"},
#   ],
#   "cota_marcada": {"id": 2, "cota": "Jovem dinâmico"}
# }
class PessoaVagaCotaSerializer(serializers.Serializer):
    cotas_disponiveis = CotaDisponivelSerializer(many=True)
    cota_marcada = CotaMarcadaSerializer(allow_null=True)


class FinalizarInscricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdPessoaVagaInscricao
        fields = ["cm_pessoa_id", "ed_vaga_id", "pontuacao", "data"]

    def create(self, validated_data):
        return EdPessoaVagaInscricao.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.pontuacao = validated_data.get("pontuacao", instance.pontuacao)
        instance.data = timezone.now()
        instance.save()
        return instance


# Serializers para documentação
class PessoaVagaCampoRequestSerializer(serializers.Serializer):
    checkbox_da_vaga = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs dos checkboxes selecionados",
    )
    combobox_da_vaga = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs dos comboboxes selecionados",
    )
    datebox_da_vaga = serializers.DictField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        help_text="Dicionário com IDs dos dateboxes e suas datas (inicio/fim)",
    )


class PessoaVagaCampoResponseSerializer(serializers.Serializer):
    checkboxes = serializers.ListField(child=serializers.DictField())
    comboboxes = serializers.ListField(child=serializers.DictField())
    dateboxes = serializers.ListField(child=serializers.DictField())
