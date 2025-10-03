from drf_spectacular.utils import extend_schema

from django.db import transaction, IntegrityError
from django.db.models import OuterRef, Q, Prefetch, Subquery
from django.utils.timezone import now

from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cead.models import (
    AcCurso,
    AcCursoOferta,
    EdEdital,
    FiEditalFuncaoOferta,
    FiFuncaoBolsista,
    FiPessoaFicha,
)

from .api_docs import *
from .messages import *
from .permissions import (
    IsAssociadorEditalFuncaoFichaOferta,
    IsGerenciadorVinculacaoFichas,
)
from cead.serializers import AcCursoIdNomeSerializer, AcCursoOfertaIdDescricaoSerializer
from .serializers import (
    AtualizarDataVinculoSerializer,
    BolsistaSerializer,
    CmPessoaComFichasSerializer,
    EdEditalSerializer,
    FiGetEditalFuncaoOfertaSerializer,
    FiPessoaFichaEdicaoFinanceiroSerializer,
    FiPostEditalFuncaoOfertaSerializer,
    ListarFuncoesComFichaUABSerializer,
)


class ListarEditaisAPIView(APIView):
    def get(self, request):
        editais = EdEdital.objects.all()
        data = [{"id": e.id, "nome": str(e)} for e in editais]
        return Response(data)


class ListarFuncoesAPIView(APIView):
    def get(self, request):
        funcoes = FiFuncaoBolsista.objects.all().order_by("funcao")
        data = [{"id": f.id, "nome": str(f)} for f in funcoes]
        return Response(data)


class ListarOfertasAPIView(APIView):
    def get(self, request):
        ofertas = AcCursoOferta.objects.select_related("ac_curso").all().order_by("-id")
        data = [{"id": o.id, "nome": str(o)} for o in ofertas]
        return Response(data)


@extend_schema(**DOCS_LISTAR_CURSOS_COM_BOLSISTAS_ATIVOS_APIVIEW)
class ListarCursosComBolsistasAtivosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def get(self, request):
        fichas_ativas = (
            FiPessoaFicha.objects.filter(
                data_inicio_vinculacao__lt=now(),
                ac_curso_oferta__isnull=False,
                ac_curso_oferta__ac_curso__isnull=False,
            )
            .filter(
                Q(data_fim_vinculacao__isnull=True) | Q(data_fim_vinculacao__gt=now())
            )
            .select_related("ac_curso_oferta__ac_curso")
        )

        cursos = AcCurso.objects.filter(
            id__in=fichas_ativas.values_list(
                "ac_curso_oferta__ac_curso__id", flat=True
            ).distinct()
        ).order_by("nome")

        serializer = AcCursoIdNomeSerializer(cursos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**DOCS_LISTAR_CURSOS_COM_BOLSISTAS_INATIVOS_APIVIEW)
class ListarCursosComBolsistasInativosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def get(self, request):
        # Fichas "zeradas" = sem início de vinculação definido
        fichas_inativas = FiPessoaFicha.objects.filter(
            data_inicio_vinculacao__isnull=True,
            data_fim_vinculacao__isnull=True,
            ac_curso_oferta__isnull=False,
            ac_curso_oferta__ac_curso__isnull=False,
        ).select_related("ac_curso_oferta__ac_curso")

        curso_ids = fichas_inativas.values_list(
            "ac_curso_oferta__ac_curso__id", flat=True
        )

        cursos = AcCurso.objects.filter(id__in=curso_ids).distinct().order_by("nome")

        serializer = AcCursoIdNomeSerializer(cursos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**DOCS_LISTAR_FICHAS_POR_NOME_OU_CPF)
class ListarFiPessoaFichaPorNomeOuCpfAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def get(self, request):
        termo = (request.query_params.get("q") or "").strip()
        if not termo:
            return Response([], status=status.HTTP_200_OK)

        # busca primeiro nas fichas
        fichas = (
            FiPessoaFicha.objects.filter(
                Q(cm_pessoa__nome__icontains=termo) | Q(cm_pessoa__cpf__icontains=termo)
            )
            .values_list("cm_pessoa_id", flat=True)
            .distinct()
        )

        pessoas = CmPessoa.objects.filter(id__in=fichas)

        fichas_qs = FiPessoaFicha.objects.select_related(
            "ed_edital", "fi_funcao_bolsista", "ac_curso_oferta"
        ).order_by("-id")

        pessoas = pessoas.prefetch_related(
            Prefetch("fipessoaficha_set", queryset=fichas_qs, to_attr="fichas")
        )

        serializer = CmPessoaComFichasSerializer(pessoas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**DOCS_DETALHAR_FICHA)
class DetalharFiPessoaFichaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def get(self, request, ficha_id):
        try:
            ficha = FiPessoaFicha.objects.select_related(
                "ed_edital", "fi_funcao_bolsista", "ac_curso_oferta"
            ).get(id=ficha_id)
        except FiPessoaFicha.DoesNotExist:
            return Response(
                {"detail": ERRO_FINANCEIRO_FICHA_NAO_ENCONTRADA},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FiPessoaFichaEdicaoFinanceiroSerializer(ficha)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**DOCS_CURSO_COM_BOLSISTAS_ATIVOS_APIVIEW)
class CursoComBolsistasAtivosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def get(self, request, ac_curso_id):
        fichas_ativas = (
            FiPessoaFicha.objects.filter(
                data_inicio_vinculacao__lt=now(),
                ac_curso_oferta__ac_curso__id=ac_curso_id,
            )
            .filter(
                Q(data_fim_vinculacao__isnull=True) | Q(data_fim_vinculacao__gt=now())
            )
            .select_related("cm_pessoa")
        )

        serializer = BolsistaSerializer(fichas_ativas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**DOCS_CURSO_COM_BOLSISTAS_INATIVOS_APIVIEW)
class CursoComBolsistasInativosAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def get(self, request, ac_curso_id):
        fichas_inativas = FiPessoaFicha.objects.filter(
            data_inicio_vinculacao__isnull=True,
            ac_curso_oferta__ac_curso__id=ac_curso_id,
        ).select_related("cm_pessoa")

        serializer = BolsistaSerializer(fichas_inativas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**DOCS_LISTAR_ULTIMAS_FICHAS_APIVIEW)
class ListarUltimasFichasAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def get(self, request):
        subquery = (
            FiPessoaFicha.objects.filter(cm_pessoa=OuterRef("cm_pessoa"))
            .order_by("-id")
            .values("id")[:1]
        )

        ultimas_fichas = FiPessoaFicha.objects.filter(id=Subquery(subquery)).order_by(
            "-id"
        )[:25]

        serializer = BolsistaSerializer(ultimas_fichas, many=True)
        return Response(serializer.data)


@extend_schema(**DOCS_ATUALIZAR_DATA_VINCULO_BOLSISTA_APIVIEW)
class AtualizarDataVinculoBolsistaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def put(self, request):
        ficha_id = request.data.get("id")

        if not ficha_id:
            return Response(
                {"detail": {ERRO_FINANCEIRO_IDENTIFICADOR_FICHA_OBRIGATORIO}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ficha = FiPessoaFicha.objects.get(id=ficha_id)
        except FiPessoaFicha.DoesNotExist:
            return Response(
                {"detail": {ERRO_FINANCEIRO_FICHA_NAO_ENCONTRADA}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AtualizarDataVinculoSerializer(ficha, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(BolsistaSerializer(ficha).data)


@extend_schema(**DOCS_ATUALIZAR_FICHA)
class AtualizarFiPessoaFichaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsGerenciadorVinculacaoFichas]

    def put(self, request):
        ficha_id = request.data.get("id")
        if not ficha_id:
            return Response(
                {"detail": ERRO_FINANCEIRO_IDENTIFICADOR_FICHA_OBRIGATORIO},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ficha = FiPessoaFicha.objects.get(id=ficha_id)
        except FiPessoaFicha.DoesNotExist:
            return Response(
                {"detail": ERRO_FINANCEIRO_FICHA_NAO_ENCONTRADA},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FiPessoaFichaEdicaoFinanceiroSerializer(
            ficha, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": OK_FICHA_ATUALIZADA}, status=status.HTTP_200_OK)

        return Response(
            {
                "detail": ERRO_FINANCEIRO_FICHA_NAO_ATUALIZADA,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(**DOCS_LISTAR_EDITAIS_ATUAIS_APIVIEW)
class ListarEditaisAtuaisAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalFuncaoFichaOferta]

    def get(self, request):
        editais = EdEdital.objects.filter(data_validade__gte=now())

        serializer = EdEditalSerializer(editais, many=True)
        return Response(serializer.data)


@extend_schema(**DOCS_LISTAR_OFERTAS_ATUAIS_APIVIEW)
class ListarOfertasAtuaisAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalFuncaoFichaOferta]

    def get(self, request):
        ofertas = AcCursoOferta.objects.filter(
            # inicio__lte=now(), # Nao cadastraram o inicio, verificar o motivo
            fim__gte=now()
        ).order_by("-id")

        serializer = AcCursoOfertaIdDescricaoSerializer(ofertas, many=True)
        return Response(serializer.data)


@extend_schema(**DOCS_LISTAR_FUNCOES_COM_FICHA_UAB_APIVIEW)
class ListarFuncoesComFichaUABAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalFuncaoFichaOferta]

    def get(self, request):
        funcoes_da_ficha_uab = FiFuncaoBolsista.objects.filter(ficha_uab=True)
        serializer = ListarFuncoesComFichaUABSerializer(funcoes_da_ficha_uab, many=True)
        return Response(serializer.data)


@extend_schema(**DOCS_ASSOCIAR_EDITAL_FUNCAO_FICHA_OFERTA_APIVIEW)
class AssociarEditalFuncaoFichaOfertaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalFuncaoFichaOferta]

    def get(self, request):
        associacoes = FiEditalFuncaoOferta.objects.select_related(
            "ed_edital", "fi_funcao_bolsista", "ac_curso_oferta"
        ).order_by("-ed_edital__id")
        serializer = FiGetEditalFuncaoOfertaSerializer(associacoes, many=True)
        return Response(serializer.data)

    def put(self, request):
        if not request.data.get("id"):
            return Response(
                {"detail": ERRO_FINANCEIRO_GET_ID_FI_EDITAL_FUNCAO_OFERTA},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            instance = FiEditalFuncaoOferta.objects.get(id=request.data.get("id"))
        except FiEditalFuncaoOferta.DoesNotExist:
            return Response(
                {"detail": ERRO_FINANCEIRO_GET_FI_EDITAL_FUNCAO_OFERTA},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FiPostEditalFuncaoOfertaSerializer(
            instance, data=request.data, partial=False
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
        except IntegrityError:
            return Response(
                {"detail": ERRO_FINANCEIRO_EDITAL_ASSOCIADO_FI_EDITAL_FUNCAO_OFERTA},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.data)

    def post(self, request):
        serializer = FiPostEditalFuncaoOfertaSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        lookups = {
            "ed_edital": validated_data["ed_edital"],
            "fi_funcao_bolsista": validated_data["fi_funcao_bolsista"],
            "ac_curso_oferta": validated_data.get("ac_curso_oferta"),  # pode ser None
        }

        try:
            with transaction.atomic():
                instance, created = FiEditalFuncaoOferta.objects.update_or_create(
                    **lookups, defaults={}
                )
        except IntegrityError:
            return Response(
                {"detail": ERRO_FINANCEIRO_EDITAL_ASSOCIADO_FI_EDITAL_FUNCAO_OFERTA},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = FiGetEditalFuncaoOfertaSerializer(instance).data
        return Response(
            data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


@extend_schema(**DOCS_ASSOCIAR_EDITAL_FUNCAO_FICHA_OFERTA_RETRIEVE_DESTROY_APIVIEW)
class AssociarEditalFuncaoFichaOfertaRetrieveDestroyAPIView(
    DestroyModelMixin, RetrieveAPIView
):
    """
    Busca um item especifico, serve para editar/apagar via mixin
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAssociadorEditalFuncaoFichaOferta]

    queryset = FiEditalFuncaoOferta.objects.select_related(
        "ed_edital", "fi_funcao_bolsista", "ac_curso_oferta"
    ).all()
    serializer_class = FiGetEditalFuncaoOfertaSerializer
    lookup_field = "id"

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
