from django.db.models import Exists, OuterRef
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cead.models import FiDatafrequencia, FiFrequencia, FiFrequenciaMoodle

from .api_docs import *
from .messages import ERRO_GET_DATAFREQUENCIA
from .permissions import IsVisualizadordeRelatorioMoodle
from .serializers import (
    FiDatafrequenciaSerializer,
    FiFrequenciaMoodleSerializer,
)


@extend_schema(**DOCS_LISTAR_FI_DATAFREQUENCIA_MOODLE_API_VIEW)
class ListarFiDatafrequenciaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioMoodle]

    # Retornar so as datafrequencia que tem algo escrito em fi_frequencia_moodle
    def get(self, request):
        subquery = FiFrequenciaMoodle.objects.filter(fi_datafrequencia=OuterRef("pk"))
        queryset = (
            FiDatafrequencia.objects.annotate(tem_frequencia=Exists(subquery))
            .filter(tem_frequencia=True)
            .order_by("-id")
        )

        serializer = FiDatafrequenciaSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**DOCS_SELECAO_CURSOS_RELATORIO_MOODLE_API_VIEW)
class SelecaoCursosRelatorioMoodleAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioMoodle]

    def get(self, request, fi_datafrequencia_id):
        try:
            fi_datafrequencia = FiDatafrequencia.objects.get(id=fi_datafrequencia_id)
        except FiDatafrequencia.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_DATAFREQUENCIA})

        pessoas_com_acesso_ao_moodle = FiFrequenciaMoodle.objects.filter(
            fi_datafrequencia=fi_datafrequencia
        ).values_list("cm_pessoa_id", flat=True)

        cursos = (
            FiFrequencia.objects.filter(
                fi_datafrequencia=fi_datafrequencia,
                cm_pessoa_id__in=pessoas_com_acesso_ao_moodle,
            )
            .select_related("ac_curso_oferta__ac_curso")
            .values("ac_curso_oferta__ac_curso__id", "ac_curso_oferta__ac_curso__nome")
            .distinct()
            .order_by("ac_curso_oferta__ac_curso__nome")
        )

        return Response(list(cursos), status=status.HTTP_200_OK)


@extend_schema(**DOCS_RELATORIO_MOODLE_API_VIEW)
class RelatorioMoodleAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioMoodle]

    def get(self, request, fi_datafrequencia_id):
        try:
            fi_datafrequencia = FiDatafrequencia.objects.get(id=fi_datafrequencia_id)
        except FiDatafrequencia.DoesNotExist:
            raise ValidationError({"detail": ERRO_GET_DATAFREQUENCIA})

        queryset = FiFrequenciaMoodle.objects.filter(
            fi_datafrequencia=fi_datafrequencia
        ).select_related("cm_pessoa")

        cursos_ids = request.query_params.get("cursos")
        if cursos_ids:
            ids = [x.strip() for x in cursos_ids.split(",") if x.strip().isdigit()]
            if ids:
                cursos_ids = [int(x) for x in ids]
                pessoas_filtradas = (
                    FiFrequencia.objects.filter(
                        fi_datafrequencia=fi_datafrequencia,
                        ac_curso_oferta__ac_curso__id__in=cursos_ids,
                    )
                    .values_list("cm_pessoa_id", flat=True)
                    .distinct()
                )

                queryset = queryset.filter(cm_pessoa_id__in=pessoas_filtradas)

        serializer = FiFrequenciaMoodleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
