from django.db.models import Exists, OuterRef, Subquery
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from cead.models import (
    AcCurso,
    AcDisciplina,
    CmPessoa,
    FiDatafrequencia,
    FiFrequencia,
    FiFrequenciaDisciplina,
    FiPessoaFicha,
)
from cead.serializers import AcCursoIdNomeSerializer

from .api_docs import *
from .messages import *
from .permissions import (
    IsEditorDisciplina,
    IsLancadorDeFrequencia,
    IsVisualizadordeRelatorioFrequencia,
)
from .serializers import (
    AcDisciplinaSemCursoSerializer,
    AcDisciplinaSemIdSerializer,
    AcDisciplinaSerializer,
    CmPessoaNomeSerializer,
    FiDatafrequenciaSerializer,
    FrequenciaMesAnteriorSerializer,
    FrequenciaMesAtualSerializer,
)
from .utils import *


def get_coordenador(request):
    try:
        return CmPessoa.objects.get(cpf=request.user.username)
    except CmPessoa.DoesNotExist:
        return Response(
            {"detail": ERRO_LANCA_FREQUENCIA_GET_COORDENADOR},
            status=status.HTTP_404_NOT_FOUND,
        )


def get_cursos_do_coordenador(coordenador):
    cursos = AcCurso.objects.filter(cm_pessoa_coordenador=coordenador, ativo=True)
    if not cursos.exists():
        return Response(
            {"detail": ERRO_LANCA_FREQUENCIA_GET_CURSOS_DO_COORDENADOR},
            status=status.HTTP_404_NOT_FOUND,
        )
    return cursos


def get_cursos_com_frequencia_lancada(datafrequencia):
    cursos = AcCurso.objects.filter(
        accursooferta__fifrequencia__fi_datafrequencia=datafrequencia, ativo=True
    ).distinct()

    if not cursos.exists():
        return Response(
            {"detail": ERRO_LANCA_FREQUENCIA_GET_CURSOS},
            status=status.HTTP_404_NOT_FOUND,
        )

    return cursos


