from typing import Optional

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from cead.models import (
    CmPessoa,
    EdEdital,
    EdEditalPessoa,
    EdPessoaVagaCampoCheckboxPontuacao,
    EdPessoaVagaCampoCheckboxUpload,
    EdPessoaVagaCampoComboboxPontuacao,
    EdPessoaVagaCampoComboboxUpload,
    EdPessoaVagaCampoDateboxPontuacao,
    EdPessoaVagaCampoDateboxUpload,
    EdPessoaVagaInscricao,
    EdPessoaVagaJustificativa,
    EdPessoaVagaValidacao,
    EdPessoaVagaValidacaoIndeferimento,
    EdVaga,
)
from .messages import (
    ERRO_EDITAL_FORA_PRAZO_VALIDACAO,
    ERRO_GET_PESSOA,
    ERRO_GET_PESSOAVAGAINSCRICAO,
    ERRO_PONTUACAO_INVALIDA_DOCUMENTO,
    ERRO_PONTUACAO_INVALIDA_FRASE_INCOMPLETA,
    ERRO_POST_FORMATO_ID_INVALIDO,
    ERRO_POST_TIPO_DOCUMENTO_INVALIDO,
)
from .utils import calcular_maximo_de_pontos


## BLOCO: emissão de mensagem para candidato aprovado
class ListarEditaisEmissoresMensagemFichaSerializer(serializers.ModelSerializer):
    edital_str = serializers.SerializerMethodField()

    class Meta:
        model = EdEdital
        fields = [
            "id",
            "edital_str",
            "data_fim_validacao",
            "data_validade",
        ]

    def get_edital_str(self, obj):
        return str(obj)


class ListarVagasEmissoresMensagemFichaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdVaga
        fields = ["id", "descricao", "quantidade"]

    # Retorna so depois do fim da validacao e antes da data de validade, por seguranca
    def to_representation(self, instance):
        agora = timezone.now()

        edital = instance.ed_edital
        if not (edital.data_fim_validacao <= agora <= edital.data_validade):
            return None
        return super().to_representation(instance)


class EmitirMensagemFichaVagaSerializer(serializers.ModelSerializer):
    pessoa_id = serializers.IntegerField(source="cm_pessoa.id")
    pessoa_nome = serializers.CharField(source="cm_pessoa.nome")
    pessoa_email = serializers.CharField(source="cm_pessoa.email")
    pontuacao = serializers.FloatField()
    codigo = serializers.SerializerMethodField()

    class Meta:
        model = EdPessoaVagaValidacao
        fields = [
            "pessoa_id",
            "pessoa_nome",
            "pessoa_email",
            "pontuacao",
            "codigo",
        ]

    def get_codigo(self, obj) -> str:
        return obj.codigo


## BLOCO: validação do candidato
class ListarEditaisValidacaoSerializer(serializers.ModelSerializer):
    edital_str = serializers.SerializerMethodField()

    class Meta:
        model = EdEdital
        fields = [
            "id",
            "edital_str",
            "data_inicio_validacao",
            "data_fim_validacao",
            "data_validade",
        ]

    def get_edital_str(self, obj):
        return str(obj)


class ListarVagasValidacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdVaga
        fields = ["id", "descricao", "quantidade"]

    # Retorna so se tiver em epoca de validacao, por seguranca
    def to_representation(self, instance):
        agora = timezone.now()

        edital = instance.ed_edital
        if not (
            edital.data_inicio_validacao <= agora <= edital.data_fim_validacao
            and edital.data_validade >= agora
        ):
            return None
        return super().to_representation(instance)


class VerificaValidacaoSerializer(serializers.ModelSerializer):
    nome_responsavel_validacao = serializers.SerializerMethodField()
    data = serializers.SerializerMethodField()

    class Meta:
        model = EdPessoaVagaValidacao
        fields = ["nome_responsavel_validacao", "pontuacao", "data"]

    def get_nome_responsavel_validacao(self, obj) -> str:
        return (
            obj.cm_pessoa_responsavel_validacao.nome
            if obj.cm_pessoa_responsavel_validacao
            else None
        )

    def get_data(self, obj) -> Optional[str]:
        if obj.data:
            data_local = timezone.localtime(obj.data)
            return data_local.strftime("%d/%m/%Y às %H:%M:%S")
        return None


class ValidarVagaGetSerializer(serializers.ModelSerializer):
    maximo_de_pontos = serializers.SerializerMethodField()

    class Meta:
        model = EdVaga
        fields = ["id", "descricao", "maximo_de_pontos"]

    def get_maximo_de_pontos(self, obj) -> float:
        return calcular_maximo_de_pontos(obj)

    # Retorna so se tiver em epoca de validacao, por seguranca
    def to_representation(self, instance):
        agora = timezone.now()

        edital = instance.ed_edital
        if not (
            edital.data_inicio_validacao <= agora <= edital.data_fim_validacao
            and edital.data_validade >= agora
        ):
            raise NotFound(ERRO_EDITAL_FORA_PRAZO_VALIDACAO)
        return super().to_representation(instance)


class ValidarVagaPostSerializer(serializers.Serializer):
    inscrito_id = serializers.IntegerField()
    justificativa = serializers.CharField(allow_blank=True, required=False)
    arquivo_valido = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    pontuacoes_documentos = serializers.DictField(
        child=serializers.FloatField(), required=False
    )
    indeferido = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        agora = timezone.now()
        vaga = self.context["vaga"]
        edital = vaga.ed_edital

        # Verifica se o edital está no período de validação
        if not (
            edital.data_inicio_validacao <= agora <= edital.data_fim_validacao
            and edital.data_validade >= agora
        ):
            raise serializers.ValidationError(
                {"non_field_errors": [ERRO_EDITAL_FORA_PRAZO_VALIDACAO]}
            )

        # Verifica se a inscrição existe
        try:
            data["inscricao"] = EdPessoaVagaInscricao.objects.get(
                cm_pessoa=data["inscrito_id"], ed_vaga=vaga
            )
        except EdPessoaVagaInscricao.DoesNotExist:
            raise serializers.ValidationError(
                {"inscrito_id": [ERRO_GET_PESSOAVAGAINSCRICAO]}
            )

        # Valida formato dos IDs
        for full_id in data.get("arquivo_valido", []):
            if "-" not in full_id:
                raise serializers.ValidationError(
                    {"arquivo_valido": f"{ERRO_POST_FORMATO_ID_INVALIDO}: {full_id}"}
                )

        # Valida pontuações individuais dos documentos
        pontuacoes_documentos = data.get("pontuacoes_documentos", {})
        if pontuacoes_documentos:
            # Dicionários para separar IDs por tipo
            checkbox_ids = []
            combobox_ids = []
            datebox_ids = []

            for full_id in pontuacoes_documentos.keys():
                try:
                    tipo, id_str = full_id.split("-")
                    id = int(id_str)

                    if tipo == "checkbox":
                        checkbox_ids.append(id)
                    elif tipo == "combobox":
                        combobox_ids.append(id)
                    elif tipo == "datebox":
                        datebox_ids.append(id)
                    else:
                        raise serializers.ValidationError(
                            {
                                "pontuacoes_documentos": f"{ERRO_POST_TIPO_DOCUMENTO_INVALIDO}: {tipo}"
                            }
                        )
                except ValueError:
                    raise serializers.ValidationError(
                        {
                            "pontuacoes_documentos": f"{ERRO_POST_FORMATO_ID_INVALIDO}: {full_id}"
                        }
                    )

            # Valida pontuações - checkbox
            if checkbox_ids:
                checkbox_uploads = EdPessoaVagaCampoCheckboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_checkbox__cm_pessoa=data["inscrito_id"],
                    ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga=vaga,
                    id__in=checkbox_ids,
                ).select_related(
                    "ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox"
                )

                for upload in checkbox_uploads:
                    full_id = f"checkbox-{upload.id}"
                    if full_id in pontuacoes_documentos:
                        pontuacao_informada = pontuacoes_documentos[full_id]
                        pontuacao_maxima = (
                            upload.ed_pessoa_vaga_campo_checkbox.ed_vaga_campo_checkbox.pontuacao
                            or 0
                        )
                        if (
                            pontuacao_informada < 0
                            or pontuacao_informada > pontuacao_maxima
                        ):
                            raise serializers.ValidationError(
                                {
                                    "pontuacoes_documentos": [
                                        f"{ERRO_PONTUACAO_INVALIDA_DOCUMENTO} {full_id}. "
                                        f"{ERRO_PONTUACAO_INVALIDA_FRASE_INCOMPLETA} {pontuacao_maxima}"
                                    ]
                                }
                            )

            # Valida pontuações - combobox
            if combobox_ids:
                combobox_uploads = EdPessoaVagaCampoComboboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_combobox__cm_pessoa=data["inscrito_id"],
                    ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga=vaga,
                    id__in=combobox_ids,
                ).select_related(
                    "ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox"
                )

                for upload in combobox_uploads:
                    full_id = f"combobox-{upload.id}"
                    if full_id in pontuacoes_documentos:
                        pontuacao_informada = pontuacoes_documentos[full_id]
                        pontuacao_maxima = (
                            upload.ed_pessoa_vaga_campo_combobox.ed_vaga_campo_combobox.pontuacao
                            or 0
                        )
                        if (
                            pontuacao_informada < 0
                            or pontuacao_informada > pontuacao_maxima
                        ):
                            raise serializers.ValidationError(
                                {
                                    "pontuacoes_documentos": [
                                        f"{ERRO_PONTUACAO_INVALIDA_DOCUMENTO} {full_id}. "
                                        f"{ERRO_PONTUACAO_INVALIDA_FRASE_INCOMPLETA} {pontuacao_maxima}"
                                    ]
                                }
                            )

            # Valida pontuações - datebox
            if datebox_ids:
                datebox_uploads = EdPessoaVagaCampoDateboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_datebox__cm_pessoa=data["inscrito_id"],
                    ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga=vaga,
                    id__in=datebox_ids,
                ).select_related("ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox")

                for upload in datebox_uploads:
                    full_id = f"datebox-{upload.id}"
                    if full_id in pontuacoes_documentos:
                        pontuacao_informada = pontuacoes_documentos[full_id]
                        pontuacao_maxima = (
                            upload.ed_pessoa_vaga_campo_datebox.ed_vaga_campo_datebox.pontuacao_maxima
                            or 0
                        )
                        if (
                            pontuacao_informada < 0
                            or pontuacao_informada > pontuacao_maxima
                        ):
                            raise serializers.ValidationError(
                                {
                                    "pontuacoes_documentos": [
                                        f"{ERRO_PONTUACAO_INVALIDA_DOCUMENTO} {full_id}. "
                                        f"{ERRO_PONTUACAO_INVALIDA_FRASE_INCOMPLETA} {pontuacao_maxima}"
                                    ]
                                }
                            )

        maximo = calcular_maximo_de_pontos(vaga)

        # Calcula a pontuação total com base no que foi enviado no POST
        data["pontuacao"] = round(
            sum(float(p) for p in pontuacoes_documentos.values()), 2
        )

        # Valida se pontuação total é condizente
        if data["pontuacao"] < 0 or data["pontuacao"] > maximo:
            raise serializers.ValidationError(
                {"pontuacao": [f"{ERRO_PONTUACAO_INVALIDA_FRASE_INCOMPLETA} {maximo}."]}
            )

        # Busca a pessoa responsável pela validação
        try:
            data["responsavel"] = CmPessoa.objects.get(
                cpf=self.context["request"].user.username
            )
        except CmPessoa.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": [ERRO_GET_PESSOA]})

        return data

    def _salvar_pontuacoes_individuais(self, inscricao, pontuacoes_documentos):
        if not pontuacoes_documentos:
            return

        for full_id, pontuacao in pontuacoes_documentos.items():
            try:
                tipo, id_str = full_id.split("-")
                id = int(id_str)
                pontuacao = None if float(pontuacao) == 0.0 else pontuacao

                if tipo == "checkbox":
                    checkbox_upload = EdPessoaVagaCampoCheckboxUpload.objects.filter(
                        id=id,
                        ed_pessoa_vaga_campo_checkbox__cm_pessoa=inscricao.cm_pessoa,
                        ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga=inscricao.ed_vaga,
                    ).first()
                    if checkbox_upload:
                        EdPessoaVagaCampoCheckboxPontuacao.objects.update_or_create(
                            ed_pessoa_vaga_campo_checkbox=checkbox_upload.ed_pessoa_vaga_campo_checkbox,
                            defaults={"pontuacao": pontuacao},
                        )

                elif tipo == "combobox":
                    combobox_upload = EdPessoaVagaCampoComboboxUpload.objects.filter(
                        id=id,
                        ed_pessoa_vaga_campo_combobox__cm_pessoa=inscricao.cm_pessoa,
                        ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga=inscricao.ed_vaga,
                    ).first()
                    if combobox_upload:
                        EdPessoaVagaCampoComboboxPontuacao.objects.update_or_create(
                            ed_pessoa_vaga_campo_combobox=combobox_upload.ed_pessoa_vaga_campo_combobox,
                            defaults={"pontuacao": pontuacao},
                        )

                elif tipo == "datebox":
                    datebox_upload = EdPessoaVagaCampoDateboxUpload.objects.filter(
                        id=id,
                        ed_pessoa_vaga_campo_datebox__cm_pessoa=inscricao.cm_pessoa,
                        ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga=inscricao.ed_vaga,
                    ).first()
                    if datebox_upload:
                        EdPessoaVagaCampoDateboxPontuacao.objects.update_or_create(
                            ed_pessoa_vaga_campo_datebox=datebox_upload.ed_pessoa_vaga_campo_datebox,
                            defaults={"pontuacao": pontuacao},
                        )

            except (ValueError, TypeError):
                continue

    def save(self):
        inscricao = self.validated_data["inscricao"]
        pontuacao = self.validated_data["pontuacao"]
        justificativa = self.validated_data.get("justificativa", "")
        cm_pessoa_responsavel = self.validated_data["responsavel"]
        pontuacoes_documentos = self.validated_data.get("pontuacoes_documentos", {})
        arquivos_validos = self.validated_data.get("arquivo_valido", [])
        indeferido = self.validated_data.get("indeferido", False)

        # Dicionários para armazenar IDs separados por tipo
        checkbox_ids = []
        combobox_ids = []
        datebox_ids = []

        # Separar os IDs por tipo
        for full_id in arquivos_validos:
            tipo, id = full_id.split("-")
            if tipo == "checkbox":
                checkbox_ids.append(int(id))
            elif tipo == "combobox":
                combobox_ids.append(int(id))
            elif tipo == "datebox":
                datebox_ids.append(int(id))

        # Atualizar uploads marcados como válidos
        EdPessoaVagaCampoCheckboxUpload.objects.filter(
            id__in=checkbox_ids,
            ed_pessoa_vaga_campo_checkbox__cm_pessoa=inscricao.cm_pessoa,
            ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga=inscricao.ed_vaga,
        ).update(validado=True)

        EdPessoaVagaCampoComboboxUpload.objects.filter(
            id__in=combobox_ids,
            ed_pessoa_vaga_campo_combobox__cm_pessoa=inscricao.cm_pessoa,
            ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga=inscricao.ed_vaga,
        ).update(validado=True)

        EdPessoaVagaCampoDateboxUpload.objects.filter(
            id__in=datebox_ids,
            ed_pessoa_vaga_campo_datebox__cm_pessoa=inscricao.cm_pessoa,
            ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga=inscricao.ed_vaga,
        ).update(validado=True)

        self._salvar_pontuacoes_individuais(inscricao, pontuacoes_documentos)

        # Lógica de validação e indeferimento: todo indeferido e zerado recebe nota None
        if indeferido or pontuacao == 0:
            pontuacao_valida = None
        else:
            pontuacao_valida = pontuacao

        # Atualiza ou cria a validação
        validacao, created = EdPessoaVagaValidacao.objects.update_or_create(
            cm_pessoa=inscricao.cm_pessoa,
            ed_vaga=inscricao.ed_vaga,
            defaults={
                "cm_pessoa_responsavel_validacao": cm_pessoa_responsavel,
                "pontuacao": pontuacao_valida,
            },
        )

        # Atualiza ou remove indeferimento
        if indeferido:
            EdPessoaVagaValidacaoIndeferimento.objects.update_or_create(
                ed_pessoa_vaga_validacao=validacao
            )
        else:
            EdPessoaVagaValidacaoIndeferimento.objects.filter(
                ed_pessoa_vaga_validacao=validacao
            ).delete()

        # Salva ou remove justificativa
        if justificativa and justificativa.strip():
            EdPessoaVagaJustificativa.objects.update_or_create(
                cm_pessoa=inscricao.cm_pessoa,
                ed_vaga=inscricao.ed_vaga,
                defaults={
                    "cm_pessoa_responsavel_justificativa": cm_pessoa_responsavel,
                    "justificativa": justificativa,
                },
            )
        else:
            EdPessoaVagaJustificativa.objects.filter(
                cm_pessoa=inscricao.cm_pessoa, ed_vaga=inscricao.ed_vaga
            ).delete()

        return {
            "inscrito_id": inscricao.cm_pessoa.id,
            "pontuacao": pontuacao,
            "justificativa": justificativa,
            "arquivo_valido": arquivos_validos,
            "pontuacoes_documentos": pontuacoes_documentos,
            "indeferido": indeferido,
        }


## BLOCO: relatórios
class ListarEditaisRelatorioSerializer(serializers.ModelSerializer):
    edital_str = serializers.SerializerMethodField()

    class Meta:
        model = EdEdital
        fields = ["id", "edital_str", "data_validade"]

    def get_edital_str(self, obj):
        return str(obj)


class ListarVagasRelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdVaga
        fields = ["id", "descricao", "quantidade"]


## BLOCO: justificativas
class ListarEditalJustificativaSerializer(serializers.ModelSerializer):
    edital_str = serializers.SerializerMethodField()

    class Meta:
        model = EdEdital
        fields = ["id", "edital_str"]

    def get_edital_str(self, obj):
        return str(obj)


class ListarEditaisAssociacaoEditalPessoaSerializer(serializers.ModelSerializer):
    edital_str = serializers.SerializerMethodField()

    class Meta:
        model = EdEdital
        fields = [
            "id",
            "edital_str",
            "data_fim_validacao",
            "data_validade",
        ]

    def get_edital_str(self, obj):
        return str(obj)


## BLOCO: associação edital - pessoa
# A pessoa tem que estar cadastrada com login = cpf no Django
class CmPessoaUsuarioExisteSerializer(serializers.ModelSerializer):
    usuario_existe = serializers.SerializerMethodField()

    class Meta:
        model = CmPessoa
        fields = ("id", "nome", "cpf", "usuario_existe")

    def get_usuario_existe(self, obj) -> bool:
        return User.objects.filter(username=obj.cpf).exists()


# Utilizado em AssociarEditalPessoaAPIView e AssociarEditalPessoaRetrieveDestroyAPIView
class EdGetEditalPessoaSerializer(serializers.ModelSerializer):
    cm_pessoa = CmPessoaUsuarioExisteSerializer(read_only=True)

    class Meta:
        model = EdEditalPessoa
        fields = ("id", "cm_pessoa")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not rep.get("cm_pessoa", {}).get("usuario_existe", False):
            return None

        pessoa_data = rep["cm_pessoa"]
        pessoa_data.pop("usuario_existe", None)
        return {"id": rep["id"], "cm_pessoa": pessoa_data}


class EdGetEditalPessoaMixinSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdEditalPessoa
        fields = "__all__"


class EdPostEditalPessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EdEditalPessoa
        fields = "__all__"


## BLOCO: extra - para retornar o id Django do CPF do sistema
class UsuarioPorCpfSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]
