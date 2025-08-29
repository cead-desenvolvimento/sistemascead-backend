import hashlib
from datetime import datetime, timedelta

from cead.models import TrTransmissaoHorario


def hash_transmissao(transmissao):
    horarios_qs = TrTransmissaoHorario.objects.filter(
        tr_transmissao=transmissao
    ).order_by(
        "id"
    )  # Para garantir que o hash nao mude se editar o horario
    horarios_str = ",".join(
        f"{h.inicio.isoformat()}-{h.fim.isoformat()}" for h in horarios_qs
    )

    base = {
        "id": transmissao.id,
        "cpf": transmissao.cm_pessoa.cpf,
        "termo_texto": transmissao.tr_termo.termo.strip(),
        "espaco_nome": transmissao.tr_espaco_fisico.espaco_fisico.strip(),
        "dias_pre": transmissao.tr_espaco_fisico.dias_pre_transmissao or 0,
        "dias_pos": transmissao.tr_espaco_fisico.dias_pos_transmissao or 0,
        "observacao": transmissao.observacao.strip(),
        "horarios": horarios_str,
    }
    texto = "|".join(f"{k}={v}" for k, v in sorted(base.items()))
    return hashlib.sha256(texto.encode()).hexdigest()


def get_semanas_no_intervalo(inicio, fim):
    semanas = set()
    data = inicio
    while data <= fim:
        semanas.add((data.isocalendar()[0], data.isocalendar()[1]))  # (ano, semana)
        data += timedelta(days=1)
    return semanas


def get_meses_no_intervalo(inicio, fim):
    meses = set()
    data = inicio
    while data <= fim:
        meses.add((data.year, data.month))
        data += timedelta(days=1)
    return meses


def dias_por_semana(inicio, fim):
    sem = {}
    data = inicio
    while data <= fim:
        chave = (data.isocalendar()[0], data.isocalendar()[1])
        sem[chave] = sem.get(chave, 0) + 1
        data += timedelta(days=1)
    return sem


def to_naive_time(t):
    return t.replace(tzinfo=None) if hasattr(t, "tzinfo") and t.tzinfo else t


def formatar_horario(inicio_iso, fim_iso):
    # Assume string ISO: "2025-09-15T10:00"
    dt_ini = datetime.fromisoformat(inicio_iso)
    dt_fim = datetime.fromisoformat(fim_iso)
    return f"{dt_ini.strftime('%d/%m/%Y %H:%M')} – {dt_fim.strftime('%H:%M')}"
