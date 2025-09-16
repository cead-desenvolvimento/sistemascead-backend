from django.db.models import Max, Sum, FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone

from cead.models import (
    EdVagaCampoCheckbox,
    EdVagaCampoCombobox,
    EdVagaCampoDatebox,
    EdPessoaVagaValidacao,
    EdPessoaVagaJustificativa,
    EdPessoaVagaCota,
    EdPessoaVagaValidacaoIndeferimento,
)


def calcular_maximo_de_pontos(vaga):
    soma_checkbox = EdVagaCampoCheckbox.objects.filter(
        ed_vaga=vaga, pontuacao__isnull=False
    ).aggregate(total=Coalesce(Sum("pontuacao", output_field=FloatField()), 0.0))[
        "total"
    ]

    soma_combobox = (
        EdVagaCampoCombobox.objects.filter(ed_vaga=vaga, pontuacao__isnull=False)
        .values("ed_campo_id")
        .annotate(max_pontuacao=Max("pontuacao"))
        .aggregate(total=Coalesce(Sum("max_pontuacao", output_field=FloatField()), 0.0))
    )["total"]

    soma_datebox = EdVagaCampoDatebox.objects.filter(
        ed_vaga=vaga, pontuacao_maxima__isnull=False
    ).aggregate(
        total=Coalesce(Sum("pontuacao_maxima", output_field=FloatField()), 0.0)
    )[
        "total"
    ]

    return round(float(soma_checkbox + soma_combobox + soma_datebox), 2)


def get_status_order(status):
    """
    Define a ordem de prioridade para os status:
    Deferido > Indeferido > Validado (sem pontuação) > Não Validado.
    """
    if status == "Deferido":
        return 0
    if status == "Indeferido":
        return 1
    if status == "Validado (sem pontuação)":
        return 2
    return 3


def get_sort_score(item):
    """
    Retorna a pontuação para ordenação com base no status.
    Prioriza a pontuação real para Deferidos e Indeferidos,
    e a pontuação informada para Não Validados.
    """
    status = item.get("status_validacao")
    if status in ("Deferido", "Indeferido", "Validado (sem pontuação)"):
        return item.get("pontuacao_real", 0.0)

    return item.get("pontuacao_informada", 0.0)


def processar_inscricao_para_relatorio(
    inscricao,
    validacoes_dict,
    justificativas_dict,
    cotas_dict,
    indeferidos_da_vaga,
    incluir_vaga=False,
):
    """
    Processa uma única inscrição para gerar os dados do relatório.
    Reúne a lógica de status, pontuação e responsável.
    """
    validacao = validacoes_dict.get(inscricao.cm_pessoa_id)
    justificativa = justificativas_dict.get(inscricao.cm_pessoa_id)
    cota = cotas_dict.get(inscricao.cm_pessoa_id)
    is_indeferido = inscricao.cm_pessoa_id in indeferidos_da_vaga

    status_validacao = "Não Validado"
    pontuacao_real = None
    responsavel = "-"
    data_validacao = "-"

    # Primeiro, verificar se há validação ou justificativa, pois isso indica que a inscrição foi processada.
    if validacao or justificativa:
        # Se houver validação, obtém o responsável e a data
        if validacao:
            responsavel = validacao.cm_pessoa_responsavel_validacao.nome
            data_validacao = (
                timezone.localtime(validacao.data).strftime("%d/%m/%Y %H:%M")
                if validacao.data
                else "-"
            )
        # Se não houver validação, mas houver justificativa, pega o responsável da justificativa
        elif justificativa:
            responsavel = justificativa.cm_pessoa_responsavel_justificativa.nome

        # Agora, determina o status final com base nas informações disponíveis.
        if is_indeferido:
            status_validacao = "Indeferido"
            pontuacao_real = 0.0
        elif validacao and validacao.pontuacao is not None:
            status_validacao = "Deferido"
            pontuacao_real = float(validacao.pontuacao)
        else:
            # Caso para dados antigos onde há interação do validador, mas sem pontuação
            # O sistema antigo não salvava o que estava efetivamente inválido, só criava
            # o registro de uma atividade e comparava com a inscrição, inferindo o indeferimento
            # A base antiga era caótica, não vale a pena replicar o comportamento aqui
            status_validacao = "Validado (sem pontuação)"
            pontuacao_real = 0.0

    dados_inscricao = {
        "protocolo": inscricao.id,
        "nome": inscricao.cm_pessoa.nome,
        "cpf": inscricao.cm_pessoa.cpf_com_pontos_e_traco(),
        "email": inscricao.cm_pessoa.email,
        "pontuacao_informada": (
            0.0 if inscricao.pontuacao is None else float(inscricao.pontuacao)
        ),
        "pontuacao_real": pontuacao_real if pontuacao_real is not None else "-",
        "status_validacao": status_validacao,
        "responsavel": responsavel,
        "data_inscricao": (
            timezone.localtime(inscricao.data).strftime("%d/%m/%Y %H:%M")
            if inscricao.data
            else "-"
        ),
        "data_validacao": data_validacao,
        "justificativa_pontuacao": (
            justificativa.justificativa if justificativa else "-"
        ),
        "cota": cota.ed_vaga_cota.ed_cota.cota if cota else "-",
    }

    if incluir_vaga:
        dados_inscricao["vaga"] = inscricao.ed_vaga.descricao

    return dados_inscricao
