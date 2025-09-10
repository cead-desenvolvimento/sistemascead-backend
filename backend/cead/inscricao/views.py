import imghdr
import os
import shutil
from datetime import datetime
from pathlib import Path

from PyPDF2 import PdfReader
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from cead.models import (
    CmFormacao,
    CmPessoa,
    EdCampo,
    EdCota,
    EdEdital,
    EdPessoaFormacao,
    EdPessoaVagaCampoCheckbox,
    EdPessoaVagaCampoCheckboxUpload,
    EdPessoaVagaCampoCombobox,
    EdPessoaVagaCampoComboboxUpload,
    EdPessoaVagaCampoDatebox,
    EdPessoaVagaCampoDateboxPeriodo,
    EdPessoaVagaCampoDateboxUpload,
    EdPessoaVagaCota,
    EdPessoaVagaInscricao,
    EdVaga,
    EdVagaCampoCheckbox,
    EdVagaCampoCombobox,
    EdVagaCampoDatebox,
    EdVagaCota,
)
from cead.settings import EMAIL_HOST_USER, RAIZ_ARQUIVOS_UPLOAD
from cead.utils import cortar_nome_arquivo, gerar_hash
from cead.messages import (
    EMAIL_ASSINATURA,
    EMAIL_DUVIDAS_PARA_O_SUPORTE,
    EMAIL_ENDERECO_NAO_MONITORADO,
    ERRO_GET_ARQUIVO,
    ERRO_GET_EDITAL,
    ERRO_GET_VAGA,
    ERRO_GET_VAGAS,
    ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_CHECKBOX,
    ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_COMBOBOX,
    ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX,
    ERRO_MULTIPLOS_EDITAIS,
    ERRO_SESSAO_INVALIDA,
    ERRO_VAGAID_NA_SESSAO,
    ERRO_VAGAIDHASH_NA_SESSAO,
    INFO_ENTRE_CONTATO_ACADEMICO,
    INFO_ENTRE_CONTATO_SUPORTE,
)
from cead.serializers import CPFSerializer, GetPessoaEmailSerializer

from .api_docs import *
from .messages import *
from .serializers import (
    CheckboxPessoaSerializer,
    CheckboxSerializer,
    CmPessoaPostSerializer,
    ComboboxPessoaSerializer,
    CotaMarcadaSerializer,
    DateboxPessoaSerializer,
    DateboxSerializer,
    GetEditaisSerializer,
    GetPessoaFormacaoSerializer,
    GetVagasSerializer,
    PessoaVagaCotaSerializer,
    PostPessoaFormacaoSerializer,
    PostVagasSerializer,
)
from .utils import *


def apaga_outra_inscricao_no_mesmo_edital(pessoa_id, ed_pessoa_vaga_inscricao_id):
    try:
        ed_pessoa_vaga_inscricao = EdPessoaVagaInscricao.objects.get(
            id=ed_pessoa_vaga_inscricao_id
        )
        vaga_id = ed_pessoa_vaga_inscricao.ed_vaga_id

        # -----------------------------
        # 1. Apaga filhos do Datebox (Periodos e Uploads)
        # -----------------------------
        EdPessoaVagaCampoDateboxPeriodo.objects.filter(
            ed_pessoa_vaga_campo_datebox__cm_pessoa_id=pessoa_id,
            ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga_id=vaga_id,
        ).delete()

        EdPessoaVagaCampoDateboxUpload.objects.filter(
            ed_pessoa_vaga_campo_datebox__cm_pessoa_id=pessoa_id,
            ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga_id=vaga_id,
        ).delete()

        # -----------------------------
        # 2. Apaga filhos de Combobox e Checkbox (Uploads)
        # -----------------------------
        EdPessoaVagaCampoCheckboxUpload.objects.filter(
            ed_pessoa_vaga_campo_checkbox__cm_pessoa_id=pessoa_id,
            ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga_id=vaga_id,
        ).delete()

        EdPessoaVagaCampoComboboxUpload.objects.filter(
            ed_pessoa_vaga_campo_combobox__cm_pessoa_id=pessoa_id,
            ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga_id=vaga_id,
        ).delete()

        # -----------------------------
        # 3. Apaga os registros principais dos campos
        # -----------------------------
        EdPessoaVagaCampoDatebox.objects.filter(
            cm_pessoa_id=pessoa_id,
            ed_vaga_campo_datebox__ed_vaga_id=vaga_id,
        ).delete()

        EdPessoaVagaCampoCheckbox.objects.filter(
            cm_pessoa_id=pessoa_id,
            ed_vaga_campo_checkbox__ed_vaga_id=vaga_id,
        ).delete()

        EdPessoaVagaCampoCombobox.objects.filter(
            cm_pessoa_id=pessoa_id,
            ed_vaga_campo_combobox__ed_vaga_id=vaga_id,
        ).delete()

        # -----------------------------
        # 4. Apaga a inscrição em si
        # -----------------------------
        ed_pessoa_vaga_inscricao.delete()

        # -----------------------------
        # 5. Apaga arquivos do upload local (se existirem)
        # -----------------------------
        pasta_a_apagar = os.path.join(
            RAIZ_ARQUIVOS_UPLOAD,
            f"{pessoa_id}_{vaga_id}",
        )
        if os.path.exists(pasta_a_apagar):
            shutil.rmtree(pasta_a_apagar)

    except EdPessoaVagaInscricao.DoesNotExist:
        pass

    except Exception as e:
        return Response(
            {"detail": f"{ERRO_APAGAR_INSCRICAO_CONCORRENTE}: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def get_ed_pessoa_vaga_campos(request):
    checkboxes_da_pessoa = EdPessoaVagaCampoCheckbox.objects.filter(
        cm_pessoa=request.candidato, ed_vaga_campo_checkbox__ed_vaga=request.vaga
    )

    comboboxes_da_pessoa = EdPessoaVagaCampoCombobox.objects.filter(
        cm_pessoa=request.candidato, ed_vaga_campo_combobox__ed_vaga=request.vaga
    )

    dateboxes_da_pessoa = EdPessoaVagaCampoDatebox.objects.filter(
        cm_pessoa=request.candidato, ed_vaga_campo_datebox__ed_vaga=request.vaga
    )

    return {
        "checkboxes": checkboxes_da_pessoa,
        "comboboxes": comboboxes_da_pessoa,
        "dateboxes": dateboxes_da_pessoa,
    }


def verificar_assinatura_pdf(caminho):
    """
    Verifica se um PDF possui pelo menos uma assinatura digital válida
    Retorna True se encontrar pelo menos uma assinatura, False caso contrário
    """
    with open(caminho, "rb") as f:
        reader = PdfReader(f)
        if reader.get_fields():
            for field_name, field in reader.get_fields().items():
                if field.get("/FT") == "/Sig":
                    return True
        return False


@extend_schema(**DOCS_EDITAIS_FASE_INSCRICAO_VIEW)
class EditaisFaseInscricaoView(APIView):
    def get(self, request):
        request.session.flush()

        editais = EdEdital.objects.filter(
            data_inicio_inscricao__lte=timezone.now(),
            data_fim_inscricao__gte=timezone.now(),
        ).order_by("-id")

        return Response(
            GetEditaisSerializer(editais, many=True).data, status=status.HTTP_200_OK
        )


@extend_schema(**DOCS_VAGAS_EDITAL_FASE_INSCRICAO_VIEW)
class VagasEditalFaseInscricaoView(GenericAPIView):
    serializer_class = PostVagasSerializer

    def get(self, request, ano, numero):
        try:
            edital = EdEdital.objects.get(ano=ano, numero=numero)
        except EdEdital.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_EDITAL}, status=status.HTTP_404_NOT_FOUND
            )
        except EdEdital.MultipleObjectsReturned:
            return Response(
                {"detail": ERRO_MULTIPLOS_EDITAIS},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_VAGAS}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if edital.data_fim_inscricao < timezone.now():
            return Response(
                {"detail": ERRO_INSCRICOES_ENCERRADAS}, status=status.HTTP_302_FOUND
            )
        return Response(
            GetVagasSerializer(EdVaga.objects.filter(ed_edital=edital), many=True).data,
            status=status.HTTP_200_OK,
        )

    # Colocar o ID da vaga na sessão (controle de fluxo da inscrição)
    def post(self, request, ano, numero):
        try:
            vaga_id = request.data.get("vaga_id")
            if vaga_id:
                vaga = EdVaga.objects.get(
                    id=vaga_id, ed_edital__ano=ano, ed_edital__numero=numero
                )
            else:
                return Response(
                    {"detail": ERRO_REQUEST_DATA_GET_VAGAID},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except EdVaga.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_VAGAS}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_GET_VAGAS}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        request.session["vaga_selecionada"] = vaga.id
        request.session["vaga_selecionada_hash"] = gerar_hash(vaga.id)

        return Response({"detail": OK_VAGAID_NA_SESSAO}, status=status.HTTP_200_OK)


@extend_schema(**DOCS_VALIDAR_CPF_VIEW)
class ValidarCPFView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga

    def post(self, request):
        serializer = CPFSerializer(data=request.data)
        if serializer.is_valid():
            cpf = serializer.validated_data["cpf"]
            try:
                pessoa = CmPessoa.objects.get(cpf=cpf)
                request.session["candidato"] = pessoa.id
                request.session["candidato_hash"] = gerar_hash(pessoa.id)

                return Response(
                    {"detail": OK_PESSOA_ENCONTRADA}, status=status.HTTP_200_OK
                )
            except CmPessoa.DoesNotExist:
                return Response(
                    {"detail": OK_PESSOA_NAO_ENCONTRADA, "cpf": cpf},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**DOCS_CRIAR_PESSOA_VIEW)
class CriarPessoaView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga

    def post(self, request):
        serializer = CmPessoaPostSerializer(data=request.data)

        if serializer.is_valid():
            try:
                pessoa = serializer.save()
                request.session["candidato"] = pessoa.id
                request.session["candidato_hash"] = gerar_hash(pessoa.id)
                return Response(
                    {"detail": OK_INSERCAO_CM_PESSOA, "pessoa_id": pessoa.id},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"detail": f"{ERRO_INSERCAO_CM_PESSOA}: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"detail": ERRO_APRESENTACAO_CM_PESSOA, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(**DOCS_ENVIAR_CODIGO_EMAIL_VIEW)
class EnviarCodigoEmailView(GenericAPIView):
    serializer_class = GetPessoaEmailSerializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    def get(self, request):
        return Response(
            GetPessoaEmailSerializer(request.candidato).data, status=status.HTTP_200_OK
        )

    def post(self, request):
        # Cria timestamp em blocos de 10 minutos (600 segundos)
        agora = timezone.now()
        bloco_timestamp = int(agora.timestamp() // 600) * 600

        # Hash com candidato_hash + bloco de tempo
        codigo_seed = f"{request.session['candidato_hash']}{bloco_timestamp}"
        codigo = gerar_hash(codigo_seed)[:5].upper()

        # Salva quando foi gerado para validação de expiração
        request.session["codigo_email_gerado_em"] = agora.isoformat()

        assunto = f"{EMAIL_INSCRICAO_ASSUNTO}"
        mensagem = (
            f"{request.candidato.nome},\n"
            f"{EMAIL_INSCRICAO_CODIGO_GERADO}: {codigo}\n"
            f"{request.vaga.ed_edital} - {request.vaga}\n\n"
            f"{EMAIL_ENDERECO_NAO_MONITORADO}\n"
            f"{EMAIL_DUVIDAS_PARA_O_SUPORTE} {INFO_ENTRE_CONTATO_SUPORTE}\n"
            f"{EMAIL_INSCRICAO_DUVIDAS_PARA_O_ACADEMICO} {INFO_ENTRE_CONTATO_ACADEMICO}\n\n"
            f"{EMAIL_ASSINATURA}"
        )

        send_mail(
            assunto,
            mensagem,
            EMAIL_HOST_USER,
            [request.candidato.email],
            fail_silently=False,
        )

        return Response({"detail": OK_CODIGO_EMAIL_ENVIADO}, status=status.HTTP_200_OK)


@extend_schema(**DOCS_VERIFICAR_CODIGO_VIEW)
class VerificarCodigoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    def post(self, request):
        serializer = serializers.Serializer(data=request.data)
        serializer.fields["codigo"] = serializers.CharField(max_length=5)
        serializer.is_valid(raise_exception=True)

        codigo_digitado = serializer.validated_data["codigo"].upper()

        gerado_em = request.session.get("codigo_email_gerado_em")
        if not gerado_em:
            return Response(
                {"detail": ERRO_CODIGO_AUSENTE}, status=status.HTTP_400_BAD_REQUEST
            )

        agora = timezone.now()
        criado = timezone.datetime.fromisoformat(gerado_em)

        if agora > criado + timezone.timedelta(minutes=10):
            return Response(
                {"detail": ERRO_CODIGO_EXPIRADO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Testa o bloco de tempo corrente e o anterior para cobrir transições do bloco
        bloco_de_tempo_corrente = int(agora.timestamp() // 600) * 600
        bloco_de_tempo_anterior = bloco_de_tempo_corrente - 600

        # Gera códigos para os dois blocos
        codigo_seed_corrente = (
            f"{request.session['candidato_hash']}{bloco_de_tempo_corrente}"
        )
        codigo_seed_anterior = (
            f"{request.session['candidato_hash']}{bloco_de_tempo_anterior}"
        )

        codigo_esperado_corrente = gerar_hash(codigo_seed_corrente)[:5].upper()
        codigo_esperado_anterior = gerar_hash(codigo_seed_anterior)[:5].upper()

        if codigo_digitado not in [codigo_esperado_corrente, codigo_esperado_anterior]:
            return Response(
                {"detail": ERRO_CODIGO_EMAIL}, status=status.HTTP_400_BAD_REQUEST
            )

        del request.session["codigo_email_gerado_em"]
        request.session["codigo_candidato"] = codigo_digitado
        request.session["codigo_candidato_hash"] = gerar_hash(codigo_digitado)
        return Response({"detail": OK_CODIGO_EMAIL_VALIDADO}, status=status.HTTP_200_OK)


@extend_schema(**DOCS_ASSOCIAR_PESSOA_VAGA_COTA_VIEW)
class AssociarPessoaVagaCotaView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})
        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    def get(self, request, *args, **kwargs):
        try:
            cotas_disponiveis = [
                vaga_cota.ed_cota
                for vaga_cota in EdVagaCota.objects.filter(ed_vaga=request.vaga)
            ]

            if cotas_disponiveis:
                try:
                    pessoa_vaga_cota = EdPessoaVagaCota.objects.get(
                        cm_pessoa=request.candidato, ed_vaga_cota__ed_vaga=request.vaga
                    )
                    cota_marcada = pessoa_vaga_cota.ed_vaga_cota.ed_cota
                except EdPessoaVagaCota.DoesNotExist:
                    cota_marcada = None
                except EdPessoaVagaCota.MultipleObjectsReturned:
                    raise ValidationError({"detail": ERRO_MULTIPLAS_COTAS})
                except Exception as e:
                    raise ValidationError({"detail": f"{ERRO_GET_COTA}: {str(e)}"})
            else:
                cota_marcada = None

            serializer = PessoaVagaCotaSerializer(
                {"cotas_disponiveis": cotas_disponiveis, "cota_marcada": cota_marcada}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError({"detail": f"{ERRO_GET_COTA}: {str(e)}"})

    def post(self, request, *args, **kwargs):
        cota_id = request.data.get("cota")
        if not cota_id:
            raise ValidationError({"detail": ERRO_POST_COTA})

        try:
            cota = EdCota.objects.get(id=cota_id)
        except EdCota.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_COTA})

        try:
            vaga_cota = EdVagaCota.objects.get(ed_vaga=request.vaga, ed_cota=cota)
        except EdVagaCota.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA_COTA})
        except Exception as e:
            raise ValidationError({"detail": f"{ERRO_GET_VAGA_COTA}: {str(e)}"})

        try:
            pessoa_vaga_cota, created = EdPessoaVagaCota.objects.update_or_create(
                cm_pessoa=request.candidato,
                ed_vaga_cota__ed_vaga=request.vaga,
                defaults={"ed_vaga_cota": vaga_cota},
            )
        except Exception as e:
            raise ValidationError(
                {"detail": f"{ERRO_INSERCAO_ED_PESSOA_VAGA_COTA}: {str(e)}"}
            )

        return Response(
            CotaMarcadaSerializer(vaga_cota.ed_cota).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, cota_id=None):
        try:
            cota = EdCota.objects.get(id=cota_id)
        except EdCota.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_COTA})

        try:
            vaga_cota = EdVagaCota.objects.get(ed_vaga=request.vaga, ed_cota=cota)
        except EdVagaCota.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA_COTA})
        except Exception as e:
            raise ValidationError({"detail": f"{ERRO_GET_VAGA_COTA}: {str(e)}"})

        try:
            EdPessoaVagaCota.objects.get(
                ed_vaga_cota=vaga_cota, cm_pessoa=request.candidato
            ).delete()
            return Response(
                {"detail": OK_REMOCAO_ED_PESSOA_VAGA_COTA}, status=status.HTTP_200_OK
            )
        except EdPessoaVagaCota.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_PESSOA_VAGA_COTA}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_REMOCAO_ED_PESSOA_VAGA_COTA}: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(**DOCS_LISTAR_PESSOA_FORMACAO_VIEW)
class ListarPessoaFormacaoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.candidato = candidato

    def get(self, request):
        pessoa_formacoes_serializer = GetPessoaFormacaoSerializer(
            EdPessoaFormacao.objects.filter(cm_pessoa=request.candidato), many=True
        )
        return Response(
            {
                "pessoa_formacoes": pessoa_formacoes_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(request=PostPessoaFormacaoSerializer)
    def post(self, request):
        try:
            EdPessoaFormacao.objects.create(
                cm_pessoa=request.candidato,
                cm_formacao=CmFormacao.objects.get(
                    id=request.data.get("ed_pessoa_formacao_id")
                ),
                inicio=request.data.get("inicio"),
                fim=request.data.get("fim"),
            )
            return Response(
                {"detail": OK_INSERCAO_ED_PESSOA_FORMACAO},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_INSERCAO_ED_PESSOA_FORMACAO}: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, formacao_id=None):
        try:
            EdPessoaFormacao.objects.get(
                id=formacao_id, cm_pessoa=request.candidato
            ).delete()
            return Response(
                {"detail": OK_REMOCAO_ED_PESSOA_FORMACAO}, status=status.HTTP_200_OK
            )
        except EdPessoaFormacao.DoesNotExist:
            return Response(
                {"detail": ERRO_GET_PESSOA_FORMACAO}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"{ERRO_REMOCAO_ED_PESSOA_FORMACAO}: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(**DOCS_LISTAR_FORMACAO_VIEW)
class ListarFormacaoView(APIView):
    def get(self, request):
        termo = request.GET.get("termo", "").strip().lower()
        formacoes = CmFormacao.get_formacoes()

        if termo:
            formacoes = [
                f
                for f in formacoes
                if termo in f["nome"].lower()
                or termo in f["cm_titulacao__nome"].lower()
            ]

        return Response({"formacoes_disponiveis": formacoes}, status=status.HTTP_200_OK)


@extend_schema(**DOCS_ALERTA_INSCRICAO_VIEW)
class AlertaInscricaoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    # Primeiro testa a vaga, se der, ja responde e sai, depois nas outras vagas do mesmo edital
    def get(self, request):
        if EdPessoaVagaInscricao.objects.filter(
            cm_pessoa_id=request.candidato.id, ed_vaga_id=request.vaga
        ).exists():
            return Response(
                {"alerta_inscricao": INFO_JA_INSCRITO_MESMA_VAGA},
                status=status.HTTP_200_OK,
            )

        inscricao_no_edital = EdPessoaVagaInscricao.objects.filter(
            cm_pessoa_id=request.candidato.id, ed_vaga__ed_edital=request.vaga.ed_edital
        ).first()

        if inscricao_no_edital:
            edital = inscricao_no_edital.ed_vaga.ed_edital
            if edital.multiplas_inscricoes:
                alerta_inscricao = (
                    INFO_JA_INSCRITO_MESMO_EDITAL_COM_MULTIPLAS_INSCRICOES
                )
            else:
                alerta_inscricao = (
                    INFO_JA_INSCRITO_MESMO_EDITAL_SEM_MULTIPLAS_INSCRICOES
                )
                request.session["inscricao_concorrente"] = inscricao_no_edital.id
                request.session["inscricao_concorrente_hash"] = gerar_hash(
                    inscricao_no_edital.id
                )

            return Response(
                {"alerta_inscricao": alerta_inscricao}, status=status.HTTP_200_OK
            )

        return Response({"alerta_inscricao": None}, status=status.HTTP_200_OK)


@extend_schema(**DOCS_VAGA_CAMPOS_VIEW)
class VagaCamposView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    def get(self, request):
        checkboxes_da_vaga = EdVagaCampoCheckbox.objects.filter(ed_vaga=request.vaga)
        comboboxes_da_vaga = EdVagaCampoCombobox.objects.filter(
            ed_vaga=request.vaga
        ).order_by("ed_campo_id", "ordem")
        dateboxes_da_vaga = EdVagaCampoDatebox.objects.filter(ed_vaga=request.vaga)

        response_data = {}

        if checkboxes_da_vaga.exists():
            checkboxes_serializer = CheckboxSerializer(checkboxes_da_vaga, many=True)
            response_data["checkboxes"] = checkboxes_serializer.data

        # Agrupar os comboboxes pela descricao do campo
        if comboboxes_da_vaga.exists():
            comboboxes_da_vaga_separados = {}
            for item in comboboxes_da_vaga:
                descricao = item.ed_campo.descricao
                detalhes = {
                    "id": item.id,
                    "descricao": item.descricao,
                    "pontuacao": item.pontuacao,
                    "obrigatorio": item.obrigatorio,
                }
                if descricao not in comboboxes_da_vaga_separados:
                    comboboxes_da_vaga_separados[descricao] = []
                comboboxes_da_vaga_separados[descricao].append(detalhes)
            response_data["comboboxes"] = comboboxes_da_vaga_separados

        if dateboxes_da_vaga.exists():
            dateboxes_serializer = DateboxSerializer(dateboxes_da_vaga, many=True)
            response_data["dateboxes"] = dateboxes_serializer.data

        if response_data:
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": ERRO_GET_CAMPOS_DA_VAGA}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(**DOCS_PESSOA_VAGA_CAMPO_VIEW)
class PessoaVagaCampoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    def get(self, request):
        ed_pessoa_vaga_campos = get_ed_pessoa_vaga_campos(request)

        response_data = {
            "checkboxes": CheckboxPessoaSerializer(
                ed_pessoa_vaga_campos["checkboxes"], many=True
            ).data,
            "comboboxes": ComboboxPessoaSerializer(
                ed_pessoa_vaga_campos["comboboxes"], many=True
            ).data,
            "dateboxes": DateboxPessoaSerializer(
                ed_pessoa_vaga_campos["dateboxes"], many=True
            ).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        ed_pessoa_vaga_campos = get_ed_pessoa_vaga_campos(request)

        checkboxes_da_vaga = EdVagaCampoCheckbox.objects.filter(ed_vaga=request.vaga)
        comboboxes_da_vaga = EdVagaCampoCombobox.objects.filter(
            ed_vaga=request.vaga
        ).order_by("ed_campo_id", "ordem")
        dateboxes_da_vaga = EdVagaCampoDatebox.objects.filter(ed_vaga=request.vaga)

        pontuacao_candidato = 0

        ## Processa checkboxes
        array_temporario_id_checkbox_vaga = [
            # Filtra o POST, so pega o checkbox associado, medida de seguranca
            int(item)
            for item in request.data.get("checkbox_da_vaga", [])
            if int(item) in checkboxes_da_vaga.values_list("id", flat=True)
        ]

        # Adiciona os campos obrigatorios e que nao vem no POST
        for checkbox_obrigatorio_vaga in checkboxes_da_vaga.filter(
            obrigatorio=True
        ).values_list("id", flat=True):
            if checkbox_obrigatorio_vaga not in array_temporario_id_checkbox_vaga:
                array_temporario_id_checkbox_vaga.append(checkbox_obrigatorio_vaga)

        for id_checkbox_vaga in array_temporario_id_checkbox_vaga:
            try:
                EdPessoaVagaCampoCheckbox.objects.get_or_create(
                    cm_pessoa=request.candidato,
                    ed_vaga_campo_checkbox_id=id_checkbox_vaga,
                )
                pontuacao = EdVagaCampoCheckbox.objects.get(
                    id=id_checkbox_vaga
                ).pontuacao
                if pontuacao:
                    pontuacao_candidato += pontuacao
            except Exception as e:
                return Response(
                    {"detail": f"{ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_CHECKBOX}: {e}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ## Comboboxes, para facilitar a logica de processamento, sao sempre obrigatorios
        ## O filtro segue abaixo...
        array_temporario_id_combobox_vaga = [
            int(combobox_id)
            for combobox_id in request.data.get("combobox_da_vaga", [])
            if int(combobox_id) in comboboxes_da_vaga.values_list("id", flat=True)
        ]

        # ... como e' obrigatorio, adiciona o que o candidato marcou, salvo se 0/NULL
        # Esse tipo de campo geralmente e' pontuacao por numero de certificados
        # O zero e' placeholder no frontend
        for id_combobox_vaga in array_temporario_id_combobox_vaga:
            try:
                combobox = EdVagaCampoCombobox.objects.get(id=id_combobox_vaga)
                pontuacao = combobox.pontuacao

                if pontuacao and pontuacao > 0:
                    EdPessoaVagaCampoCombobox.objects.get_or_create(
                        cm_pessoa=request.candidato, ed_vaga_campo_combobox=combobox
                    )
                    pontuacao_candidato += pontuacao

            except Exception as e:
                return Response(
                    {"detail": f"{ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_COMBOBOX}: {e}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ## Dateboxes
        # Captura o JSON enviado e garante que seja um dicionário
        dateboxes_da_vaga_dict = request.data.get("datebox_da_vaga", {}) or {}

        if not isinstance(dateboxes_da_vaga_dict, dict):
            return Response(
                {"detail": ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX_OBJETO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proteção extra: filtrar apenas os IDs válidos do banco
        dateboxes_validos = set(dateboxes_da_vaga.values_list("id", flat=True))
        dateboxes_da_vaga_dict = {
            int(datebox_id): periodos
            for datebox_id, periodos in dateboxes_da_vaga_dict.items()
            if int(datebox_id) in dateboxes_validos
        }

        # Garante que os obrigatórios estejam presentes
        for datebox_obrigatorio_vaga in dateboxes_da_vaga.filter(
            obrigatorio=True
        ).values_list("id", flat=True):
            if datebox_obrigatorio_vaga not in dateboxes_da_vaga_dict:
                # Se o candidato não enviou este datebox obrigatório,
                # adiciona um período vazio para que o campo ainda passe
                # pelo fluxo normal de validação (e gere erro se faltando).
                dateboxes_da_vaga_dict[datebox_obrigatorio_vaga] = [{}]

        # Processamento dos dateboxes
        for id_datebox_data, periodos in dateboxes_da_vaga_dict.items():
            if not isinstance(periodos, list):
                periodos = [periodos]

            try:
                datebox_obj = EdVagaCampoDatebox.objects.get(id=id_datebox_data)

                ed_pessoa_vaga_campo_datebox_obj, _ = (
                    EdPessoaVagaCampoDatebox.objects.get_or_create(
                        cm_pessoa=request.candidato,
                        ed_vaga_campo_datebox_id=id_datebox_data,
                    )
                )

                # 1. Obtém todos os períodos relacionados ao campo, para
                # não ter que apagar em caso das datas não terem mudado

                # Qual o problema? A pessoa entra com a data A até B, e depois edita
                # de A até C, então preciso saber o que mudou para apagar o antigo

                # Poderia apagar tudo antes e salvar de novo, mas não é elegante
                periodos_existentes = list(
                    EdPessoaVagaCampoDateboxPeriodo.objects.filter(
                        ed_pessoa_vaga_campo_datebox=ed_pessoa_vaga_campo_datebox_obj
                    )
                )

                # 2. Converte para set de tuplas (inicio, fim)
                periodos_existentes_set = {
                    (p.inicio, p.fim) for p in periodos_existentes
                }

                # 3. Prepara os novos períodos a partir do POST
                periodos_recebidos_set = set()
                periodos_recebidos_info = []

                for periodo in periodos:
                    date_inicio = (
                        datetime.strptime(periodo.get("inicio"), "%Y-%m-%d").date()
                        if periodo.get("inicio")
                        else None
                    )
                    date_fim = (
                        datetime.strptime(periodo.get("fim"), "%Y-%m-%d").date()
                        if periodo.get("fim")
                        else None
                    )

                    if date_inicio is None:
                        raise Exception(
                            ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX_INICIO_INVALIDO
                        )
                    if date_fim is None:
                        raise Exception(
                            ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX_FIM_INVALIDO
                        )
                    if date_fim <= date_inicio:
                        raise Exception(
                            ERRO_INSCRICAO_DATA_FORMACAO_FIM_MAIOR_OU_IGUAL_DATA_FORMACAO_INICIO
                        )

                    periodos_recebidos_set.add((date_inicio, date_fim))
                    periodos_recebidos_info.append((date_inicio, date_fim))

                # 4. Apaga os que não foram enviados
                for p in periodos_existentes:
                    if (p.inicio, p.fim) not in periodos_recebidos_set:
                        p.delete()

                # 5. Cria os novos
                for inicio, fim in periodos_recebidos_info:
                    if (inicio, fim) not in periodos_existentes_set:
                        EdPessoaVagaCampoDateboxPeriodo.objects.create(
                            ed_pessoa_vaga_campo_datebox=ed_pessoa_vaga_campo_datebox_obj,
                            inicio=inicio,
                            fim=fim,
                        )

                # 6. Pontuação acumulada
                pontuacao_total_por_datebox = sum(
                    int(
                        (fim - inicio).days / datebox_obj.multiplicador_fracao_pontuacao
                    )
                    * datebox_obj.fracao_pontuacao
                    for inicio, fim in periodos_recebidos_info
                )

                pontuacao_candidato += min(
                    pontuacao_total_por_datebox, datebox_obj.pontuacao_maxima
                )

            except Exception as e:
                return Response(
                    {"detail": f"{ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX}: {e}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Pode haver campos marcados anteriormente, entao apaga o que o usuario quer desmarcar
        lista_de_checkboxes_marcados_pela_pessoa = list(
            ed_pessoa_vaga_campos["checkboxes"].values_list(
                "ed_vaga_campo_checkbox_id", flat=True
            )
        )
        checkboxes_nao_marcados_agora = list(
            set(lista_de_checkboxes_marcados_pela_pessoa)
            - set(array_temporario_id_checkbox_vaga)
        )
        EdPessoaVagaCampoCheckboxUpload.objects.filter(
            ed_pessoa_vaga_campo_checkbox__cm_pessoa=request.candidato,
            ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox_id__in=checkboxes_nao_marcados_agora,
        ).delete()
        EdPessoaVagaCampoCheckbox.objects.filter(
            cm_pessoa=request.candidato,
            ed_vaga_campo_checkbox_id__in=checkboxes_nao_marcados_agora,
        ).delete()

        lista_de_comboboxes_marcados_pela_pessoa = list(
            ed_pessoa_vaga_campos["comboboxes"].values_list(
                "ed_vaga_campo_combobox_id", flat=True
            )
        )
        comboboxes_nao_marcados_agora = list(
            set(lista_de_comboboxes_marcados_pela_pessoa)
            - set(array_temporario_id_combobox_vaga)
        )
        EdPessoaVagaCampoComboboxUpload.objects.filter(
            ed_pessoa_vaga_campo_combobox__cm_pessoa=request.candidato,
            ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox_id__in=comboboxes_nao_marcados_agora,
        ).delete()
        EdPessoaVagaCampoCombobox.objects.filter(
            cm_pessoa=request.candidato,
            ed_vaga_campo_combobox_id__in=comboboxes_nao_marcados_agora,
        ).delete()

        lista_de_dateboxes_marcados_pela_pessoa = list(
            ed_pessoa_vaga_campos["dateboxes"].values_list(
                "ed_vaga_campo_datebox_id", flat=True
            )
        )
        array_temporario_id_datebox_vaga = list(
            map(int, request.data.get("datebox_da_vaga", {}).keys())
        )
        dateboxes_nao_marcados_agora = list(
            set(lista_de_dateboxes_marcados_pela_pessoa)
            - set(array_temporario_id_datebox_vaga)
        )
        EdPessoaVagaCampoDateboxUpload.objects.filter(
            ed_pessoa_vaga_campo_datebox__cm_pessoa=request.candidato,
            ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox_id__in=dateboxes_nao_marcados_agora,
        ).delete()
        EdPessoaVagaCampoDateboxPeriodo.objects.filter(
            ed_pessoa_vaga_campo_datebox__cm_pessoa=request.candidato,
            ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox_id__in=dateboxes_nao_marcados_agora,
        ).delete()
        EdPessoaVagaCampoDatebox.objects.filter(
            cm_pessoa=request.candidato,
            ed_vaga_campo_datebox_id__in=dateboxes_nao_marcados_agora,
        ).delete()

        request.session["pontuacao"] = pontuacao_candidato
        request.session["pontuacao_hash"] = gerar_hash(pontuacao_candidato)

        return Response(
            {"detail": OK_ED_PESSOA_VAGA_CAMPOS}, status=status.HTTP_201_CREATED
        )


@extend_schema(**DOCS_BAIXAR_ARQUIVO_INSCRICAO_VIEW)
class BaixarArquivoInscricaoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    def get(self, request):
        caminho_relativo = request.GET.get("caminho")

        if not caminho_relativo:
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_404_NOT_FOUND
            )

        # Verificar se o arquivo pertence ao candidato e vaga corretos
        # Extrair candidato_id e vaga_id do caminho
        try:
            # Formato esperado: "candidato_id_vaga_id/nome_arquivo.ext"
            pasta_candidato_vaga = caminho_relativo.split("/")[0]
            candidato_id_str, vaga_id_str = pasta_candidato_vaga.split("_")
            candidato_id_arquivo = int(candidato_id_str)
            vaga_id_arquivo = int(vaga_id_str)
        except (ValueError, IndexError):
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_403_FORBIDDEN
            )

        # Verificar se os IDs do arquivo correspondem aos da sessão
        if candidato_id_arquivo != request.candidato.id:
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_403_FORBIDDEN
            )

        if vaga_id_arquivo != request.vaga.id:
            return Response(
                {"detail": ERRO_GET_ARQUIVO}, status=status.HTTP_403_FORBIDDEN
            )

        raiz = Path(RAIZ_ARQUIVOS_UPLOAD).resolve()
        caminho_absoluto = (raiz / caminho_relativo).resolve()

        # Segurança - verificar se o arquivo está dentro da pasta permitida
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
            f'inline; filename="{os.path.basename(caminho_absoluto.name)}"'
        )
        return response


@extend_schema(**DOCS_ANEXAR_ARQUIVOS_VIEW)
class AnexarArquivosView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})
        if "pontuacao" not in request.session:
            raise ValidationError({"detail": ERRO_PONTUACAO_NA_SESSAO})
        if "pontuacao_hash" not in request.session:
            raise ValidationError({"detail": ERRO_PONTUACAOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["pontuacao_hash"] != gerar_hash(
            request.session["pontuacao"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato

    # Associa os campos marcados com o arquivo que o candidato subiu,
    # se houver, considerando que a inscricao pode ser editada
    def get(self, request):
        # Checkbox
        checkboxes_da_pessoa = EdPessoaVagaCampoCheckbox.objects.filter(
            cm_pessoa=request.candidato, ed_vaga_campo_checkbox__ed_vaga=request.vaga
        )

        checkboxes = []
        for checkbox_da_pessoa in checkboxes_da_pessoa:
            checkbox_da_pessoa_com_upload = (
                EdPessoaVagaCampoCheckboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_checkbox=checkbox_da_pessoa
                ).first()
            )

            checkboxes.append(
                {
                    "ed_vaga_campo_checkbox_id": checkbox_da_pessoa.ed_vaga_campo_checkbox.id,
                    "nome_campo": checkbox_da_pessoa.ed_vaga_campo_checkbox.ed_campo.descricao,
                    "arquivo": (
                        checkbox_da_pessoa_com_upload.caminho_arquivo
                        if checkbox_da_pessoa_com_upload
                        else None
                    ),
                }
            )

        # Combobox
        comboboxes_da_pessoa = EdPessoaVagaCampoCombobox.objects.filter(
            cm_pessoa=request.candidato, ed_vaga_campo_combobox__ed_vaga=request.vaga
        )
        comboboxes = []
        for combobox_da_pessoa in comboboxes_da_pessoa:
            combobox_da_pessoa_com_upload = (
                EdPessoaVagaCampoComboboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_combobox=combobox_da_pessoa
                ).first()
            )
            comboboxes.append(
                {
                    "ed_vaga_campo_combobox_id": combobox_da_pessoa.ed_vaga_campo_combobox.id,
                    "nome_campo": combobox_da_pessoa.ed_vaga_campo_combobox.ed_campo.descricao,
                    "arquivo": (
                        combobox_da_pessoa_com_upload.caminho_arquivo
                        if combobox_da_pessoa_com_upload
                        else None
                    ),
                }
            )

        # Datebox
        dateboxes_da_pessoa = EdPessoaVagaCampoDatebox.objects.filter(
            cm_pessoa=request.candidato, ed_vaga_campo_datebox__ed_vaga=request.vaga
        ).prefetch_related("periodos")

        dateboxes = []
        for datebox_da_pessoa in dateboxes_da_pessoa:
            datebox_da_pessoa_com_upload = (
                EdPessoaVagaCampoDateboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_datebox=datebox_da_pessoa
                ).first()
            )

            periodos = list(datebox_da_pessoa.periodos.values("inicio", "fim"))

            dateboxes.append(
                {
                    "ed_vaga_campo_datebox_id": datebox_da_pessoa.ed_vaga_campo_datebox.id,
                    "nome_campo": datebox_da_pessoa.ed_vaga_campo_datebox.ed_campo.descricao,
                    "periodos": periodos,
                    "arquivo": (
                        datebox_da_pessoa_com_upload.caminho_arquivo
                        if datebox_da_pessoa_com_upload
                        else None
                    ),
                }
            )

        response_data = {}
        if checkboxes:
            response_data["checkboxes"] = checkboxes
        if comboboxes:
            response_data["comboboxes"] = comboboxes
        if dateboxes:
            response_data["dateboxes"] = dateboxes

        if not response_data:
            return Response(
                {"detail": ERRO_GET_CAMPOS_DA_VAGA}, status=status.HTTP_204_NO_CONTENT
            )

        return Response(response_data, status=status.HTTP_200_OK)

    # A pessoa pode editar a inscricao, logo, preciso saber quais campos foram
    # deixados sem marcar na tela anterior para envio
    # Se foi deixado de marcar um campo, o arquivo correspondente deve ser
    # apagado, porque a marcacao do campo ja foi embora em PessoaVagaCampoView.post
    def post(self, request):
        # Campos selecionados pelo candidato
        ed_pessoa_vaga_campos = get_ed_pessoa_vaga_campos(request)
        campos_selecionados_ids = {"checkbox": [], "combobox": [], "datebox": []}

        # Obtendo os IDs dos campos selecionados
        for checkbox in ed_pessoa_vaga_campos["checkboxes"]:
            campos_selecionados_ids["checkbox"].append(
                checkbox.ed_vaga_campo_checkbox.id
            )
        for combobox in ed_pessoa_vaga_campos["comboboxes"]:
            campos_selecionados_ids["combobox"].append(
                combobox.ed_vaga_campo_combobox.id
            )
        for datebox in ed_pessoa_vaga_campos["dateboxes"]:
            campos_selecionados_ids["datebox"].append(datebox.ed_vaga_campo_datebox.id)

        # Atualizar ou criar arquivos para campos reenviados
        for campo_tipo_arquivo, arquivo in request.FILES.items():
            try:
                campo_tipo, campo_id_str = campo_tipo_arquivo.split("_")
                campo_id = int(campo_id_str)

                if campo_tipo not in ["checkbox", "combobox", "datebox"]:
                    raise ValueError(ERRO_TIPO_CAMPO_INVALIDO)

                # Validar qual o tipo de campo e buscar a associacao do arquivo enviado com o campo na base de dados
                if campo_id in campos_selecionados_ids[campo_tipo]:
                    if campo_tipo == "checkbox":
                        ed_campo = EdPessoaVagaCampoCheckbox.objects.get(
                            ed_vaga_campo_checkbox_id=campo_id,
                            cm_pessoa=request.candidato,
                        )
                        descricao_campo = (
                            ed_campo.ed_vaga_campo_checkbox.ed_campo.descricao
                        )
                    elif campo_tipo == "combobox":
                        ed_campo = EdPessoaVagaCampoCombobox.objects.get(
                            ed_vaga_campo_combobox_id=campo_id,
                            cm_pessoa=request.candidato,
                        )
                        descricao_campo = (
                            ed_campo.ed_vaga_campo_combobox.ed_campo.descricao
                        )
                    elif campo_tipo == "datebox":
                        ed_campo = EdPessoaVagaCampoDatebox.objects.get(
                            ed_vaga_campo_datebox_id=campo_id,
                            cm_pessoa=request.candidato,
                        )
                        descricao_campo = (
                            ed_campo.ed_vaga_campo_datebox.ed_campo.descricao
                        )

                    # Monta a string do nome do arquivo e seu caminho relativo
                    caminho_relativo = os.path.join(
                        f"{request.candidato.id}_{request.vaga.id}",
                        cortar_nome_arquivo(
                            descricao_campo,
                            os.path.splitext(arquivo.name)[1].lower(),
                        ),
                    )
                    caminho = os.path.join(RAIZ_ARQUIVOS_UPLOAD, caminho_relativo)

                    # Salvar ou atualizar o arquivo correspondente ao campo
                    if campo_tipo == "checkbox":
                        EdPessoaVagaCampoCheckboxUpload.objects.update_or_create(
                            ed_pessoa_vaga_campo_checkbox=ed_campo,
                            defaults={
                                "caminho_arquivo": caminho_relativo,
                                "validado": False,
                            },
                        )
                    elif campo_tipo == "combobox":
                        EdPessoaVagaCampoComboboxUpload.objects.update_or_create(
                            ed_pessoa_vaga_campo_combobox=ed_campo,
                            defaults={
                                "caminho_arquivo": caminho_relativo,
                                "validado": False,
                            },
                        )
                    elif campo_tipo == "datebox":
                        EdPessoaVagaCampoDateboxUpload.objects.update_or_create(
                            ed_pessoa_vaga_campo_datebox=ed_campo,
                            defaults={
                                "caminho_arquivo": caminho_relativo,
                                "validado": False,
                            },
                        )

                    # 🟢 Criar diretório antes de salvar
                    try:
                        os.makedirs(os.path.dirname(caminho), exist_ok=True)
                    except Exception as e:
                        return Response(
                            {"detail": f"{ERRO_CRIACAO_PASTA_UPLOAD}: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                    # 🔵 Primeiro, salva o arquivo fisicamente
                    try:
                        with open(caminho, "wb+") as destino:
                            for parte in arquivo.chunks():
                                destino.write(parte)
                    except Exception as e:
                        return Response(
                            {"detail": f"{ERRO_ARQUIVO_INVALIDO}: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                    # 🔴 Agora processamos o arquivo salvo
                    extensao = os.path.splitext(arquivo.name)[1].lower()
                    extensoes_permitidas = [".pdf", ".jpg", ".jpeg", ".png"]

                    if extensao not in extensoes_permitidas:
                        return Response(
                            {"detail": ERRO_ARQUIVO_INVALIDO_TIPO_INVALIDO},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    requer_assinatura = False
                    if campo_tipo == "checkbox":
                        requer_assinatura = ed_campo.ed_vaga_campo_checkbox.assinado
                    elif campo_tipo == "combobox":
                        requer_assinatura = ed_campo.ed_vaga_campo_combobox.assinado
                    elif campo_tipo == "datebox":
                        requer_assinatura = ed_campo.ed_vaga_campo_datebox.assinado
                    if extensao in [".pdf"]:
                        if requer_assinatura:
                            if not verificar_assinatura_pdf(caminho):
                                if os.path.exists(caminho):
                                    os.remove(caminho)
                                return Response(
                                    {"detail": ERRO_VERIFICACAO_ASSINATURA_DIGITAL},
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                        else:
                            try:
                                comprimir_pdf(caminho, caminho)
                            except ValueError as e:
                                return Response(
                                    {"detail": str(e)},
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                    elif extensao in [".jpg", ".jpeg", ".png"]:
                        if requer_assinatura:
                            return Response(
                                {"detail": ERRO_VALIDACAO_ASSINATURA_DIGITAL_PDF},
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        try:
                            with open(caminho, "rb") as f:
                                tipo_imagem = imghdr.what(f)
                            if tipo_imagem in ["jpeg", "png"]:
                                redimensionar_imagem(caminho, caminho)
                            else:
                                return Response(
                                    {"detail": ERRO_ARQUIVO_INVALIDO},
                                    status=status.HTTP_400_BAD_REQUEST,
                                )
                        except Exception as e:
                            return Response(
                                {"detail": f"{ERRO_ARQUIVO_INVALIDO}: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            )
            except (IndexError, ValueError, EdCampo.DoesNotExist) as e:
                return Response(
                    {"detail": f"{ERRO_ARQUIVO_INVALIDO}: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"detail": f"{ERRO_POST_ARQUIVOS}: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        ## Segunda parte: excluir arquivos orfaos
        # Obter todos os arquivos atualmente relacionados no banco de dados apos a atualizacao
        arquivos_atuais = {
            "checkbox": list(
                EdPessoaVagaCampoCheckboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_checkbox__cm_pessoa=request.candidato,
                    ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga=request.vaga,
                ).values_list("caminho_arquivo", flat=True)
            ),
            "combobox": list(
                EdPessoaVagaCampoComboboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_combobox__cm_pessoa=request.candidato,
                    ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga=request.vaga,
                ).values_list("caminho_arquivo", flat=True)
            ),
            "datebox": list(
                EdPessoaVagaCampoDateboxUpload.objects.filter(
                    ed_pessoa_vaga_campo_datebox__cm_pessoa=request.candidato,
                    ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga=request.vaga,
                ).values_list("caminho_arquivo", flat=True)
            ),
        }

        # Listar todos os arquivos no diretorio de uploads do candidato
        diretorio_candidato = os.path.join(
            RAIZ_ARQUIVOS_UPLOAD, f"{request.candidato.id}_{request.vaga.id}"
        )
        arquivos_no_disco = []
        if os.path.exists(diretorio_candidato):
            arquivos_no_disco = [
                os.path.join(diretorio_candidato, f)
                for f in os.listdir(diretorio_candidato)
            ]

        # Comparar os arquivos no disco com os arquivos no banco de dados e remover os órfãos
        arquivos_atuais_no_disco = [
            os.path.join(RAIZ_ARQUIVOS_UPLOAD, arquivo)
            for tipo in arquivos_atuais.values()
            for arquivo in tipo
        ]

        for arquivo_orfao in set(arquivos_no_disco) - set(arquivos_atuais_no_disco):
            os.remove(arquivo_orfao)

        return Response(
            {"detail": OK_ED_PESSOA_VAGA_CAMPO_UPLOAD}, status=status.HTTP_201_CREATED
        )


@extend_schema(**DOCS_FINALIZAR_INSCRICAO_VIEW)
class FinalizarInscricaoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "pontuacao" not in request.session:
            raise ValidationError({"detail": ERRO_PONTUACAO_NA_SESSAO})
        if "pontuacao_hash" not in request.session:
            raise ValidationError({"detail": ERRO_PONTUACAOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["pontuacao_hash"] != gerar_hash(
            request.session["pontuacao"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        if vaga.ed_edital.data_fim_inscricao < timezone.now():
            raise ValidationError({"detail": ERRO_INSCRICOES_ENCERRADAS})

        request.vaga = vaga
        request.candidato = candidato
        request.pontuacao = request.session["pontuacao"]

        ed_pessoa_vaga_campos = get_ed_pessoa_vaga_campos(request)

        arquivos_faltantes = []

        for checkbox_id in ed_pessoa_vaga_campos["checkboxes"].values_list(
            "ed_vaga_campo_checkbox__id", flat=True
        ):
            if not EdPessoaVagaCampoCheckboxUpload.objects.filter(
                ed_pessoa_vaga_campo_checkbox__cm_pessoa=candidato,
                ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga=vaga,
                ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__id=checkbox_id,
            ).exists():
                arquivos_faltantes.append(f"checkbox_{checkbox_id}")

        for combobox_id in ed_pessoa_vaga_campos["comboboxes"].values_list(
            "ed_vaga_campo_combobox__id", flat=True
        ):
            if not EdPessoaVagaCampoComboboxUpload.objects.filter(
                ed_pessoa_vaga_campo_combobox__cm_pessoa=candidato,
                ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga=vaga,
                ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__id=combobox_id,
            ).exists():
                arquivos_faltantes.append(f"combobox_{combobox_id}")

        for datebox_id in ed_pessoa_vaga_campos["dateboxes"].values_list(
            "ed_vaga_campo_datebox__id", flat=True
        ):
            if not EdPessoaVagaCampoDateboxUpload.objects.filter(
                ed_pessoa_vaga_campo_datebox__cm_pessoa=candidato,
                ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga=vaga,
                ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__id=datebox_id,
            ).exists():
                arquivos_faltantes.append(f"datebox_{datebox_id}")

        # Garante, por segurança, que tem pelo menos um período preenchido
        for datebox in ed_pessoa_vaga_campos["dateboxes"]:
            if not EdPessoaVagaCampoDateboxPeriodo.objects.filter(
                ed_pessoa_vaga_campo_datebox=datebox,
                inicio__isnull=False,
                fim__isnull=False,
            ).exists():
                arquivos_faltantes.append(f"datebox_{datebox.ed_vaga_campo_datebox.id}")

        if arquivos_faltantes:
            raise ValidationError(
                {"detail": f"{ERRO_FALTA_ARQUIVO}: {arquivos_faltantes}"}
            )

    def get(self, request):
        # request.session["inscricao_concorrente"] existe apenas se edital nao permite multiplas inscricoes
        if "inscricao_concorrente" in request.session:
            # Entao verifica se a inscricao de fato ainda existe na base
            inscricao_no_edital_ja_salva = EdPessoaVagaInscricao.objects.filter(
                cm_pessoa_id=request.candidato.id,
                ed_vaga__ed_edital=request.vaga.ed_edital,
            ).exists()

            if inscricao_no_edital_ja_salva:
                apaga_outra_inscricao_no_mesmo_edital(
                    request.candidato.id, request.session["inscricao_concorrente"]
                )

            del request.session["inscricao_concorrente"]
            del request.session["inscricao_concorrente_hash"]

        try:
            pontuacao = getattr(request, "pontuacao", None)
            if not pontuacao or pontuacao == 0:
                pontuacao = None

            inscricao, created = EdPessoaVagaInscricao.objects.update_or_create(
                cm_pessoa=request.candidato,
                ed_vaga=request.vaga,
                defaults={"pontuacao": pontuacao, "data": timezone.now()},
            )
            del request.session["pontuacao"]
            request.session["inscricao_id"] = inscricao.id
            request.session["inscricao_id_hash"] = gerar_hash(inscricao.id)

            if created:
                return Response(
                    {"sucesso": True, "detail": OK_INSERCAO_ED_PESSOA_INSCRICAO},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"sucesso": True, "detail": OK_ATUALIZACAO_ED_PESSOA_INSCRICAO},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {
                    "sucesso": False,
                    "detail": f"{ERRO_INSERCAO_ED_PESSOA_VAGA_INSCRICAO}: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(**DOCS_GET_INSCRICAO_VIEW)
class GetInscricaoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "vaga_selecionada" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAID_NA_SESSAO})
        if "vaga_selecionada_hash" not in request.session:
            raise ValidationError({"detail": ERRO_VAGAIDHASH_NA_SESSAO})
        if "candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATO_NA_SESSAO})
        if "candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CANDIDATOHASH_NA_SESSAO})
        if "codigo_candidato" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATO_NA_SESSAO})
        if "codigo_candidato_hash" not in request.session:
            raise ValidationError({"detail": ERRO_CODIGOCANDIDATOHASH_NA_SESSAO})
        if "inscricao_id" not in request.session:
            raise ValidationError({"detail": ERRO_INSCRICAO_NA_SESSAO})
        if "inscricao_id_hash" not in request.session:
            raise ValidationError({"detail": ERRO_INSCRICAOHASH_NA_SESSAO})

        if request.session["vaga_selecionada_hash"] != gerar_hash(
            request.session["vaga_selecionada"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["candidato_hash"] != gerar_hash(
            request.session["candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["inscricao_id_hash"] != gerar_hash(
            request.session["inscricao_id"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["codigo_candidato_hash"] != gerar_hash(
            request.session["codigo_candidato"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            vaga = EdVaga.objects.get(id=request.session["vaga_selecionada"])
        except EdVaga.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_VAGA})
        try:
            candidato = CmPessoa.objects.get(id=request.session["candidato"])
        except CmPessoa.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_CANDIDATO})
        try:
            inscricao = EdPessoaVagaInscricao.objects.get(
                id=request.session["inscricao_id"]
            )
        except EdPessoaVagaInscricao.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_INSCRICAO})

        request.vaga = vaga
        request.candidato = candidato
        request.inscricao = inscricao

    def get(self, request):
        context = {
            "pessoa_nome": request.candidato.nome,
            "edital": str(EdEdital.objects.get(id=request.vaga.ed_edital.id)),
            "vaga_nome": request.vaga.descricao,
            "inscricao": {
                "id": request.inscricao.id,
                "pontuacao": request.inscricao.pontuacao,
                "data": request.inscricao.data,
                "assinatura": request.inscricao.codigo_pessoavagainscricao(),
            },
        }

        arquivos_do_candidato = []

        checkbox_uploads = EdPessoaVagaCampoCheckboxUpload.objects.filter(
            ed_pessoa_vaga_campo_checkbox__cm_pessoa=request.candidato,
            ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_vaga=request.vaga,
        ).select_related(
            "ed_pessoa_vaga_campo_checkbox__ed_vaga_campo_checkbox__ed_campo"
        )
        for upload in checkbox_uploads:
            arquivos_do_candidato.append(
                upload.ed_pessoa_vaga_campo_checkbox.ed_vaga_campo_checkbox.ed_campo.descricao
            )

        combobox_uploads = EdPessoaVagaCampoComboboxUpload.objects.filter(
            ed_pessoa_vaga_campo_combobox__cm_pessoa=request.candidato,
            ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_vaga=request.vaga,
        ).select_related(
            "ed_pessoa_vaga_campo_combobox__ed_vaga_campo_combobox__ed_campo"
        )
        for upload in combobox_uploads:
            arquivos_do_candidato.append(
                upload.ed_pessoa_vaga_campo_combobox.ed_vaga_campo_combobox.ed_campo.descricao
            )

        datebox_uploads = EdPessoaVagaCampoDateboxUpload.objects.filter(
            ed_pessoa_vaga_campo_datebox__cm_pessoa=request.candidato,
            ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_vaga=request.vaga,
        ).select_related(
            "ed_pessoa_vaga_campo_datebox__ed_vaga_campo_datebox__ed_campo"
        )
        for upload in datebox_uploads:
            arquivos_do_candidato.append(
                upload.ed_pessoa_vaga_campo_datebox.ed_vaga_campo_datebox.ed_campo.descricao
            )

        context["arquivos_do_candidato"] = arquivos_do_candidato
        request.session.flush()

        return Response(context, status=status.HTTP_200_OK)
