from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# EMAIL - TRANSMISSÃO
# ------------------------------

EMAIL_TRANSMISSAO_ASSUNTO = "CEAD, UFJF - pedido de transmissão"

# ------------------------------
# ERROS - TRANSMISSÃO
# ------------------------------

ERRO_GET_REQUISITANTE = "Não foi possível obter os dados do requisitante"
ERRO_GET_LIMITES = "Não foi possível obter as configurações de limites da transmissão"
ERRO_ACEITE_TERMO_NAO_REALIZADO = "Aceite do termo não realizado"
ERRO_ACEITE_TERMO_EXPIRADO = "Aceite do termo expirado"
ERRO_GET_TERMO_SEM_TERMO = "Nenhum termo encontrado"

ERRO_ESPACO_NAO_ENCONTRADO = "Espaço não encontrado"
ERRO_GET_ESPACO_FISICO_SEM_ESPACO_FISICO = "Nenhum espaço físico encontrado"
ERRO_POST_ESPACO_ID_OBRIGATORIO = "O identificador do espaço não está na sessão"

ERRO_DATA_EQUIPE_INDISPONIVEL = "Equipe indisponível"
ERRO_DATA_INDISPONIVEL = "Data indisponível"
ERRO_DATA_INVALIDA = "Data inválida - dia não permitido"
ERRO_DATA_INVALIDA_INICIO = "Data inválida - início inválido"
ERRO_DATA_INVALIDA_INICIO_OBRIGATORIO = "Data inválida - início é obrigatório"
ERRO_DATA_INVALIDA_INICIO_FIM = "Data inválida - fim antes do início"
ERRO_DATA_INVALIDA_INTERVALO = "Data inválida - fora do intervalo permitido"
ERRO_DATA_FORMATO = "O formato da data enviada é inválido"
ERRO_DATA_SEMANA = "O evento deve ter início e fim na mesma semana"
ERRO_DATA_SESSAO = "Erro ao interpretar datas da sessão"
ERRO_DATAS_OBRIGATORIAS = "As duas datas são obrigatórias"

ERRO_HORARIO_CONFLITO_RESERVA = "Conflito de reserva de horário"
ERRO_HORARIO_INFORMACOES_INCOMPLETAS = "Informações incompletas em"
ERRO_HORARIO_INVALIDO_INICIO_FIM = "Horário inválido - fim antes ou igual ao início"
ERRO_HORARIO_FORMATO_INVALIDO = "Formato inválido em"
ERRO_HORARIO_NAO_PERMITIDO = "Horário não permitido"
ERRO_HORARIO_SEM_HORARIO = "Horário não informado"

ERRO_TRANSMISSAO_NAO_ESTA_NO_GRUPO_REQUISITANTES_DE_TRANSMISSAO = (
    "Você não está no grupo de requisitantes de transmissão"
)
ERRO_TRANSMISSAO_OBSERVACAO = "O campo de observação é obrigatório"
ERRO_TRANSMISSAO_SALVAR = "Erro ao salvar a transmissão"
ERRO_TRANSMISSAO_SESSAO = "Os dados da transmissão não estão na sessão"

ERRO_LIMITES_LIMITE_POR_PESSOA = "O limite de pedidos de transmissão foi excedido"
ERRO_LIMITES_LIMITE_POR_MES = "O limite mensal de pedidos de transmissão foi excedido"
ERRO_LIMITES_LIMITE_POR_SEMANA = (
    "O limite semanal de pedidos de transmissão foi excedido"
)
ERRO_LIMITES_LIMITE_NA_SEMANA = (
    "O limite de dias na semana para pedidos de transmissão foi excedido"
)
ERRO_LIMITES_LIMITE_SEMANA = (
    "As configurações não permitem eventos que passam de uma semana para outra"
)

# Adiciona INFO_ENTRE_CONTATO_SUPORTE a todas as mensagens de erro
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# OK - TRANSMISSÃO
# ------------------------------

OK_ACEITE_TERMO = "O termo foi aceito"
OK_ESPACO_SELECIONADO = "Espaço selecionado"
OK_PERIODO_SELECIONADO = "Período selecionado"
OK_HORARIO_SELECIONADO = "Horário selecionado"
