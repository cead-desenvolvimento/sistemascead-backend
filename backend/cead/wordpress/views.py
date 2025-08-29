from datetime import date

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from cead.models import (
    AcCurso,
    AcCursoOfertaPolo,
    AcPolo,
    AcPoloHorarioFuncionamento,
)

from .api_docs import *
from .messages import *
from .serializers import (
    AcCursoAtivoSerializer,
    AcCursoContatoSerializer,
    AcCursoDescricaoPerfilEgressoSerializer,
    AcPoloApresentacaoSerializer,
    AcPoloInformacoesSerializer,
    AcPoloNomeSerializer,
    AcPoloSerializer,
)


@extend_schema(**DOCS_GET_CURSOS_ATIVOS_DO_POLO)
@api_view(["GET"])
def get_cursos_ativos_do_polo(request, nome_polo):
    polo = AcPolo.objects.filter(nome=nome_polo).first()

    if not polo:
        return Response(
            {"detail": ERRO_POLO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )

    curso_ids = (
        AcCursoOfertaPolo.objects.filter(
            ac_polo=polo, ac_curso_oferta__fim__gte=date.today()
        )
        .values_list("ac_curso_oferta__ac_curso_id", flat=True)
        .distinct()
    )

    cursos = AcCurso.objects.filter(id__in=curso_ids)

    return Response(AcCursoAtivoSerializer(cursos, many=True).data)


@extend_schema(**DOCS_GET_CURSO_CONTATO)
@api_view(["GET"])
def get_curso_contato(request, nome_curso):
    curso = (
        AcCurso.objects.filter(nome=nome_curso)
        .select_related("cm_pessoa_coordenador")
        .first()
    )

    if not curso:
        return Response(
            {"detail": ERRO_CURSO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(AcCursoContatoSerializer(curso).data)


@extend_schema(**DOCS_GET_CURSO_DESCRICAO_PERFIL_EGRESSO)
@api_view(["GET"])
def get_curso_descricao_perfil_egresso(request, nome_curso):
    curso = (
        AcCurso.objects.filter(nome=nome_curso)
        .select_related("cm_pessoa_coordenador")
        .first()
    )

    if not curso:
        return Response(
            {"detail": ERRO_CURSO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(AcCursoDescricaoPerfilEgressoSerializer(curso).data)


@extend_schema(**DOCS_GET_POLOS)
@api_view(["GET"])
def get_polos(request):
    return Response(AcPoloSerializer(AcPolo.objects.all(), many=True).data)


@extend_schema(**DOCS_GET_POLOS_INFORMACOES)
@api_view(["POST"])
def get_polos_informacoes(request):
    polos = request.data.get("polo")

    if not polos:
        return Response(
            {"error": ERRO_POLO_NENHUM_POLO_FORNECIDO},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Garante que e' uma lista, mesmo que venha como string unica
    polos = polos if isinstance(polos, list) else [polos]

    conditions = Q()
    for nome in polos:
        conditions |= Q(nome__iexact=nome)

    queryset = (
        AcPolo.objects.filter(conditions, ativo=True)
        .select_related("cm_municipio__cm_uf")
        .order_by("cm_municipio__cm_uf__sigla", "nome")
    )

    return Response(AcPoloInformacoesSerializer(queryset, many=True).data)


@extend_schema(**DOCS_GET_POLOS_QUANTIDADE)
@api_view(["GET"])
def get_polos_quantidade(request):
    return Response({"polos_quantidade": AcPolo.objects.count()})


@extend_schema(**DOCS_GET_POLOS_ATIVOS_DO_CURSO)
@api_view(["GET"])
def get_polos_ativos_do_curso(request, nome_curso):
    curso = AcCurso.objects.filter(nome=nome_curso).first()

    if not curso:
        return Response(
            {"detail": ERRO_CURSO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )

    polos_ofertas = (
        AcCursoOfertaPolo.objects.filter(
            ac_curso_oferta__ac_curso=curso, ac_curso_oferta__fim__gte=date.today()
        )
        .select_related("ac_polo")
        .distinct("ac_polo_id")
    )

    polos_ativos = sorted(
        [oferta.ac_polo for oferta in polos_ofertas], key=lambda polo: polo.nome
    )
    return Response(AcPoloNomeSerializer(polos_ativos, many=True).data)


@extend_schema(**DOCS_GET_POLO)
@api_view(["GET"])
def get_polo(request, nome_polo):
    polo = (
        AcPolo.objects.filter(nome=nome_polo)
        .select_related("cm_municipio", "cm_municipio__cm_uf")
        .first()
    )

    if not polo:
        return Response(
            {"detail": ERRO_POLO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(AcPoloSerializer(polo).data)


@extend_schema(**DOCS_GET_POLO_APRESENTACAO)
@api_view(["GET"])
def get_polo_apresentacao(request, nome_polo):
    polo = AcPolo.objects.filter(nome=nome_polo).first()

    if not polo:
        return Response(
            {"detail": ERRO_POLO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(AcPoloApresentacaoSerializer(polo).data)


@extend_schema(**DOCS_GET_POLO_NOME_COM_OFERTA_ATIVA)
@api_view(["GET"])
def get_polo_nome_com_oferta_ativa(request, nome_polo):
    polo = AcPolo.objects.filter(nome=nome_polo).first()

    if not polo:
        return Response(
            {"detail": ERRO_POLO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )

    oferta_ativa = AcCursoOfertaPolo.objects.filter(
        ac_polo=polo, ac_curso_oferta__fim__gte=date.today()
    ).exists()

    if not oferta_ativa:
        return Response(
            {"detail": ERRO_POLO_SEM_OFERTA_ATIVA}, status=status.HTTP_404_NOT_FOUND
        )

    return Response(AcPoloNomeSerializer(polo).data)


@extend_schema(**DOCS_GET_POLO_HORARIO_FUNCIONAMENTO)
@api_view(["GET"])
def get_polo_horario_funcionamento(request, nome_polo):
    polo = AcPolo.objects.filter(nome=nome_polo).first()

    if not polo:
        return Response(
            {"detail": ERRO_POLO_NAO_ENCONTRADO}, status=status.HTTP_404_NOT_FOUND
        )

    horarios = (
        AcPoloHorarioFuncionamento.objects.filter(ac_polo=polo)
        .values("dia_semana", "hora_inicio", "hora_fim")
        .order_by("dia_semana", "hora_inicio")
    )
    return Response(list(horarios))
