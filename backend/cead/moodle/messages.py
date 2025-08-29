from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

ERRO_GET_DATAFREQUENCIA = "Período de frequência não encontrado"
ERRO_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_MOODLE = (
    "Você não está no grupo de visualizadores de relatório do Moodle"
)

# Adiciona INFO_ENTRE_CONTATO_SUPORTE a todas as mensagens de erro
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE
