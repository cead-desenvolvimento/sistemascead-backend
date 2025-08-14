# admin.py
ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_CHECKBOX = (
    "Houve um erro ao tentar inserir um campo de checkbox"
)
ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_COMBOBOX = (
    "Houve um erro ao tentar inserir um campo de combobox"
)
ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX = (
    "Houve um erro ao tentar inserir um campo de data"
)
ERRO_FERIADOS_INSERCAO = "Erro ao importar feriados"
OK_FERIADOS_INSERCAO = "Feriado(s) inserido(s)"

# ------------------------------
# MENSAGENS PADRÃO DE EMAIL
# ------------------------------
EMAIL_ASSINATURA = "CEAD, UFJF"
EMAIL_DUVIDAS_PARA_O_SUPORTE = (
    "Problemas de ordem tecnológica e/ou dúvidas em relação ao sistema?"
)
EMAIL_ENDERECO_NAO_MONITORADO = (
    "Não responda esta mensagem, o endereço de envio não é monitorado."
)

# ------------------------------
# ERROS COMUNS DO SISTEMA
# ------------------------------
ERRO_CPF_INVALIDO = "CPF inválido"
ERRO_GET_ARQUIVO = "O arquivo não foi encontrado"
ERRO_GET_DATAFREQUENCIA = "Período de frequência não encontrado"
ERRO_GET_EDITAL = "O edital não foi encontrado"
ERRO_GET_PESSOA_VAGA_VALIDACAO = "A validação da pessoa não foi encontrada"
ERRO_GET_VAGA = "Vaga não encontrada"
ERRO_GET_VAGAS = "Ocorreu um erro ao tentar listar as vagas do edital"
ERRO_HASH_INVALIDO = "Erro na validação do hash"
ERRO_MULTIPLOS_EDITAIS = "Mais de um edital encontrado com este número e ano"
ERRO_SESSAO_INVALIDA = "Sessão inválida"
ERRO_VAGAID_NA_SESSAO = "Identificador da vaga não está na sessão"
ERRO_VAGAIDHASH_NA_SESSAO = "Hash do identificador da vaga não está na sessão"

# ------------------------------
# CONTATOS DE EQUIPE
# ------------------------------
INFO_EMAIL_ACADEMICO = "academico.cead@ufjf.br"
INFO_ENTRE_CONTATO_ACADEMICO = (
    "Entre em contato com a equipe acadêmica do CEAD: " + INFO_EMAIL_ACADEMICO
)

INFO_EMAIL_FINANCEIRO = "financeiro.cead@ufjf.br"
INFO_ENTRE_CONTATO_FINANCEIRO = (
    "Entre em contato com a equipe do financeiro do CEAD: " + INFO_EMAIL_FINANCEIRO
)

INFO_EMAIL_SUPORTE = "suporte.cead@ufjf.br"
INFO_ENTRE_CONTATO_SUPORTE = (
    "Entre em contato com o suporte tecnológico do CEAD: " + INFO_EMAIL_SUPORTE
)

# ------------------------------
# APLICA CONTATO DO SUPORTE A TODAS AS MENSAGENS DE ERRO
# ------------------------------
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE
