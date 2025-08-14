from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

ERRO_CREDENCIAIS_INVALIDAS = "Não há conta ativa com as credenciais enviadas"
ERRO_CORRIJA_ERROS = "Por favor, corrija os erros"
OK_SENHA_ALTERADA = "Sua senha foi alterada"

# Adiciona INFO_ENTRE_CONTATO_SUPORTE a todas as mensagens de erro
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE
