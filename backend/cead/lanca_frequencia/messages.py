from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# ERROS - CURSO / DISCIPLINA
# ------------------------------
ERRO_LANCA_FREQUENCIA_GET_CURSO = "Erro ao buscar o curso"
ERRO_LANCA_FREQUENCIA_GET_CURSOS = "Erro ao buscar os cursos"
ERRO_LANCA_FREQUENCIA_GET_CURSOS_DO_COORDENADOR = (
    "Não há cursos em que o usuário autenticado é coordenador"
)
ERRO_LANCA_FREQUENCIA_GET_DISCIPLINAS = (
    "Disciplinas não encontradas para o curso do coordenador autenticado"
)

# ------------------------------
# ERROS - COORDENADOR
# ------------------------------
ERRO_LANCA_FREQUENCIA_GET_COORDENADOR = (
    "Coordenador de curso não encontrado na tabela cm_pessoa"
)

# ------------------------------
# ERROS - DATAFREQUENCIA
# ------------------------------
ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA = (
    "Não foi possível encontrar a data de frequência"
)
ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_ANTIGA = (
    "Não foi possível acessar esta data de frequência"
)
ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_MES_ANTERIOR = (
    "Não foi possível encontrar a data de frequência do mês passado"
)
ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_MES_ATUAL = (
    "Não foi possível encontrar a data de frequência do mês atual"
)
ERRO_LANCA_FREQUENCIA_GET_DATAFREQUENCIA_VAZIO = (
    "Não há data frequência para o período selecionado"
)

# ------------------------------
# ERROS - FICHA / FREQUÊNCIA
# ------------------------------
ERRO_LANCA_FREQUENCIA_FICHA_NAO_ENCONTRADA = (
    "A ficha de Ficha não encontrada, identificador"
)
ERRO_LANCA_FREQUENCIA_SEM_FICHA = "Nenhuma ficha encontrada"
ERRO_LANCA_FREQUENCIA_FREQUENCIA_JA_LANCADA = "A frequência deste mês já foi lançada"
ERRO_LANCA_FREQUENCIA_NAO_ESTA_EM_PERIODO_DE_LANCAMENTO = (
    "Frequência fora de período de lançamento"
)

# ------------------------------
# ERROS - PERMISSÕES / GRUPOS
# ------------------------------
ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_EDITORES_DISCIPLINAS = (
    "Você não está no grupo de editores de disciplinas"
)
ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_LANCADORES_DE_FREQUENCIA = (
    "Você não está no grupo de lançadores de frequência"
)
ERRO_LANCA_FREQUENCIA_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_FREQUENCIA = (
    "Você não está no grupo de visualizadores de relatório de frequência"
)

# ------------------------------
# ERROS - DISCIPLINA / INSERÇÃO
# ------------------------------
ERRO_LANCA_FREQUENCIA_DISCIPLINA_NAO_ENCONTRADA = (
    "Disciplina não encontrada, identificador"
)
ERRO_LANCA_FREQUENCIA_DISCIPLINA_INSERCAO = (
    "Erro na associação entre bolsista e disciplina"
)

# ------------------------------
# APLICA CONTATO DO SUPORTE EM TODAS AS MENSAGENS DE ERRO
# ------------------------------
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# SUCESSO
# ------------------------------
OK_FREQUENCIA_LANCADA = "A frequência foi lançada"
