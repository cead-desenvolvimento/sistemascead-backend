from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# MENSAGENS DE EMAIL - FICHA
# ------------------------------
EMAIL_BOLSA_ASSUNTO = "CEAD, UFJF - Ficha para provimento de bolsa"
EMAIL_BOLSA_CODIGO_GERADO = "O código para o preenchimento da sua ficha foi gerado"
EMAIL_BOLSA_DUVIDAS_PARA_O_FINANCEIRO = "Dúvidas no preenchimento da ficha?"
EMAIL_BOLSA_ENDERECO_FICHA = "A ficha deve ser preenchida em"
EMAIL_BOLSA_ENVIADO = "Mensagem enviada para"
EMAILS_BOLSA_ENVIADOS = "Mensagens enviadas"

# ------------------------------
# MENSAGENS DE EMAIL - JUSTIFICATIVA
# ------------------------------
EMAIL_JUSTIFICATIVA_ASSUNTO = "CEAD, UFJF - Justificativas da avaliação do Edital"
EMAIL_JUSTIFICATIVA_AS_SEGUINTES_JUSTIFICATIVAS = (
    "as seguintes justificativas para o Edital"
)
EMAIL_JUSTIFICATIVA_A_SEGUINTE_JUSTIFICATIVA = "a seguinte justificativa para o Edital"
EMAIL_JUSTIFICATIVA_AVALIADOR_REGISTROU = (
    "O(a) avaliador(a) da sua documentação registrou no sistema"
)
EMAIL_JUSTIFICATIVA_DUVIDAS_PARA_O_ACADEMICO = "Dúvidas?"

# ------------------------------
# MENSAGENS DE ERRO - AÇÕES DE USUÁRIO
# ------------------------------
ERRO_EDITAL_FORA_PRAZO_EMISSAO_MENSAGEM = (
    "O edital está fora do prazo para o envio de mensagem de geração de ficha"
)
ERRO_EDITAL_FORA_PRAZO_VALIDACAO = "O edital está fora do prazo de validação"
ERRO_PONTUACAO_INVALIDA_DOCUMENTO = "Pontuação inválida para o documento"
ERRO_PONTUACAO_INVALIDA_FRASE_INCOMPLETA = "A pontuação deve estar entre 0 e"

# ------------------------------
# MENSAGENS DE ERRO - FORMATAÇÃO E POST
# ------------------------------
ERRO_POST_FORMATO_ID_INVALIDO = "Formato do identificador de arquivo inválido"
ERRO_POST_PESSOAVAGAVALIDACAO = "Erro no serializer que valida o candidato"
ERRO_POST_TIPO_DOCUMENTO_INVALIDO = "Tipo de documento inválido"

# ------------------------------
# MENSAGENS DE ERRO - CONSULTAS
# ------------------------------
ERRO_GET_PESSOA = "Pessoa não encontrada na tabela cm_pessoa"
ERRO_GET_PESSOAS = "Problemas na busca das pessoas"
ERRO_GET_PESSOAVAGAINSCRICAO = (
    "Inscrição não encontrada para a pessoa e vaga informadas"
)
ERRO_GET_PESSOAVAGAJUSTIFICATIVA = (
    "Justificativa não encontrada para a pessoa neste edital"
)
ERRO_GET_PESSOAVAGAVALIDACOES = "Validações não encontradas para a vaga informada"
ERRO_GET_USUARIO = "Usuário não encontrado em django.auth_user"
ERRO_ENVIO_EMAIL = "Erro no envio do email"

# ------------------------------
# MENSAGENS DE ERRO - PERMISSÕES
# ------------------------------
ERRO_NAO_ESTA_AUTORIZADO_A_VISUALIZAR_ESTE_RELATORIO = (
    "Você não está associado ao edital para visualizar este relatório"
)
ERRO_NAO_ESTA_NO_GRUPO_ASSOCIADORES_DE_EDITAIS_PESSOAS = (
    "Você não está no grupo de associadores de editais/pessoas"
)
ERRO_NAO_ESTA_NO_GRUPO_EMISSORES_DE_MENSAGEM_FICHA = (
    "Você não está no grupo de emissores de mensagem para criação de ficha"
)
ERRO_NAO_ESTA_NO_GRUPO_VALIDADORES_DE_EDITAIS = (
    "Você não está no grupo de validadores de editais"
)
ERRO_NAO_ESTA_NO_GRUPO_VISUALIZADORES_DE_RELATORIO_DE_EDITAIS = (
    "Você não está no grupo de visualizadores de relatório de editais"
)

# ------------------------------
# MENSAGENS DE SUCESSO
# ------------------------------
OK_DADOS_CANDIDATO = "Informações salvas para o candidato"

# ------------------------------
# COMPLETA MENSAGENS DE ERRO COM CONTATO DO SUPORTE
# ------------------------------
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE
