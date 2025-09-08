# Vai fazer 'confirmacao' de vaga?

import os
import textwrap
from pathlib import Path

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import F, FloatField, Max, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.utils import timezone

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cead.messages import (
    EMAIL_ASSINATURA,
    EMAIL_DUVIDAS_PARA_O_SUPORTE,
    EMAIL_ENDERECO_NAO_MONITORADO,
    ERRO_GET_ARQUIVO,
    ERRO_GET_EDITAL,
    ERRO_GET_PESSOA_VAGA_VALIDACAO,
    ERRO_MULTIPLOS_EDITAIS,
    ERRO_GET_VAGA,
    ERRO_GET_VAGAS,
    ERRO_SESSAO_INVALIDA,
    ERRO_VAGAID_NA_SESSAO,
    ERRO_VAGAIDHASH_NA_SESSAO,
    INFO_ENTRE_CONTATO_ACADEMICO,
    INFO_ENTRE_CONTATO_FINANCEIRO,
    INFO_ENTRE_CONTATO_SUPORTE,
)
from cead.models import (
    CmPessoa,
    EdEdital,
    EdEditalPessoa,
    EdPessoaVagaCampoCheckbox,
    EdPessoaVagaCampoCheckboxUpload,
    EdPessoaVagaCampoCombobox,
    EdPessoaVagaCampoComboboxUpload,
    EdPessoaVagaCampoDatebox,
    EdPessoaVagaCampoDateboxUpload,
    EdPessoaVagaConfirmacao,
    EdPessoaVagaCota,
    EdPessoaVagaInscricao,
    EdPessoaVagaJustificativa,
    EdPessoaVagaValidacao,
    EdVaga,
    EdVagaCampoCheckbox,
    EdVagaCampoCombobox,
    EdVagaCampoDatebox,
)
from cead.serializers import (
    CPFSerializer,
    CmPessoaIdNomeCpfSerializer,
    GetPessoaEmailSerializer,
)
from cead.settings import EMAIL_HOST_USER, RAIZ_ARQUIVOS_UPLOAD
from cead.utils import gerar_hash

from .api_docs import *
from .messages import *
from .permissions import (
    IsAssociadorEditalPessoa,
    IsEmissorMensagemCriacaoFicha,
    IsValidadorDeEditais,
    IsVisualizadordeRelatorioDeEditais,
    PodeAcessarEditalEspecifico,
)
from .renderers import CSVRenderer
from .serializers import (
    EdGetEditalPessoaSerializer,
    EdPostEditalPessoaSerializer,
    EmitirMensagemFichaVagaSerializer,
    ListarEditaisAssociacaoEditalPessoaSerializer,
    ListarEditaisEmissoresMensagemFichaSerializer,
    ListarEditaisRelatorioSerializer,
    ListarEditaisValidacaoSerializer,
    ListarEditalJustificativaSerializer,
    ListarVagasEmissoresMensagemFichaSerializer,
    ListarVagasRelatorioSerializer,
    ListarVagasValidacaoSerializer,
    RelatorioEditalSerializer,
    RelatorioVagaSerializer,
    UsuarioPorCpfSerializer,
    ValidarVagaGetSerializer,
    ValidarVagaPostSerializer,
    VerificaValidacaoSerializer,
)


def enviar_email_base(pessoa_vaga_validacao, request):
    codigo = pessoa_vaga_validacao.codigo
    ficha_url = request.build_absolute_uri(f"/ficha/index.html?codigo={codigo}")

    assunto = f"{EMAIL_BOLSA_ASSUNTO} - {pessoa_vaga_validacao.ed_vaga.ed_edital} - {pessoa_vaga_validacao.ed_vaga}"
    mensagem = textwrap.dedent(
        f"""
        {pessoa_vaga_validacao.cm_pessoa.nome},
        {EMAIL_BOLSA_CODIGO_GERADO}: {codigo}
        {EMAIL_BOLSA_ENDERECO_FICHA} {ficha_url}

        {EMAIL_ENDERECO_NAO_MONITORADO}
        {EMAIL_DUVIDAS_PARA_O_SUPORTE} {INFO_ENTRE_CONTATO_SUPORTE}
        {EMAIL_BOLSA_DUVIDAS_PARA_O_FINANCEIRO} {INFO_ENTRE_CONTATO_FINANCEIRO}

        {EMAIL_ASSINATURA}
    """
    ).strip()

    send_mail(
        assunto,
        mensagem,
        EMAIL_HOST_USER,
        [pessoa_vaga_validacao.cm_pessoa.email],
        fail_silently=True,  # Deixa os try-except de EnviarEmailAPIView e EnviarEmailsAPIView com a responsabilidade de mostrar erros
    )


@extend_schema(**DOCS_ENVIAR_EMAIL_APIVIEW)
class EnviarEmailAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmissorMensagemCriacaoFicha]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_id" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_id_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if request.session["vaga_id_hash"] != gerar_hash(request.session["vaga_id"]):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            pessoa_vaga_validacao = EdPessoaVagaValidacao.objects.get(
                cm_pessoa__email=kwargs["email"], ed_vaga=request.session["vaga_id"]
            )
        except EdPessoaVagaValidacao.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_PESSOA_VAGA_VALIDACAO})

        request.pessoa_vaga_validacao = pessoa_vaga_validacao

    def get(self, request, email):
        try:
            enviar_email_base(request.pessoa_vaga_validacao, request)
            return Response(
                {
                    "detail": f"{EMAIL_BOLSA_ENVIADO} {request.pessoa_vaga_validacao.cm_pessoa.nome}"
                },
                status=status.HTTP_200_OK,
            )
        except EdPessoaVagaValidacao.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_PESSOA_VAGA_VALIDACAO},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_ENVIO_EMAIL}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(**DOCS_ENVIAR_EMAILS_APIVIEW)
class EnviarEmailsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmissorMensagemCriacaoFicha]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_id" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_id_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if request.session["vaga_id_hash"] != gerar_hash(request.session["vaga_id"]):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            validados = EdPessoaVagaValidacao.objects.filter(
                ed_vaga=request.session["vaga_id"]
            ).order_by(F("pontuacao").desc(nulls_last=True))
        except EdPessoaVagaValidacao.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_PESSOAVAGAVALIDACOES})

        request.validados = validados

    def post(self, request):
        email_limite = request.data.get("enviar_ate")

        deve_enviar = True
        numero_emails_enviados = 0
        nome_ultima_pessoa_que_o_email_foi_enviado = ""
        erros = []

        try:
            for validado in request.validados:
                if deve_enviar:
                    if validado.cm_pessoa.email == email_limite:
                        deve_enviar = False
                    try:
                        enviar_email_base(validado, request)
                        numero_emails_enviados += 1
                        nome_ultima_pessoa_que_o_email_foi_enviado = (
                            validado.cm_pessoa.nome
                        )
                    except Exception as e:
                        erros.append(
                            f"{ERRO_ENVIO_EMAIL} {validado.cm_pessoa.nome}: {str(e)}"
                        )

            informacoes_envio = {
                "numero_emails_enviados": numero_emails_enviados,
                "nome_ultima_pessoa_que_o_email_foi_enviado": nome_ultima_pessoa_que_o_email_foi_enviado,
            }

            if numero_emails_enviados > 0:
                return Response(
                    {**informacoes_envio, "detail": EMAILS_BOLSA_ENVIADOS},
                    status=status.HTTP_200_OK,
                )
            if erros:
                informacoes_envio["erros"] = erros
                return Response(
                    {**informacoes_envio, "detail": EMAILS_BOLSA_ENVIADOS},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"detail": ERRO_ENVIO_EMAIL},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_ENVIO_EMAIL}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(**DOCS_LISTAR_EDITAIS_EMISSORES_MENSAGEM_FICHA_APIVIEW)
class ListarEditaisEmissoresMensagemFichaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmissorMensagemCriacaoFicha]

    def get(self, request):
        agora = timezone.now()

        # Filtro = editais depois da validacao e antes da validade
        if request.user.groups.filter(
            name__in=["Acadêmico - administradores", "Financeiro - administradores"]
        ).exists():
            editais = EdEdital.objects.filter(
                data_fim_validacao__lte=agora, data_validade__gte=agora
            ).order_by("-id")
        else:  # Busca apenas os editais que estão associados em ed_edital_pessoa
            try:
                pessoa = CmPessoa.objects.get(cpf=request.user.username)
            except CmPessoa.DoesNotExist:
                return Response(
                    {"detail": ERRO_GET_PESSOA}, status=status.HTTP_404_NOT_FOUND
                )

            editais = EdEdital.objects.filter(
                id__in=EdEditalPessoa.objects.filter(cm_pessoa=pessoa).values_list(
                    "ed_edital_id", flat=True
                ),
                data_fim_validacao__lte=agora,
                data_validade__gte=agora,
            ).order_by("-id")

        return Response(
            ListarEditaisEmissoresMensagemFichaSerializer(editais, many=True).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_LISTAR_EDITAIS_RELATORIOS_APIVIEW)
class ListarEditaisRelatoriosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioDeEditais]

    def get(self, request):
        if request.user.groups.filter(
            name__in=["Acadêmico - administradores", "Financeiro - administradores"]
        ).exists():
            editais = EdEdital.objects.all().order_by("-id")
        else:
            pessoa = CmPessoa.objects.get(cpf=request.user.username)
            if not pessoa:
                return Response(
                    {"detail": ERRO_GET_PESSOA}, status=status.HTTP_404_NOT_FOUND
                )

            editais = EdEdital.objects.filter(
                id__in=EdEditalPessoa.objects.filter(cm_pessoa=pessoa).values_list(
                    "ed_edital_id", flat=True
                )
            ).order_by("-id")

        return Response(
            ListarEditaisRelatorioSerializer(editais, many=True).data,
            status=status.HTTP_200_OK,
        )


class ListarEditaisValidacaoAPIView(APIView):
    serializer_class = ListarEditaisValidacaoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsValidadorDeEditais]

    @extend_schema(**DOCS_LISTAR_EDITAIS_VALIDACAO_APIVIEW)
    def get(self, request):
        agora = timezone.now()

        if request.user.groups.filter(name="Acadêmico - administradores").exists():
            editais = EdEdital.objects.filter(
                data_inicio_validacao__lte=agora,
                data_fim_validacao__gte=agora,
                data_validade__gte=agora,
            ).order_by("-id")
        else:
            editais = EdEdital.objects.filter(
                id__in=EdEditalPessoa.objects.filter(
                    cm_pessoa=CmPessoa.objects.get(cpf=request.user.username)
                ).values_list("ed_edital_id", flat=True),
                data_inicio_validacao__lte=agora,
                data_fim_validacao__gte=agora,
                data_validade__gte=agora,
            ).order_by("-id")

        return Response(ListarEditaisValidacaoSerializer(editais, many=True).data)


class ListarEditalJustificativaAPIView(GenericAPIView):
    serializer_class = ListarEditalJustificativaSerializer

    @extend_schema(**DOCS_LISTAR_EDITAL_JUSTIFICATIVA_APIVIEW)
    def get(self, request):
        try:
            editais = EdEdital.objects.filter(
                data_inicio_validacao__lt=timezone.now(),
                data_validade__gt=timezone.now(),
            ).order_by("-id")
            return Response(
                ListarEditalJustificativaSerializer(editais, many=True).data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_EDITAL}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(**DOCS_LISTAR_VAGAS_EMISSORES_MENSAGEM_FICHA_APIVIEW)
class ListarVagasEmissoresMensagemFichaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmissorMensagemCriacaoFicha]

    def get(self, request, ano, numero):
        try:
            vagas = EdVaga.objects.filter(
                ed_edital=EdEdital.objects.get(ano=ano, numero=numero)
            )
            return Response(
                ListarVagasEmissoresMensagemFichaSerializer(vagas, many=True).data
            )
        except EdEdital.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_EDITAL}, status=status.HTTP_404_NOT_FOUND
            )
        except EdEdital.MultipleObjectsReturned:
            return Response(
                {"detail": ERRO_MULTIPLOS_EDITAIS},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_VAGAS}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(**DOCS_LISTAR_VAGAS_RELATORIO_APIVIEW)
class ListarVagasRelatorioAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        IsVisualizadordeRelatorioDeEditais,
        PodeAcessarEditalEspecifico,
    ]

    def get(self, request, ano, numero):
        try:
            edital = EdEdital.objects.get(ano=ano, numero=numero)
            vagas = EdVaga.objects.filter(ed_edital=edital)
            return Response(
                ListarVagasRelatorioSerializer(vagas, many=True).data,
                status=status.HTTP_200_OK,
            )
        except EdEdital.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_EDITAL}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(**DOCS_LISTAR_VAGAS_VALIDACAO_APIVIEW)
class ListarVagasValidacaoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsValidadorDeEditais]

    def get(self, request, ano, numero):
        try:
            vagas = EdVaga.objects.filter(
                ed_edital=EdEdital.objects.get(ano=ano, numero=numero)
            )
            return Response(ListarVagasValidacaoSerializer(vagas, many=True).data)
        except EdEdital.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_EDITAL}, status=status.HTTP_404_NOT_FOUND
            )
        except EdEdital.MultipleObjectsReturned:
            return Response(
                {"detail": ERRO_MULTIPLOS_EDITAIS},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_VAGAS}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(**DOCS_VALIDAR_VAGA_APIVIEW)
class ValidarVagaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsValidadorDeEditais]

    def get(self, request, vaga_id):
        try:
            vaga = EdVaga.objects.get(id=vaga_id)
            agora = timezone.now()
            edital = vaga.ed_edital

            if not (
                edital.data_inicio_validacao <= agora <= edital.data_fim_validacao
                and edital.data_validade >= agora
            ):
                return Response(
                    {"detail": ERRO_EDITAL_FORA_PRAZO_VALIDACAO},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            vaga_data = ValidarVagaGetSerializer(vaga).data

            # Parâmetros de paginação
            page_size = request.query_params.get("page_size", 10)
            page = request.query_params.get("page", 1)

            try:
                page_size = int(page_size)
                page = int(page)
            except ValueError:
                page_size = 10
                page = 1

            page_size = min(page_size, 20)  # Até 20 por página
            offset = (page - 1) * page_size

            # Apenas id da inscricao, quem pega os dados de verdade -> self.get_inscritos
            # cm_pessoa ta ai apenas para ordenar pelo nome
            inscritos_da_pagina_atual = (
                EdPessoaVagaInscricao.objects.filter(ed_vaga=vaga)
                .select_related("cm_pessoa")
                .only("id", "cm_pessoa")
                .order_by("cm_pessoa__nome")[offset : offset + page_size]
            )

            total_count = EdPessoaVagaInscricao.objects.filter(ed_vaga=vaga).count()

            pagination_data = {
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
                "next": page + 1 if offset + page_size < total_count else None,
                "previous": page - 1 if page > 1 else None,
            }

            response_data = {
                **vaga_data,
                "inscritos": self.get_inscritos(
                    vaga, [insc.id for insc in inscritos_da_pagina_atual]
                ),
                "pagination": pagination_data,
            }

            return Response(response_data)

        except EdVaga.DoesNotExist:
            return Response({"detail": ERRO_GET_VAGA}, status=status.HTTP_404_NOT_FOUND)

    def get_inscritos(self, vaga, inscrito_ids):
        # 1. Buscar os inscritos paginados
        inscritos = (
            EdPessoaVagaInscricao.objects.filter(id__in=inscrito_ids)
            .select_related("cm_pessoa")
            .order_by("cm_pessoa__nome")
        )

        # Extrair pessoa_ids para usar nas consultas
        pessoa_ids = [inscrito.cm_pessoa.id for inscrito in inscritos]

        # 2. BUSCAR TODOS OS DADOS DE UMA VEZ

        # 2.1 Justificativas
        justificativas_dict = {
            j.cm_pessoa_id: j.justificativa
            for j in EdPessoaVagaJustificativa.objects.filter(
                cm_pessoa_id__in=pessoa_ids, ed_vaga=vaga
            )
        }

        # 2.2 Pontuações
        pontuacoes_dict = self.get_pontuacoes(vaga, pessoa_ids)

        # 2.3 Uploads
        uploads_pontuacoes_dict = self.get_uploads_pontuacoes(vaga, pessoa_ids)

        # 3. Montar resultado usando os dicionários
        return [
            {
                "cm_pessoa": {
                    "id": inscrito.cm_pessoa.id,
                    "nome": inscrito.cm_pessoa.nome,
                    "cpf": inscrito.cm_pessoa.cpf_com_pontos_e_traco(),
                },
                "justificativa": justificativas_dict.get(inscrito.cm_pessoa.id),
                "uploads": uploads_pontuacoes_dict.get(inscrito.cm_pessoa.id, []),
                "pontuacao_total": pontuacoes_dict.get(inscrito.cm_pessoa.id, 0.0),
            }
            for inscrito in inscritos
        ]

    def get_pontuacoes(self, vaga, pessoa_ids):
        pontuacoes = {}

        # Checkbox scores - uma query para todas as pessoas
        checkbox_scores = (
            EdPessoaVagaCampoCheckbox.objects.filter(
                ed_vaga_campo_checkbox__ed_vaga=vaga,
                cm_pessoa_id__in=pessoa_ids,
            )
            .values("cm_pessoa_id")
            .annotate(
                total=Coalesce(
                    Sum("ed_vaga_campo_checkbox__pontuacao", output_field=FloatField()),
                    0.0,
                )
            )
        )

        # Combobox scores - uma query para todas as pessoas
        combobox_scores = (
            EdPessoaVagaCampoCombobox.objects.filter(
                ed_vaga_campo_combobox__ed_vaga=vaga,
                cm_pessoa_id__in=pessoa_ids,
            )
            .values("cm_pessoa_id")
            .annotate(
                total=Coalesce(
                    Max("ed_vaga_campo_combobox__pontuacao", output_field=FloatField()),
                    0.0,
                )
            )
        )

        # Datebox scores - uma query para todas as pessoas
        datebox_scores = (
            EdPessoaVagaCampoDatebox.objects.filter(
                ed_vaga_campo_datebox__ed_vaga=vaga,
                cm_pessoa_id__in=pessoa_ids,
            )
            .values("cm_pessoa_id")
            .annotate(
                total=Coalesce(
                    Max(
                        "ed_vaga_campo_datebox__pontuacao_maxima",
                        output_field=FloatField(),
                    ),
                    0.0,
                )
            )
        )

        # Transforma os resultados em dicionários para acesso rápido
        checkbox_dict = {
            item["cm_pessoa_id"]: item["total"] for item in checkbox_scores
        }
        combobox_dict = {
            item["cm_pessoa_id"]: item["total"] for item in combobox_scores
        }
        datebox_dict = {item["cm_pessoa_id"]: item["total"] for item in datebox_scores}

        # Consolida os valores
        for pessoa_id in pessoa_ids:
            pontuacoes[pessoa_id] = (
                float(checkbox_dict.get(pessoa_id, 0.0))
                + float(combobox_dict.get(pessoa_id, 0.0))
                + float(datebox_dict.get(pessoa_id, 0.0))
            )

        return pontuacoes

    def get_uploads_pontuacoes(self, vaga, pessoa_ids):
        """Busca todos os uploads de uma vez, já com descrições padronizadas."""
        uploads_por_pessoa = {pessoa_id: [] for pessoa_id in pessoa_ids}

        def fmt_num(v):
            try:
                v = float(v)
                return str(int(v)) if v.is_integer() else f"{v:.1f}".replace(".", ",")
            except Exception:
                return str(v)

        def plural_ponto(v):
            try:
                v = float(v)
                return (
                    "ponto"
                    if (v == 1 or (v.is_integer() and int(v) == 1))
                    else "pontos"
                )
            except Exception:
                return "pontos"

        # -------- Checkbox uploads --------
        checkbox_uploads = (
            EdPessoaVagaCampoCheckboxUpload.objects.filter(
                ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga=vaga,
                ed_pessoa_vaga_campo_checkbox__cm_pessoa_id__in=pessoa_ids,
            )
            .select_related(
                "ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_campo",
                "ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox",
            )
            .prefetch_related("ed_pessoa_vaga_campo_checkbox__pontuacoes")
        )

        for upload in checkbox_uploads:
            pessoa_id = upload.ed_pessoa_vaga_campo_checkbox.cm_pessoa_id
            pontuacao_obtida = 0
            pontuacao_obj = upload.ed_pessoa_vaga_campo_checkbox.pontuacoes.first()
            if pontuacao_obj:
                pontuacao_obtida = pontuacao_obj.pontuacao or 0

            campo = upload.ed_pessoa_vaga_campo_checkbox.ed_vaga_campo_checkbox
            descricao = campo.ed_campo.descricao
            pmax = campo.pontuacao or 0
            if pmax > 0:
                descricao += f" ({fmt_num(pmax)} {plural_ponto(pmax)})"

            uploads_por_pessoa[pessoa_id].append(
                {
                    "pk": upload.id,
                    "fields": {
                        "tipo": "checkbox",
                        "descricao": descricao,
                        "pontuacao_obtida": pontuacao_obtida,
                        "pontuacao_do_campo": pmax,  # usado no front como max do input
                        "caminho_arquivo": upload.url_download,
                        "validado": upload.validado,
                    },
                }
            )

        # -------- Combobox uploads --------
        # máximo do GRUPO por (vaga + campo): uma agregação só
        maiores_por_campo = (
            EdVagaCampoCombobox.objects.filter(ed_vaga=vaga)
            .values("ed_campo")
            .annotate(maior=Max("pontuacao"))
        )
        max_por_campo = {m["ed_campo"]: m["maior"] for m in maiores_por_campo}

        combobox_uploads = (
            EdPessoaVagaCampoComboboxUpload.objects.filter(
                ed_pessoa_vaga_campo_combobox__cm_pessoa_id__in=pessoa_ids,
                ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga=vaga,
            )
            .select_related(
                "ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_campo",
                "ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox",
            )
            .prefetch_related("ed_pessoa_vaga_campo_combobox__pontuacoes")
        )

        for upload in combobox_uploads:
            pessoa_id = upload.ed_pessoa_vaga_campo_combobox.cm_pessoa_id
            pontuacao_obtida = 0
            pontuacao_obj = upload.ed_pessoa_vaga_campo_combobox.pontuacoes.first()
            if pontuacao_obj:
                pontuacao_obtida = pontuacao_obj.pontuacao or 0

            campo = upload.ed_pessoa_vaga_campo_combobox.ed_vaga_campo_combobox
            descricao = campo.ed_campo.descricao

            # máximo do grupo (vaga + campo), NÃO o valor da opção
            pmax_grupo = max_por_campo.get(campo.ed_campo_id, 0) or 0
            if pmax_grupo > 0:
                descricao += f" ({fmt_num(pmax_grupo)} {plural_ponto(pmax_grupo)})"

            # mas o input no front continua limitado ao valor da opção escolhida:
            pmax_da_opcao = campo.pontuacao or 0

            uploads_por_pessoa[pessoa_id].append(
                {
                    "pk": upload.id,
                    "fields": {
                        "tipo": "combobox",
                        "descricao": descricao,
                        "pontuacao_obtida": pontuacao_obtida,
                        "pontuacao_do_campo": pmax_da_opcao,  # mantém limite correto do input
                        "caminho_arquivo": upload.url_download,
                        "validado": upload.validado,
                    },
                }
            )

        # -------- Datebox uploads --------
        datebox_uploads = (
            EdPessoaVagaCampoDateboxUpload.objects.filter(
                ed_pessoa_vaga_campo_datebox__cm_pessoa_id__in=pessoa_ids,
                ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga=vaga,
            )
            .select_related(
                "ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_campo",
                "ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox",
            )
            .prefetch_related(
                "ed_pessoa_vaga_campo_datebox__pontuacoes",
                "ed_pessoa_vaga_campo_datebox__periodos",
            )
        )

        for upload in datebox_uploads:
            pessoa_id = upload.ed_pessoa_vaga_campo_datebox.cm_pessoa_id
            pontuacao_obtida = 0
            pontuacao_obj = upload.ed_pessoa_vaga_campo_datebox.pontuacoes.first()
            if pontuacao_obj:
                pontuacao_obtida = pontuacao_obj.pontuacao or 0

            campo = upload.ed_pessoa_vaga_campo_datebox.ed_vaga_campo_datebox
            pmax = campo.pontuacao_maxima or 0
            descricao = f"{campo.ed_campo.descricao}"
            if pmax > 0:
                descricao += f" ({fmt_num(pmax)} {plural_ponto(pmax)})"

            periodos = [
                f"{p['inicio']} a {p['fim']}"
                for p in upload.ed_pessoa_vaga_campo_datebox.periodos.values(
                    "inicio", "fim"
                )
            ]
            if periodos:
                descricao += "\n(" + ", ".join(periodos) + ")"

            uploads_por_pessoa[pessoa_id].append(
                {
                    "pk": upload.id,
                    "fields": {
                        "tipo": "datebox",
                        "descricao": descricao,
                        "pontuacao_obtida": pontuacao_obtida,
                        "pontuacao_maxima": pmax,
                        "periodos": list(
                            upload.ed_pessoa_vaga_campo_datebox.periodos.values(
                                "inicio", "fim"
                            )
                        ),
                        "caminho_arquivo": upload.url_download,
                        "validado": upload.validado,
                    },
                }
            )

        return uploads_por_pessoa

    ### POST
    def post(self, request, vaga_id):
        try:
            vaga = EdVaga.objects.get(id=vaga_id)
        except EdVaga.DoesNotExist:
            return Response({"detail": ERRO_GET_VAGA}, status=status.HTTP_404_NOT_FOUND)

        serializer = ValidarVagaPostSerializer(
            data=request.data, context={"vaga": vaga, "request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": OK_DADOS_CANDIDATO}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"detail": ERRO_POST_PESSOAVAGAVALIDACAO, "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(**DOCS_EMITIR_MENSAGEM_FICHA_VAGA_APIVIEW)
class EmitirMensagemFichaVagaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEmissorMensagemCriacaoFicha]

    def get(self, request, vaga_id):
        try:
            vaga = EdVaga.objects.get(id=vaga_id)
        except EdVaga.DoesNotExist:
            return Response({"detail": ERRO_GET_VAGA}, status=status.HTTP_404_NOT_FOUND)

        agora = timezone.now()
        edital = vaga.ed_edital
        if not (edital.data_fim_validacao <= agora <= edital.data_validade):
            return Response(
                {"detail": ERRO_EDITAL_FORA_PRAZO_EMISSAO_MENSAGEM},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.session["vaga_id"] = vaga_id
        request.session["vaga_id_hash"] = gerar_hash(vaga_id)

        validados = EdPessoaVagaValidacao.objects.filter(ed_vaga=vaga).order_by(
            F("pontuacao").desc(nulls_last=True)
        )
        return Response(
            EmitirMensagemFichaVagaSerializer(validados, many=True).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_VERIFICA_VALIDACAO_APIVIEW)
class VerificaValidacaoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsValidadorDeEditais]

    def get(self, request, vaga_id, pessoa_id):
        try:
            return Response(
                VerificaValidacaoSerializer(
                    EdPessoaVagaValidacao.objects.get(
                        cm_pessoa=CmPessoa.objects.get(id=pessoa_id),
                        ed_vaga=EdVaga.objects.get(id=vaga_id),
                    )
                ).data,
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(None, status=status.HTTP_404_NOT_FOUND)


@extend_schema(**DOCS_BAIXAR_ARQUIVOS_APIVIEW)
class BaixarArquivosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsValidadorDeEditais]

    def get(self, request):
        caminho_relativo = request.GET.get("caminho")

        if not caminho_relativo:
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_404_NOT_FOUND
            )

        raiz = Path(RAIZ_ARQUIVOS_UPLOAD).resolve()
        caminho_absoluto = (raiz / caminho_relativo).resolve()

        # Seguranca (inclusive tudo a mesma mensagem para nao mostrar o que aconteceu para o front)
        if not str(caminho_absoluto).startswith(str(raiz)):
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_403_FORBIDDEN
            )

        if not caminho_absoluto.exists():
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_404_NOT_FOUND
            )

        if caminho_absoluto.suffix.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_403_FORBIDDEN
            )

        response = HttpResponse()
        response["Content-Type"] = ""
        response["X-Accel-Redirect"] = f"/arquivos/{caminho_relativo}"
        response["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(caminho_absoluto.name)}"'
        )
        return response


@extend_schema(**DOCS_LISTAR_PESSOAS_PARA_ASSOCIACAO_APIVIEW)
class ListarPessoasParaAssociacaoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalPessoa]

    def get(self, request):
        try:
            # Parametros de busca
            search_term = request.query_params.get("search", "")
            page = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 15))

            # Buscar usuarios com CPF válido
            users_com_cpf = (
                User.objects.exclude(username="")
                .filter(username__regex=r"^\d{11}$")
                .values_list("username", flat=True)
            )

            # Buscar pessoas correspondentes com filtro
            pessoas_query = CmPessoa.objects.filter(cpf__in=users_com_cpf)

            # Aplicar filtro de busca, se fornecido
            if search_term:
                pessoas_query = pessoas_query.filter(
                    Q(nome__icontains=search_term) | Q(cpf__icontains=search_term)
                )

            # Ordenar
            pessoas_query = pessoas_query.order_by("nome")

            # Paginacao
            start = (page - 1) * page_size
            end = start + page_size
            pessoas_page = pessoas_query[start:end]

            # Total para paginacao
            total_count = pessoas_query.count()

            serializer = CmPessoaIdNomeCpfSerializer(pessoas_page, many=True)

            return Response(
                {
                    "results": serializer.data,
                    "count": total_count,
                    "page": page,
                    "total_pages": (total_count + page_size - 1) // page_size,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_PESSOAS}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(**DOCS_LISTAR_EDITAIS_ASSOCIAR_EDITAL_PESSOA_APIVIEW)
class ListarEditaisAssociarEditalPessoaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalPessoa]

    def get(self, request):
        agora = timezone.now()

        # Filtro = editais antes do fim da validacao e antes da validade
        editais = EdEdital.objects.filter(
            data_fim_validacao__gte=agora, data_validade__gte=agora
        ).order_by("-id")

        return Response(
            ListarEditaisAssociacaoEditalPessoaSerializer(editais, many=True).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_BUSCAR_USUARIO_POR_CPF_VIEW)
class BuscarUsuarioPorCpfView(APIView):
    """
    Para criar o botao para editar o usuario na tela
    editais/associar_edital_pessoa/associar_edital_pessoa.html
    Porque nao basta associar o usuario ao edital, ele precisa ir para os grupos
    corretos para ter acesso a as telas
    """

    def get(self, request, cpf):
        try:
            pessoa = CmPessoa.objects.get(cpf=cpf)
        except CmPessoa.DoesNotExist:
            return Response({"erro": ERRO_GET_PESSOA}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(username=pessoa.cpf)
        except User.DoesNotExist:
            return Response(
                {"erro": ERRO_GET_USUARIO}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UsuarioPorCpfSerializer(user)
        return Response(serializer.data)


@extend_schema(**DOCS_ASSOCIAR_EDITAL_PESSOA_APIVIEW)
class AssociarEditalPessoaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalPessoa]

    def get(self, request, edital):
        agora = timezone.now()

        try:
            edital = EdEdital.objects.filter(
                id=edital,
                data_fim_validacao__gte=agora,
                data_validade__gte=agora,
            ).get()
        except EdEdital.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_EDITAL}, status=status.HTTP_404_NOT_FOUND
            )
        except EdEdital.MultipleObjectsReturned:
            return Response(
                {"detail": ERRO_MULTIPLOS_EDITAIS},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_EDITAL}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        associacoes = (
            EdEditalPessoa.objects.select_related("cm_pessoa", "ed_edital")
            .filter(ed_edital=edital)
            .order_by("cm_pessoa__nome")
        )
        serializer = EdGetEditalPessoaSerializer(associacoes, many=True)
        return Response(serializer.data)

    def post(self, request, edital):
        data = request.data.copy()
        data["ed_edital"] = edital

        serializer = EdPostEditalPessoaSerializer(data=data)
        if serializer.is_valid():
            instance, created = EdEditalPessoa.objects.update_or_create(
                ed_edital_id=edital,
                cm_pessoa_id=data.get("cm_pessoa"),
                defaults=serializer.validated_data,
            )
            return Response(
                EdPostEditalPessoaSerializer(instance).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**DOCS_ASSOCIAR_EDITAL_PESSOA_RETRIEVE_DESTROY_APIVIEW)
class AssociarEditalPessoaRetrieveDestroyAPIView(DestroyModelMixin, RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalPessoa]

    queryset = EdEditalPessoa.objects.select_related("cm_pessoa", "ed_edital").all()
    serializer_class = EdGetEditalPessoaSerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@extend_schema(**DOCS_ENVIAR_JUSTIFICATIVA_POR_EMAIL_APIVIEW)
class EnviarJustificativaPorEmailAPIView(APIView):
    serializer_class = CPFSerializer

    def post(self, request, ano, numero):
        serializer = CPFSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cpf = serializer.validated_data["cpf"]

        try:
            edital = EdEdital.objects.get(
                data_inicio_validacao__lt=timezone.now(),
                data_validade__gt=timezone.now(),
                ano=ano,
                numero=numero,
            )
        except EdEdital.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_EDITAL}, status=status.HTTP_404_NOT_FOUND
            )
        except EdEdital.MultipleObjectsReturned:
            return Response(
                {"detail": ERRO_MULTIPLOS_EDITAIS},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_EDITAL}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            pessoa = CmPessoa.objects.get(cpf=cpf)
        except CmPessoa.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_PESSOA}, status=status.HTTP_404_NOT_FOUND
            )

        validado = EdPessoaVagaValidacao.objects.filter(
            cm_pessoa=pessoa, ed_vaga__ed_edital=edital
        ).exists()

        if not validado:
            return Response(
                {"detail": ERRO_GET_PESSOA_VAGA_VALIDACAO},
                status=status.HTTP_404_NOT_FOUND,
            )

        justificativas = EdPessoaVagaJustificativa.objects.filter(
            cm_pessoa=pessoa, ed_vaga__ed_edital=edital
        ).select_related("ed_vaga")

        if not justificativas.exists():
            return Response(
                {"detail": ERRO_GET_PESSOAVAGAJUSTIFICATIVA},
                status=status.HTTP_404_NOT_FOUND,
            )

        assunto = f"{EMAIL_JUSTIFICATIVA_ASSUNTO} {edital.numero}/{edital.ano}"

        justificativa_texto = (
            EMAIL_JUSTIFICATIVA_A_SEGUINTE_JUSTIFICATIVA
            if len(justificativas) == 1
            else EMAIL_JUSTIFICATIVA_AS_SEGUINTES_JUSTIFICATIVAS
        )

        corpo = [
            f"{pessoa.nome},",
            f"{EMAIL_JUSTIFICATIVA_AVALIADOR_REGISTROU} {justificativa_texto} {edital.numero}/{edital.ano} - {edital.descricao}:\n",
        ]

        for j in justificativas:
            corpo.append(
                f"Vaga: {j.ed_vaga}\nJustificativa: {j.justificativa.strip()}\n"
            )

        corpo.append(
            f"{EMAIL_ENDERECO_NAO_MONITORADO}\n{EMAIL_JUSTIFICATIVA_DUVIDAS_PARA_O_ACADEMICO} {INFO_ENTRE_CONTATO_ACADEMICO}"
        )

        mensagem = "\n".join(corpo)

        send_mail(
            assunto,
            mensagem,
            EMAIL_HOST_USER,
            [pessoa.email],
            fail_silently=False,
        )

        return Response(
            {"detail": GetPessoaEmailSerializer(pessoa).data}, status=status.HTTP_200_OK
        )


@extend_schema(**DOCS_RELATORIO_DO_EDITAL_APIVIEW)
class RelatorioDoEditalAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioDeEditais]
    renderer_classes = [CSVRenderer]

    def get(self, request, ano, numero):
        try:
            edital = EdEdital.objects.get(ano=ano, numero=numero)
        except EdEdital.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_EDITAL}, status=status.HTTP_404_NOT_FOUND
            )

        vagas = EdVaga.objects.filter(ed_edital=edital)
        relatorio = []

        for vaga in vagas:
            for inscricao in EdPessoaVagaInscricao.objects.filter(ed_vaga=vaga):
                # Espera-se que haja apenas uma validacao, justificativa, etc, mas por seguranca usei filter + first
                validacao = EdPessoaVagaValidacao.objects.filter(
                    ed_vaga=vaga, cm_pessoa=inscricao.cm_pessoa
                ).first()
                justificativa = EdPessoaVagaJustificativa.objects.filter(
                    ed_vaga=vaga, cm_pessoa=inscricao.cm_pessoa
                ).first()
                confirmacao = EdPessoaVagaConfirmacao.objects.filter(
                    ed_vaga=vaga, cm_pessoa=inscricao.cm_pessoa
                ).first()
                cota = EdPessoaVagaCota.objects.filter(
                    cm_pessoa=inscricao.cm_pessoa, ed_vaga_cota__ed_vaga=vaga
                ).first()

                # No sistema antigo o candidato considerado validado tinha todos os documentos validos
                # Ou seja, ou ele estava validado ou se usava o campo justificativa para saber o que nao esta' valido
                if validacao and validacao.cm_pessoa_responsavel_validacao:
                    responsavel = validacao.cm_pessoa_responsavel_validacao.nome
                elif (
                    justificativa and justificativa.cm_pessoa_responsavel_justificativa
                ):
                    responsavel = justificativa.cm_pessoa_responsavel_justificativa.nome
                else:
                    responsavel = "-"

                dados_inscricao = {
                    "protocolo": inscricao.id,
                    "vaga": vaga.descricao,
                    "nome": inscricao.cm_pessoa.nome,
                    "cpf": inscricao.cm_pessoa.cpf_com_pontos_e_traco(),
                    "email": inscricao.cm_pessoa.email,
                    "pontuacao_informada": (
                        0.0
                        if inscricao.pontuacao is None
                        else float(inscricao.pontuacao)
                    ),
                    # 0 = NULL, se validado
                    "pontuacao_real": (
                        0.0
                        if validacao and validacao.pontuacao is None
                        else (
                            float(validacao.pontuacao)
                            if validacao and validacao.pontuacao is not None
                            else "-"
                        )
                    ),
                    "responsavel_validacao_ou_justificativa": responsavel,
                    "data_inscricao": (
                        timezone.localtime(inscricao.data).strftime("%d/%m/%Y %H:%M")
                        if inscricao and inscricao.data
                        else "-"
                    ),
                    "data_validacao": (
                        timezone.localtime(validacao.data).strftime("%d/%m/%Y %H:%M")
                        if validacao and validacao.data
                        else "-"
                    ),
                    "justificativa_pontuacao": (
                        justificativa.justificativa if justificativa else "-"
                    ),
                    "confirmado": "Sim" if confirmacao else "Não",
                    "cota": cota.ed_vaga_cota.ed_cota.cota if cota else "-",
                }

                relatorio.append(RelatorioEditalSerializer(dados_inscricao).data)

        if not relatorio:
            return Response(
                [
                    {
                        "protocolo": "",
                        "vaga": "",
                        "nome": "",
                        "cpf": "",
                        "email": "",
                        "pontuacao_informada": "",
                        "pontuacao_real": "",
                        "responsavel_validacao_ou_justificativa": "",
                        "data_inscricao": "",
                        "data_validacao": "",
                        "justificativa_pontuacao": "",
                        "confirmado": "",
                        "cota": "",
                    }
                ],
                status=status.HTTP_200_OK,
            )
        return Response(relatorio, status=status.HTTP_200_OK)


@extend_schema(**DOCS_RELATORIO_DA_VAGA_APIVIEW)
class RelatorioDaVagaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioDeEditais]
    renderer_classes = [CSVRenderer]

    def get(self, request, vaga_id):
        try:
            vaga = EdVaga.objects.get(id=vaga_id)
        except EdVaga.DoesNotExist:
            return Response({"detail": ERRO_GET_VAGA}, status=status.HTTP_404_NOT_FOUND)

        relatorio = []

        for inscricao in EdPessoaVagaInscricao.objects.filter(ed_vaga=vaga):
            validacao = EdPessoaVagaValidacao.objects.filter(
                ed_vaga=vaga, cm_pessoa=inscricao.cm_pessoa
            ).first()
            justificativa = EdPessoaVagaJustificativa.objects.filter(
                ed_vaga=vaga, cm_pessoa=inscricao.cm_pessoa
            ).first()
            confirmacao = EdPessoaVagaConfirmacao.objects.filter(
                ed_vaga=vaga, cm_pessoa=inscricao.cm_pessoa
            ).first()
            cota = EdPessoaVagaCota.objects.filter(
                cm_pessoa=inscricao.cm_pessoa, ed_vaga_cota__ed_vaga=vaga
            ).first()

            if validacao and validacao.cm_pessoa_responsavel_validacao:
                responsavel = validacao.cm_pessoa_responsavel_validacao.nome
            elif justificativa and justificativa.cm_pessoa_responsavel_justificativa:
                responsavel = justificativa.cm_pessoa_responsavel_justificativa.nome
            else:
                responsavel = "-"

            dados_inscricao = {
                "protocolo": inscricao.id,
                "nome": inscricao.cm_pessoa.nome,
                "cpf": inscricao.cm_pessoa.cpf_com_pontos_e_traco(),
                "email": inscricao.cm_pessoa.email,
                "pontuacao_informada": (
                    0.0 if inscricao.pontuacao is None else float(inscricao.pontuacao)
                ),
                # 0 = NULL, se validado
                "pontuacao_real": (
                    0.0
                    if validacao and validacao.pontuacao is None
                    else (
                        float(validacao.pontuacao)
                        if validacao and validacao.pontuacao is not None
                        else "-"
                    )
                ),
                "responsavel_validacao_ou_justificativa": responsavel,
                "data_inscricao": (
                    timezone.localtime(inscricao.data).strftime("%d/%m/%Y %H:%M")
                    if inscricao and inscricao.data
                    else "-"
                ),
                "data_validacao": (
                    timezone.localtime(validacao.data).strftime("%d/%m/%Y %H:%M")
                    if validacao and validacao.data
                    else "-"
                ),
                "justificativa_pontuacao": (
                    justificativa.justificativa if justificativa else "-"
                ),
                "confirmado": "Sim" if confirmacao else "Não",
                "cota": cota.ed_vaga_cota.ed_cota.cota if cota else "-",
            }

            relatorio.append(RelatorioVagaSerializer(dados_inscricao).data)

        if not relatorio:
            return Response(
                [
                    {
                        "protocolo": "",
                        "nome": "",
                        "cpf": "",
                        "email": "",
                        "pontuacao_informada": "",
                        "pontuacao_real": "",
                        "responsavel_validacao_ou_justificativa": "",
                        "data_inscricao": "",
                        "data_validacao": "",
                        "justificativa_pontuacao": "",
                        "confirmado": "",
                        "cota": "",
                    }
                ],
                status=status.HTTP_200_OK,
            )
        return Response(relatorio, status=status.HTTP_200_OK)
