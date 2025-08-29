import os
from datetime import date

import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from cead.messages import ERRO_GET_PESSOA_VAGA_VALIDACAO, ERRO_SESSAO_INVALIDA
from cead.models import (
    CmMunicipio,
    CmPessoaBanco,
    CmPessoaEndereco,
    CmPessoaTelefone,
    CmUf,
    EdPessoaVagaGerouFicha,
    EdPessoaVagaValidacao,
    FiEditalFuncaoOferta,
    FiFuncaoBolsistaDeclaracao,
    FiPessoaFicha,
)
from cead.serializers import (
    AcCursoOfertaIdDescricaoSerializer,
    CPFSerializer,
)
from cead.settings import STATIC_ROOT
from cead.utils import gerar_hash, remove_caracteres_especiais

from .api_docs import *
from .messages import *
from .serializers import (
    CmMunicipioIdSerializer,
    CmPessoaBancoGetSerializer,
    CmPessoaBancoPostSerializer,
    CmPessoaEnderecoGetSerializer,
    CmPessoaEnderecoPostSerializer,
    CmPessoaNomeCpfFormatadoEmailGetSerializer,
    CmPessoaTelefoneGetSerializer,
    CmPessoaTelefonePostSerializer,
    FiFuncaoBolsistaGetSerializer,
    FiPessoaFichaGetSerializer,
    FiPessoaFichaPostSerializer,
)


@extend_schema(**DOCS_LISTAR_MUNICIPIOS_VIEW)
class ListarMunicipiosAPIView(APIView):
    def get(self, request):
        search_term = request.query_params.get("search", "").strip()
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        if not search_term:
            return Response(
                {"detail": ERRO_INFORME_TERMO_BUSCA_SEARCH},
                status=status.HTTP_400_BAD_REQUEST,
            )

        municipios_query = (
            CmMunicipio.objects.filter(municipio__icontains=search_term)
            .select_related("cm_uf")
            .order_by("municipio")
        )

        total_count = municipios_query.count()
        start = (page - 1) * page_size
        end = start + page_size
        municipios_page = municipios_query[start:end]

        serializer = CmMunicipioIdSerializer(municipios_page, many=True)

        return Response(
            {
                "results": serializer.data,
                "count": total_count,
                "page": page,
                "total_pages": (total_count + page_size - 1) // page_size,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_CPF_CODIGO_PESSOA_VALIDACAO_VIEW)
class CPFCodigoPessoaValidacaoView(APIView):
    def post(self, request, codigo):
        serializer = CPFSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ed_pessoa_vaga_validacao = EdPessoaVagaValidacao.validar_codigo_pelo_cpf(
                serializer.validated_data["cpf"], codigo
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        associacao_edital_funcao_oferta_id = (
            FiEditalFuncaoOferta.objects.filter(
                ed_edital=ed_pessoa_vaga_validacao.ed_vaga.ed_edital
            )
            .order_by("-id")
            .values_list("id", flat=True)
            .first()
            # Obtem o ultimo porque o sistema antigo permitia
            # erroneamente mais de uma associacao
        )

        if not associacao_edital_funcao_oferta_id:
            return Response(
                {"detail": ERRO_GET_FI_EDITAL_FUNCAO_OFERTA},
                status=status.HTTP_404_NOT_FOUND,
            )

        request.session["ed_pessoa_vaga_validacao_id"] = ed_pessoa_vaga_validacao.id
        request.session["ed_pessoa_vaga_validacao_id_hash"] = gerar_hash(
            ed_pessoa_vaga_validacao.id
        )
        request.session["associacao_edital_funcao_oferta_id"] = (
            associacao_edital_funcao_oferta_id
        )
        request.session["associacao_edital_funcao_oferta_id_hash"] = gerar_hash(
            associacao_edital_funcao_oferta_id
        )

        return Response(
            {"detail": OK_CPF_HASH_VALIDADO}, status=status.HTTP_201_CREATED
        )


@extend_schema(**DOCS_CADASTRO_ENDERECO_TELEFONE_BANCO_VIEW)
class CadastroEnderecoTelefoneBancoView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "ed_pessoa_vaga_validacao_id" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID})
        if "ed_pessoa_vaga_validacao_id_hash" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID_HASH}
            )
        if "associacao_edital_funcao_oferta_id" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID}
            )
        if "associacao_edital_funcao_oferta_id_hash" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID_HASH}
            )

        if request.session["ed_pessoa_vaga_validacao_id_hash"] != gerar_hash(
            request.session["ed_pessoa_vaga_validacao_id"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["associacao_edital_funcao_oferta_id_hash"] != gerar_hash(
            request.session["associacao_edital_funcao_oferta_id"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            ed_pessoa_vaga_validacao = EdPessoaVagaValidacao.objects.get(
                id=request.session["ed_pessoa_vaga_validacao_id"]
            )
        except EdPessoaVagaValidacao.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_PESSOA_VAGA_VALIDACAO})

        request.ed_pessoa_vaga_validacao = ed_pessoa_vaga_validacao

    def get(self, request):
        cm_pessoa = request.ed_pessoa_vaga_validacao.cm_pessoa

        endereco_obj = CmPessoaEndereco.objects.filter(cm_pessoa=cm_pessoa).first()
        banco_obj = CmPessoaBanco.objects.filter(cm_pessoa=cm_pessoa).first()

        data = {
            "endereco": (
                CmPessoaEnderecoGetSerializer(endereco_obj).data
                if endereco_obj
                else None
            ),
            "telefones": CmPessoaTelefoneGetSerializer(
                CmPessoaTelefone.objects.filter(cm_pessoa=cm_pessoa), many=True
            ).data,
            "banco": CmPessoaBancoGetSerializer(banco_obj).data if banco_obj else None,
        }

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        cm_pessoa = request.ed_pessoa_vaga_validacao.cm_pessoa

        endereco_data = request.data.get("endereco", {})
        cm_municipio_data = endereco_data.pop("cm_municipio", {})
        cm_uf_data = cm_municipio_data.pop("cm_uf", {})

        try:
            cm_uf = CmUf.objects.get(sigla=cm_uf_data["sigla"])
            cm_municipio = CmMunicipio.objects.get(
                municipio=cm_municipio_data["municipio"], cm_uf=cm_uf
            )
        except CmUf.DoesNotExist:
            return Response(
                {"detail": ERRO_UF_INVALIDA, "field": "endereco.cm_uf.sigla"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except CmMunicipio.DoesNotExist:
            return Response(
                {
                    "detail": ERRO_MUNICIPIO_INVALIDO,
                    "field": "endereco.cm_municipio.municipio",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        endereco_serializer = CmPessoaEnderecoPostSerializer(
            data=endereco_data, context={"cm_pessoa": cm_pessoa}
        )
        if not endereco_serializer.is_valid():
            return Response(
                {"errors": endereco_serializer.errors, "section": "endereco"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        telefones_data = request.data.get("telefones", [])
        telefone_serializer = CmPessoaTelefonePostSerializer(
            data=telefones_data, many=True, context={"cm_pessoa": cm_pessoa}
        )
        if not telefone_serializer.is_valid():
            return Response(
                {"errors": telefone_serializer.errors, "section": "telefones"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        banco_data = request.data.get("banco", {})
        banco_serializer = CmPessoaBancoPostSerializer(
            data=banco_data, context={"cm_pessoa": cm_pessoa}
        )
        if not banco_serializer.is_valid():
            return Response(
                {"errors": banco_serializer.errors, "section": "banco"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            CmPessoaEndereco.objects.update_or_create(
                cm_pessoa=cm_pessoa,
                defaults={
                    **endereco_serializer.validated_data,
                    "cm_municipio": cm_municipio,
                },
            )

            CmPessoaTelefone.objects.filter(cm_pessoa=cm_pessoa).delete()
            CmPessoaTelefone.objects.bulk_create(
                [
                    CmPessoaTelefone(cm_pessoa=cm_pessoa, **telefone_data)
                    for telefone_data in telefone_serializer.validated_data
                ]
            )

            CmPessoaBanco.objects.update_or_create(
                cm_pessoa=cm_pessoa, defaults={**banco_serializer.validated_data}
            )

        except Exception as e:
            return Response(
                {"detail": ERRO_CREATE_DADOS_PESSOAIS, "debug": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"success": OK_SALVOU_ENDERECO_TELEFONE_DADOS_BANCARIOS},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(**DOCS_CADASTRO_FI_PESSOA_FICHA_APIVIEW)
class CadastroFiPessoaFichaAPIView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "ed_pessoa_vaga_validacao_id" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID})
        if "ed_pessoa_vaga_validacao_id_hash" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID_HASH}
            )
        if "associacao_edital_funcao_oferta_id" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID}
            )
        if "associacao_edital_funcao_oferta_id_hash" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID_HASH}
            )
        if request.session["ed_pessoa_vaga_validacao_id_hash"] != gerar_hash(
            request.session["ed_pessoa_vaga_validacao_id"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["associacao_edital_funcao_oferta_id_hash"] != gerar_hash(
            request.session["associacao_edital_funcao_oferta_id"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            ed_pessoa_vaga_validacao = EdPessoaVagaValidacao.objects.get(
                id=request.session["ed_pessoa_vaga_validacao_id"]
            )
        except EdPessoaVagaValidacao.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_PESSOA_VAGA_VALIDACAO})

        try:
            associacao_edital_funcao_oferta = FiEditalFuncaoOferta.objects.get(
                id=request.session["associacao_edital_funcao_oferta_id"]
            )
        except FiEditalFuncaoOferta.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_FI_EDITAL_FUNCAO_OFERTA})

        request.ed_pessoa_vaga_validacao = ed_pessoa_vaga_validacao
        request.associacao_edital_funcao_oferta = associacao_edital_funcao_oferta

    def get(self, request):
        ed_edital = request.ed_pessoa_vaga_validacao.ed_vaga.ed_edital
        associacao_edital_funcao_oferta = request.associacao_edital_funcao_oferta

        # Editais para coordenadores nao sao associados com oferta
        ac_curso_oferta_data = (
            AcCursoOfertaIdDescricaoSerializer(
                associacao_edital_funcao_oferta.ac_curso_oferta
            ).data
            if associacao_edital_funcao_oferta.ac_curso_oferta_id is not None
            else None
        )
        fi_funcao_bolsista_serializer = FiFuncaoBolsistaGetSerializer(
            associacao_edital_funcao_oferta.fi_funcao_bolsista
        )
        fi_ficha_serializer = FiPessoaFichaGetSerializer(
            FiPessoaFicha.objects.filter(
                cm_pessoa=request.ed_pessoa_vaga_validacao.cm_pessoa
            ).last()
        )

        return Response(
            {
                "cm_pessoa__nome_display": request.ed_pessoa_vaga_validacao.cm_pessoa.nome,
                "ed_edital__numero_ano_edital_display": (
                    f"Edital {ed_edital.numero_ano_edital()} - {ed_edital.descricao}"
                ),
                "ac_curso_oferta": ac_curso_oferta_data,
                "fi_funcao_bolsista": fi_funcao_bolsista_serializer.data,
                "fi_ficha": fi_ficha_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        cm_pessoa = request.ed_pessoa_vaga_validacao.cm_pessoa
        ed_edital = request.ed_pessoa_vaga_validacao.ed_vaga.ed_edital

        serializer = FiPessoaFichaPostSerializer(
            data=request.data,
            context={"ed_pessoa_vaga_validacao": request.ed_pessoa_vaga_validacao},
        )
        if serializer.is_valid():
            serializer.save(cm_pessoa=cm_pessoa, ed_edital=ed_edital)
            return Response({"detail": OK_FICHA_SALVA}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**DOCS_GERAR_FICHA_PDF_APIVIEW)
class GerarFichaPDFAPIView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        if "ed_pessoa_vaga_validacao_id" not in request.session:
            raise ValidationError({"detail": ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID})
        if "ed_pessoa_vaga_validacao_id_hash" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID_HASH}
            )
        if "associacao_edital_funcao_oferta_id" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID}
            )
        if "associacao_edital_funcao_oferta_id_hash" not in request.session:
            raise ValidationError(
                {"detail": ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID_HASH}
            )

        if request.session["ed_pessoa_vaga_validacao_id_hash"] != gerar_hash(
            request.session["ed_pessoa_vaga_validacao_id"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})
        if request.session["associacao_edital_funcao_oferta_id_hash"] != gerar_hash(
            request.session["associacao_edital_funcao_oferta_id"]
        ):
            raise ValidationError({"detail": ERRO_SESSAO_INVALIDA})

        try:
            ed_pessoa_vaga_validacao = EdPessoaVagaValidacao.objects.get(
                id=request.session["ed_pessoa_vaga_validacao_id"]
            )
        except EdPessoaVagaValidacao.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_PESSOA_VAGA_VALIDACAO})

        try:
            associacao_edital_funcao_oferta = (
                FiEditalFuncaoOferta.objects.select_related(
                    "ed_edital",
                    "fi_funcao_bolsista",
                    "ac_curso_oferta__ac_curso__ac_curso_tipo",
                ).get(id=request.session["associacao_edital_funcao_oferta_id"])
            )
        except FiEditalFuncaoOferta.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_FI_EDITAL_FUNCAO_OFERTA})

        request.session.flush()
        request.ed_pessoa_vaga_validacao = ed_pessoa_vaga_validacao
        request.associacao_edital_funcao_oferta = associacao_edital_funcao_oferta

    def get(self, request):
        associacao_edital_funcao_oferta = request.associacao_edital_funcao_oferta
        ed_pessoa_vaga_validacao = request.ed_pessoa_vaga_validacao
        cm_pessoa = request.ed_pessoa_vaga_validacao.cm_pessoa
        ed_edital = ed_pessoa_vaga_validacao.ed_vaga.ed_edital

        fi_pessoa_ficha_serializer = FiPessoaFichaGetSerializer(
            FiPessoaFicha.objects.filter(cm_pessoa=cm_pessoa).last()
        )
        cm_pessoa_banco = CmPessoaBanco.objects.get(cm_pessoa=cm_pessoa)

        cm_pessoa_serializer = CmPessoaNomeCpfFormatadoEmailGetSerializer(cm_pessoa)
        cm_pessoa_endereco_serializer = CmPessoaEnderecoGetSerializer(
            CmPessoaEndereco.objects.get(cm_pessoa=cm_pessoa)
        )
        cm_pessoa_banco_serializer = CmPessoaBancoGetSerializer(cm_pessoa_banco)
        telefone_serializer = CmPessoaTelefoneGetSerializer(
            CmPessoaTelefone.objects.filter(cm_pessoa=cm_pessoa)[:2], many=True
        )

        # Resolve a associacao curso e tipo de curso a ficha
        # Nem sempre a ficha possui esses dados, ex.: coordenadoria geral
        oferta = associacao_edital_funcao_oferta.ac_curso_oferta
        ac_curso = (
            getattr(getattr(oferta, "ac_curso", None), "nome", None) if oferta else None
        )
        ac_curso_tipo = (
            getattr(
                getattr(getattr(oferta, "ac_curso", None), "ac_curso_tipo", None),
                "nome",
                None,
            )
            if oferta
            else None
        )

        ficha = {
            "ac_curso": ac_curso,
            "ac_curso_tipo": ac_curso_tipo,
            "cm_pessoa": cm_pessoa_serializer.data,
            "cm_pessoa_banco": cm_pessoa_banco_serializer.data,
            "cm_pessoa_endereco": cm_pessoa_endereco_serializer.data,
            "telefones": telefone_serializer.data,
            "ed_edital": ed_edital.numero_ano_edital(),
            "fi_pessoa_ficha": fi_pessoa_ficha_serializer.data,
            # DTL aceita so objetos date para converter na pagina
            "data_nascimento": date.fromisoformat(
                fi_pessoa_ficha_serializer.data["data_nascimento"]
            ),
            "data_emissao_documento": date.fromisoformat(
                fi_pessoa_ficha_serializer.data["data_emissao"]
            ),
            "hoje": date.today(),
            "itens_declaracao": list(
                FiFuncaoBolsistaDeclaracao.objects.filter(
                    fi_funcao_bolsista=fi_pessoa_ficha_serializer.instance.fi_funcao_bolsista
                )
                .order_by("id")
                .values_list(
                    "item_declaracao", flat=True
                )  # Importante a ordem em que foi cadastrado
            ),
            "ficha_static_images_dir": os.path.join(STATIC_ROOT, "ficha", "imagens"),
        }

        html_string = render_to_string("gera_ficha.html", ficha)

        options = {
            "page-size": "A4",
            "margin-right": "0mm",
            "margin-left": "0mm",
            "enable-local-file-access": "",
            "disable-smart-shrinking": "",
            "zoom": "0.9",
        }
        pdf = pdfkit.from_string(html_string, False, options=options)

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="ficha_{remove_caracteres_especiais(cm_pessoa_serializer.data.get("nome"))}.pdf"'
        )
        response["Access-Control-Expose-Headers"] = (
            "Content-Disposition"  # Para o front pegar o nome do arquivo
        )
        return response
