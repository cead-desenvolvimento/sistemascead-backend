from django.utils import timezone
from datetime import timedelta
from cead.models import FiFrequencia, FiDatafrequencia, FiPessoaFicha

from .messages import (
    ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_MES_ANTERIOR,
    ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_MES_ATUAL,
)


# Serve para o relatorio administrativo
# as outras funcoes abaixo sempre calculam em relacao ao mes corrente, porque o usuario
# so pode pegar o relatorio do mes
# Essa funcao pega o mes anterior ao do parametro e retorna string mm/aa
def get_datafrequencia_periodo_anterior(datafrequencia_atual):
    if (
        not datafrequencia_atual
        or not hasattr(datafrequencia_atual, "data_inicio")
        or not datafrequencia_atual.data_inicio
    ):
        return None

    try:
        data = datafrequencia_atual.data_inicio
        mes_anterior = data.replace(day=1) - timedelta(days=1)
        return f"{mes_anterior.month:02d}/{str(mes_anterior.year)}"
    except Exception:
        return None


# Ha de se considerar que a frequencia sempre inicia e termina no mesmo mes, e ha uma para cada mes
def get_datafrequencia_mes_anterior():
    primeiro_dia_mes_anterior = (
        timezone.now().replace(day=1) - timedelta(days=1)
    ).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ultimo_dia_mes_anterior = (primeiro_dia_mes_anterior + timedelta(days=32)).replace(
        day=1
    ) - timedelta(seconds=1)

    try:
        return FiDatafrequencia.objects.get(
            data_inicio__lte=ultimo_dia_mes_anterior,
            data_fim__gte=primeiro_dia_mes_anterior,
        )
    except Exception as e:
        raise Exception(
            f"{ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_MES_ANTERIOR}: {str(e)}"
        )


# Ha de se considerar que a frequencia sempre inicia e termina no mesmo mes, e ha uma para cada mes
def get_datafrequencia_mes_atual():
    primeiro_dia_mes_corrente = timezone.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    ultimo_dia_mes_corrente = (primeiro_dia_mes_corrente + timedelta(days=32)).replace(
        day=1
    ) - timedelta(seconds=1)

    try:
        return FiDatafrequencia.objects.get(
            data_inicio__lte=ultimo_dia_mes_corrente,
            data_fim__gte=primeiro_dia_mes_corrente,
        )
    except Exception as e:
        raise Exception(
            f"{ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_MES_ATUAL}: {str(e)}"
        )


def esta_em_periodo_de_lancamento(datafrequencia):
    if datafrequencia and datafrequencia.data_inicio and datafrequencia.data_fim:
        return datafrequencia.data_inicio <= timezone.now() <= datafrequencia.data_fim
    return False


def ja_lancou_frequencia(datafrequencia, cm_pessoa_coordenador):
    return FiFrequencia.objects.filter(
        cm_pessoa_coordenador=cm_pessoa_coordenador, fi_datafrequencia=datafrequencia
    ).exists()


def montar_relatorio_curso(curso, coord, datafrequencia):
    """
    Monta o dicionário de um curso com coordenador e bolsistas lançados.
    Tudo gira em torno da ficha, porque são os dados mais confiáveis da base do legado
    """
    pessoas_ids = FiFrequencia.objects.filter(
        fi_datafrequencia=datafrequencia,
        ac_curso_oferta__ac_curso=curso,
        cm_pessoa_coordenador_id=coord.id,
    ).values_list("cm_pessoa_id", flat=True)

    fichas_queryset = (
        FiPessoaFicha.objects.filter(
            cm_pessoa_id__in=pessoas_ids,
            ac_curso_oferta__ac_curso=curso,
        )
        .order_by("cm_pessoa", "-id")
        .distinct("cm_pessoa")
        .select_related("cm_pessoa", "ac_curso_oferta")
    )

    return {
        "coordenador": coord,
        "curso": curso,
        "fichas": fichas_queryset,
    }