@extend_schema(**DOCS_LANCA_FREQUENCIA_PREVIA_API_VIEW)
class LancaFrequenciaPreviaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsLancadorDeFrequencia]

    def post(self, request):
        bolsistas = request.data.get("bolsistas", [])
        if not bolsistas:
            return Response(
                {"detail": ERRO_LANCA_FREQUENCIA_SEM_FICHA},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dados_previos = []

        for bolsista in bolsistas:
            ficha_id = bolsista.get("ficha_id")
            autorizar_pagamento = bolsista.get("autorizar_pagamento", False)
            disciplinas_ids = bolsista.get("disciplinas", [])

            try:
                ficha = FiPessoaFicha.objects.get(id=ficha_id)
            except FiPessoaFicha.DoesNotExist:
                return Response(
                    {
                        "detail": f"{ERRO_LANCA_FREQUENCIA_FICHA_NAO_ENCONTRADA}: {ficha_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            disciplinas = list(
                AcDisciplina.objects.filter(
                    id__in=disciplinas_ids, ativa=True
                ).values_list("id", "nome")
            )

            dados_previos.append(
                {
                    "ficha_id": ficha.id,
                    "nome": ficha.cm_pessoa.nome,
                    "cpf": ficha.cm_pessoa.cpf,
                    "funcao": ficha.fi_funcao_bolsista.funcao,
                    "curso": ficha.ac_curso_oferta.ac_curso.nome,
                    "autorizar_pagamento": autorizar_pagamento,
                    "disciplinas": [d[1] for d in disciplinas],
                    "disciplinas_ids": [d[0] for d in disciplinas],
                }
            )

            # ordena: pagos primeiro (alfabético), depois não pagos (alfabético)
            dados_previos.sort(
                key=lambda b: (not b["autorizar_pagamento"], b["nome"].lower())
            )

        return Response({"preview": dados_previos}, status=status.HTTP_200_OK)


@extend_schema(**DOCS_LANCA_FREQUENCIA_API_VIEW)
class LancaFrequenciaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsLancadorDeFrequencia]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        cm_pessoa_coordenador = get_coordenador(request)
        if isinstance(cm_pessoa_coordenador, Response):
            raise ValidationError(cm_pessoa_coordenador.data)

        cursos_do_coordenador = get_cursos_do_coordenador(cm_pessoa_coordenador)
        if isinstance(cursos_do_coordenador, Response):
            raise ValidationError(cursos_do_coordenador.data)

        if not AcDisciplina.objects.filter(ac_curso__in=cursos_do_coordenador).exists():
            raise ValidationError({"detail": ERRO_LANCA_FREQUENCIA_GET_DISCIPLINAS})

        datafrequencia_mes_atual = get_datafrequencia_mes_atual()

        if not esta_em_periodo_de_lancamento(datafrequencia_mes_atual):
            raise ValidationError(
                {"detail": ERRO_LANCA_FREQUENCIA_NAO_ESTA_EM_PERIODO_DE_LANCAMENTO}
            )

        if ja_lancou_frequencia(datafrequencia_mes_atual, cm_pessoa_coordenador):
            raise ValidationError(
                {"detail": ERRO_LANCA_FREQUENCIA_FREQUENCIA_JA_LANCADA}
            )

        request.cm_pessoa_coordenador = cm_pessoa_coordenador
        request.cursos_do_coordenador = cursos_do_coordenador
        request.datafrequencia_mes_atual = datafrequencia_mes_atual

    def get(self, request):
        cursos_do_coordenador = []

        for curso_do_coordenador in request.cursos_do_coordenador:
            # Pega a última ficha da pessoa e organiza por nome (ordem alfabética)
            ultima_ficha = (
                FiPessoaFicha.objects.filter(cm_pessoa=OuterRef("cm_pessoa"))
                .order_by("-id")
                .values("id")[:1]
            )

            bolsistas = (
                FiPessoaFicha.objects.filter(
                    ac_curso_oferta__ac_curso=curso_do_coordenador,
                    data_fim_vinculacao__isnull=True,
                    id=Subquery(ultima_ficha),
                )
                .order_by("cm_pessoa__nome")
            )

            dados_do_curso = {
                "coordenador": request.cm_pessoa_coordenador,
                "curso": curso_do_coordenador,
                "disciplinas_do_curso": AcDisciplina.objects.filter(
                    ac_curso=curso_do_coordenador, ativa=True
                ),
            }

            cursos_do_coordenador.append(
                FrequenciaMesAnteriorSerializer(
                    dados_do_curso,
                    context={
                        "bolsistas": bolsistas
                    },
                ).data
            )

        return Response(cursos_do_coordenador, status=status.HTTP_200_OK)

    def post(self, request):
        bolsistas = request.data.get("bolsistas", [])

        if not bolsistas:
            return Response(
                {"detail": ERRO_LANCA_FREQUENCIA_SEM_FICHA},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for bolsista in bolsistas:
            ficha_id = bolsista.get("ficha_id")
            autorizar_pagamento = bolsista.get("autorizar_pagamento", False)
            disciplinas_ids = bolsista.get("disciplinas", [])

            if not autorizar_pagamento:
                continue

            try:
                ficha = FiPessoaFicha.objects.get(id=ficha_id)
            except FiPessoaFicha.DoesNotExist:
                return Response(
                    {
                        "detail": f"{ERRO_LANCA_FREQUENCIA_FICHA_NAO_ENCONTRADA}: {ficha_id}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            fi_frequencia = FiFrequencia.objects.create(
                cm_pessoa=ficha.cm_pessoa,
                cm_pessoa_coordenador=request.cm_pessoa_coordenador,
                fi_datafrequencia=request.datafrequencia_mes_atual,
                ac_curso_oferta=ficha.ac_curso_oferta,
                fi_funcao_bolsista=ficha.fi_funcao_bolsista,
                data=timezone.now(),
            )

            for disciplina_id in disciplinas_ids:
                try:
                    disciplina = AcDisciplina.objects.get(id=disciplina_id, ativa=True)
                except AcDisciplina.DoesNotExist:
                    return Response(
                        {
                            "detail": f"{ERRO_LANCA_FREQUENCIA_DISCIPLINA_NAO_ENCONTRADA}: {disciplina_id}"
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                try:
                    FiFrequenciaDisciplina.objects.create(
                        fi_frequencia=fi_frequencia,
                        ac_disciplina=disciplina,
                    )
                except Exception as e:
                    return Response(
                        {
                            "detail": f"{ERRO_LANCA_FREQUENCIA_DISCIPLINA_INSERCAO}: {str(e)}"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

        return Response(
            {"detail": OK_FREQUENCIA_LANCADA}, status=status.HTTP_201_CREATED
        )


@extend_schema(**DOCS_RELATORIO_LANCAMENTO_API_VIEW)
class RelatorioLancamentoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsLancadorDeFrequencia]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        cm_pessoa_coordenador = get_coordenador(request)
        if isinstance(cm_pessoa_coordenador, Response):
            raise ValidationError(cm_pessoa_coordenador.data)

        cursos_do_coordenador = get_cursos_do_coordenador(cm_pessoa_coordenador)
        if isinstance(cursos_do_coordenador, Response):
            raise ValidationError(cursos_do_coordenador.data)

        request.cm_pessoa_coordenador = cm_pessoa_coordenador
        request.cursos_do_coordenador = cursos_do_coordenador
        request.datafrequencia = get_datafrequencia_mes_atual()

    def get(self, request):
        cursos_do_coordenador = []

        for curso_do_coordenador in request.cursos_do_coordenador:
            relatorio = montar_relatorio_curso(
                curso_do_coordenador,
                request.cm_pessoa_coordenador,
                request.datafrequencia,
            )

            dados_do_curso = {
                "coordenador": CmPessoaNomeSerializer(relatorio["coordenador"]).data,
                "curso": relatorio["curso"],
            }

            cursos_do_coordenador.append(
                FrequenciaMesAtualSerializer(
                    dados_do_curso,
                    context={
                        "bolsistas": sorted(
                            relatorio["fichas"], key=lambda f: f.cm_pessoa.nome
                        )
                    },
                ).data
            )

        return Response(
            {
                "mes_ano_datafrequencia_mes_anterior": get_datafrequencia_periodo_anterior(
                    request.datafrequencia
                ),
                "cursos": cursos_do_coordenador,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_LISTAR_FI_DATAFREQUENCIA_API_VIEW)
class ListarFiDatafrequenciaAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioFrequencia]

    def get(self, request):
        frequencias = FiFrequencia.objects.filter(fi_datafrequencia=OuterRef("pk"))
        datafrequencias = (
            FiDatafrequencia.objects.annotate(tem_frequencia=Exists(frequencias))
            .filter(tem_frequencia=True)
            .order_by("-id")[:6]  # Somente 6 meses
            # Porque nao faz sentido buscar bolsista ja inativado
            # Teria que mudar toda a logica de ficha, se alguem precisar
            # de coisas mais antigas vai ser melhor buscar na base direto
        )

        return Response(
            FiDatafrequenciaSerializer(datafrequencias, many=True).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_RELATORIO_ADMINISTRATIVO_LANCAMENTO_API_VIEW)
class RelatorioAdministrativoLancamentoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVisualizadordeRelatorioFrequencia]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        fi_datafrequencia_id = kwargs.pop("fi_datafrequencia_id", None)
        if not fi_datafrequencia_id:
            raise ValidationError(ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA)

        frequencias = FiFrequencia.objects.filter(fi_datafrequencia=OuterRef("pk"))
        ultimos_ids_permitidos = (
            FiDatafrequencia.objects.annotate(tem_frequencia=Exists(frequencias))
            .filter(tem_frequencia=True)
            .order_by("-id")
            .values_list("id", flat=True)[:6]
        )
        if int(fi_datafrequencia_id) not in ultimos_ids_permitidos:
            raise PermissionDenied(ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_ANTIGA)

        try:
            datafrequencia = FiDatafrequencia.objects.get(id=fi_datafrequencia_id)
        except FiDatafrequencia.DoesNotExist:
            raise ValidationError(
                f"{ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_VAZIO}: {fi_datafrequencia_id}"
            )

        cursos_com_frequencias_lancadas = get_cursos_com_frequencia_lancada(
            datafrequencia
        )
        if isinstance(cursos_com_frequencias_lancadas, Response):
            raise ValidationError(cursos_com_frequencias_lancadas.data)

        request.datafrequencia = datafrequencia
        request.cursos_com_frequencias_lancadas = cursos_com_frequencias_lancadas

    def get(self, request, fi_datafrequencia_id):
        cursos_com_frequencias_lancadas = []

        for curso in request.cursos_com_frequencias_lancadas:
            coord_ids = (
                FiFrequencia.objects.filter(
                    fi_datafrequencia=request.datafrequencia,
                    ac_curso_oferta__ac_curso=curso,
                )
                .values_list("cm_pessoa_coordenador_id", flat=True)
                .distinct()
            )

            for coord_id in coord_ids:
                coord = CmPessoa.objects.get(id=coord_id)

                relatorio = montar_relatorio_curso(
                    curso,
                    coord,
                    request.datafrequencia,
                )

                dados_do_curso = {
                    "coordenador": CmPessoaNomeSerializer(
                        relatorio["coordenador"]
                    ).data,
                    "curso": relatorio["curso"],
                }

                cursos_com_frequencias_lancadas.append(
                    FrequenciaMesAtualSerializer(
                        dados_do_curso,
                        context={
                            "bolsistas": sorted(
                                relatorio["fichas"], key=lambda f: f.cm_pessoa.nome
                            )
                        },
                    ).data
                )

        return Response(
            {
                "mes_ano_datafrequencia_mes_anterior": get_datafrequencia_periodo_anterior(
                    request.datafrequencia
                ),
                "cursos": cursos_com_frequencias_lancadas,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_LISTAR_CURSOS_COM_DISCIPLINAS_API_VIEW)
class ListarCursosComDisciplinasAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEditorDisciplina]

    def get(self, request):
        return Response(
            AcCursoIdNomeSerializer(
                AcCurso.objects.filter(ativo=True).order_by("nome"),
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )


@extend_schema(**DOCS_DISCIPLINAS_CURSO_API_VIEW)
class DisciplinasCursoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEditorDisciplina]

    def get(self, request, ac_curso_id):
        try:
            curso = AcCurso.objects.get(id=ac_curso_id)
        except AcCurso.DoesNotExist:
            return Response(
                {"detail": ERRO_LANCA_FREQUENCIA_GET_CURSO},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            AcDisciplinaSemCursoSerializer(
                AcDisciplina.objects.filter(ac_curso=curso).order_by("nome"), many=True
            ).data
        )

    def post(self, request, ac_curso_id):
        try:
            curso = AcCurso.objects.get(id=ac_curso_id)
        except AcCurso.DoesNotExist:
            return Response(
                {"detail": ERRO_LANCA_FREQUENCIA_GET_CURSO},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AcDisciplinaSemIdSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(ac_curso=curso)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**DOCS_DISCIPLINAS_CURSO_RETRIEVE_UPDATE_DESTROY_API_VIEW)
class DisciplinasCursoRetrieveUpdateDestroyAPIView(UpdateModelMixin, RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsEditorDisciplina]

    queryset = AcDisciplina.objects.all()
    serializer_class = AcDisciplinaSerializer
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
