from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# ERROS - GERAÇÃO DE FICHA
# ------------------------------
ERRO_CODIGO_URL_NAO_ENCONTRADO = (
    "O código de acesso não está presente no endereço da página"
)
ERRO_FICHA_JA_ATIVA = "A ficha já possui início de vínculo do bolsista registrado e não pode mais ser editada"
ERRO_GERACAO_PDF = "Erro ao gerar o PDF"
ERRO_GERACAO_PDF_WKHTMLTOPDF = "Erro ao gerar o PDF - wkhtmltopdf"

# ------------------------------
# ERROS - BUSCA
# ------------------------------
ERRO_INFORME_TERMO_BUSCA_SEARCH = "Informe o termo de busca usando o parâmetro `search`"

# ------------------------------
# ERROS - DADOS PESSOAIS
# ------------------------------
ERRO_CREATE_DADOS_PESSOAIS = "Erro na criação do dados pessoais"
ERRO_NOME_CONJUGE_INVALIDO = "Nome do cônjuge inválido"
ERRO_NOME_MAE_INVALIDO = "Nome da mãe inválido"
ERRO_NOME_MAE_OBRIGATORIO = "O nome da mãe é obrigatório"
ERRO_NOME_PAI_INVALIDO = "Nome do pai inválido"

# ------------------------------
# ERROS - ASSOCIAÇÃO EDITAL, FUNÇÃO DO BOLSISTA E OFERTA
# ------------------------------
ERRO_GET_FI_EDITAL_FUNCAO_OFERTA = (
    "Sem associação entre edital, função do bolsista e oferta"
)

# ------------------------------
# ERROS - LOCALIZAÇÃO (UF, MUNICÍPIO)
# ------------------------------
ERRO_MUNICIPIO_INVALIDO = "Erro ao obter o município em cm_municipio"
ERRO_UF_INVALIDA = "Erro ao obter a unidade da federação cm_uf"

# ------------------------------
# ERROS - SESSÃO
# ------------------------------
ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID = (
    "Sessão inválida, associação edital/função/oferta não encontrada"
)
ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID = (
    "Sessão inválida, identificador de validação não encontrado"
)
ERRO_SESSAO_ASSOCIACAO_EDITAL_FUNCAO_OFERTA_ID_HASH = (
    "Sessão inválida, hash da associação edital/função/oferta não encontrado"
)
ERRO_SESSAO_ED_PESSOA_VAGA_VALIDACAO_ID_HASH = (
    "Sessão inválida, hash do identificador de validação não encontrado"
)

# ------------------------------
# APLICA CONTATO DO SUPORTE EM TODAS AS MENSAGENS DE ERRO
# ------------------------------
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# MENSAGENS DE SUCESSO
# ------------------------------
OK_CPF_HASH_VALIDADO = "O hash é valido para o CPF informado"
OK_FICHA_SALVA = "Salvou os dados da ficha"
OK_SALVOU_ENDERECO_TELEFONE_DADOS_BANCARIOS = (
    "Salvou os dados de endereço, telefone e bancários"
)
