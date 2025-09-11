from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# ERROS - DADOS E CAMPOS OBRIGATÓRIOS
# ------------------------------
ERRO_DATA_INVALIDA = "Data inválida"
ERRO_FINANCEIRO_IDENTIFICADOR_FICHA_OBRIGATORIO = (
    "O identificador da ficha é obrigatório"
)
ERRO_FINANCEIRO_GET_ID_FI_EDITAL_FUNCAO_OFERTA = (
    "Identificador não enviado na requisição"
)

# ------------------------------
# ERROS - FICHA E EDITAL
# ------------------------------
ERRO_FINANCEIRO_EDITAL_ASSOCIADO_FI_EDITAL_FUNCAO_OFERTA = (
    "Este edital já está associado a uma função/oferta"
)
ERRO_FINANCEIRO_FICHA_NAO_ENCONTRADA = "Ficha não encontrada"
ERRO_FINANCEIRO_GET_FI_EDITAL_FUNCAO_OFERTA = "Identificador não encontrado"

# ------------------------------
# ERROS - PERMISSÕES DE GRUPO
# ------------------------------
ERRO_FINANCEIRO_NAO_ESTA_NO_GRUPO_DE_GERENCIADORES_DATA_VINCULACAO_FICHAS = (
    "Você não está no grupo de gerenciadores de datas de vinculação de fichas"
)
ERRO_FINANCEIRO_NAO_ESTA_NO_GRUPO_DE_ASSOCIADOR_VAGA_FICHA = (
    "Você não está no grupo de associadores de vaga e ficha"
)

# ------------------------------
# ATUALIZAÇÃO DE FICHA
# ------------------------------
OK_FICHA_ATUALIZADA = "A ficha foi atualizada"


# ------------------------------
# APLICA CONTATO DO SUPORTE EM TODAS AS MENSAGENS DE ERRO
# ------------------------------
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE
