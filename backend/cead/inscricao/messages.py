from cead.messages import INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# ERROS - SERIALIZERS
# ------------------------------
ERRO_EMAIL_INVALIDO = "Endereço de email inválido"
ERRO_EMAIL_JA_REGISTRADO = "Este endereço de email já está registrado no sistema"
ERRO_NOME_INVALIDO = "Nome inválido"
ERRO_NOME_OBRIGATORIO = "O nome é obrigatório"

# ------------------------------
# EMAIL - INSCRIÇÃO
# ------------------------------
EMAIL_INSCRICAO_ASSUNTO = "CEAD, UFJF - seu código para inscrição"
EMAIL_INSCRICAO_CODIGO_GERADO = (
    "O código para o preenchimento da sua inscrição foi gerado"
)
EMAIL_INSCRICAO_DUVIDAS_PARA_O_ACADEMICO = "Dúvidas no preenchimento da inscrição?"

# ------------------------------
# ERROS - SESSÃO
# ------------------------------
ERRO_CANDIDATO_NA_SESSAO = "Candidato não está na sessão"
ERRO_CANDIDATOHASH_NA_SESSAO = "Hash do candidato não está na sessão"
ERRO_CODIGOCANDIDATO_NA_SESSAO = "Código do candidato não está na sessão"
ERRO_CODIGOCANDIDATOHASH_NA_SESSAO = "Hash do código do candidato não está na sessão"
ERRO_CODIGO_AUSENTE = "O validador do código está ausente na sessão"
ERRO_INSCRICAO_NA_SESSAO = "Inscrição não está na sessão"
ERRO_INSCRICAOHASH_NA_SESSAO = "Hash da inscrição não está na sessão"
ERRO_PONTUACAO_NA_SESSAO = "Pontuação não está na sessão"
ERRO_PONTUACAOHASH_NA_SESSAO = "Hash da pontuação não está na sessão"
ERRO_REQUEST_DATA_GET_VAGAID = "O identificador da vaga não foi fornecido"

# ------------------------------
# ERROS - INSCRIÇÃO
# ------------------------------
ERRO_APAGAR_INSCRICAO_CONCORRENTE = "Erro ao apagar a inscrição concorrente"
ERRO_INSCRICAO_EMAIL_NAO_CORRESPONDE = (
    "O email digitado não corresponde ao CPF informado"
)
ERRO_INSCRICOES_ENCERRADAS = "As inscrições para este edital estão encerradas"
ERRO_MULTIPLAS_COTAS = "Mais de uma cota associada ao candidato nesta vaga"
ERRO_MULTIPLAS_VAGAS = (
    "Mais de uma inscrição em edital que não permite múltipla inscrição"
)

# ------------------------------
# ERROS - UPLOAD E ARQUIVOS
# ------------------------------
ERRO_ARQUIVO_INVALIDO = "Arquivo inválido"
ERRO_ARQUIVO_SENHA = "O arquivo está protegido com senha"
ERRO_CRIACAO_PASTA_UPLOAD = "Erro na criação da pasta de upload de arquivos"
ERRO_FALTA_ARQUIVO = (
    "Há campos marcados para envio de arquivos que não estão na base de dados"
)
ERRO_GS_NAO_ENCONTRADO = "Executável gs não encontrado"
ERRO_POST_ARQUIVOS = "Erro no POST dos arquivos"

# ------------------------------
# ERROS - CÓDIGOS DE VALIDAÇÃO
# ------------------------------
ERRO_CODIGO_EXPIRADO = "Código expirado"
ERRO_CODIGO_EMAIL = "Código enviado por e-mail não é valido"

# ------------------------------
# ERROS - CAMPOS E VAGAS
# ------------------------------
ERRO_GET_CAMPOS_DA_VAGA = "Não há campos de pontuação para esta vaga"
ERRO_TIPO_CAMPO_INVALIDO = "Tipo de campo inválido"

# ------------------------------
# ERROS - GET DE ENTIDADES
# ------------------------------
ERRO_GET_CANDIDATO = "Erro na obtenção dos dados do candidato"
ERRO_GET_COTA = "Erro na obtenção dos dados de cota"
ERRO_GET_INSCRICAO = "Erro na obtenção dos dados da inscrição"
ERRO_GET_PESSOA_FORMACAO = "Erro na obtenção da formação da pessoa"
ERRO_GET_PESSOA_VAGA_COTA = "Erro na obtenção da associação entre pessoa, vaga e cota"
ERRO_GET_VAGA_COTA = "Cota não encontrada para a vaga especificada"

# ------------------------------
# ERROS - GET DE ENTIDADES
# ------------------------------
ERRO_POST_COTA = "O campo cota é obrigatório"

# ------------------------------
# ERROS - INSERÇÃO
# ------------------------------
ERRO_APRESENTACAO_CM_PESSOA = "Os dados da pessoa são inválidos"
ERRO_INSERCAO_CM_PESSOA = "Houve um erro ao tentar inserir a pessoa"
ERRO_INSERCAO_ED_PESSOA_FORMACAO = "Houve um erro ao tentar inserir a formação"
ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX_FIM_INVALIDO = "Data de fim inválida"
ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX_INICIO_INVALIDO = "Data de início inválida"
ERRO_INSERCAO_ED_PESSOA_VAGA_CAMPO_DATEBOX_OBJETO = (
    "O campo datebox_da_vaga deve ser um objeto"
)
ERRO_INSCRICAO_DATA_FORMACAO_FIM_MAIOR_OU_IGUAL_DATA_FORMACAO_INICIO = (
    "A data de fim deve ser posterior à data de início da formação"
)
ERRO_INSERCAO_ED_PESSOA_VAGA_COTA = "Erro na associação entre pessoa, vaga e cota"
ERRO_INSERCAO_ED_PESSOA_VAGA_INSCRICAO = "Houve um erro ao tentar finalizar a inscrição"

# ------------------------------
# ERROS - REMOÇÃO
# ------------------------------
ERRO_REMOCAO_ED_PESSOA_FORMACAO = "Erro ao apagar formação"
ERRO_REMOCAO_ED_PESSOA_VAGA_COTA = "Erro ao apagar a relação entre pessoa, vaga e cota"

# ------------------------------
# ERROS - ASSINATURA DIGITAL
# ------------------------------
ERRO_VALIDACAO_ASSINATURA_DIGITAL = (
    "Este campo requer documentação assinada digitalmente"
)
ERRO_VALIDACAO_ASSINATURA_DIGITAL_PDF = (
    "Este campo requer um arquivo PDF e assinado digitalmente"
)
ERRO_VERIFICACAO_ASSINATURA_DIGITAL = "Erro na verificação da assinatura digital"

# ------------------------------
# APLICA CONTATO DO SUPORTE EM TODAS AS MENSAGENS DE ERRO
# ------------------------------
for var_name in list(globals()):
    if var_name.startswith("ERRO_"):
        globals()[var_name] += ". " + INFO_ENTRE_CONTATO_SUPORTE

# ------------------------------
# ALERTAS DE INSCRIÇÃO
# ------------------------------
INFO_JA_INSCRITO_MESMA_VAGA = "Você já está inscrito para esta vaga. Se deseja alterar alguma informação, continue o processo até a tela de geração do número de protocolo."
INFO_JA_INSCRITO_MESMO_EDITAL_COM_MULTIPLAS_INSCRICOES = "Você já está inscrito em outra vaga deste edital, que permite múltiplas inscrições. Finalizar esta inscrição não apagará a anterior."
INFO_JA_INSCRITO_MESMO_EDITAL_SEM_MULTIPLAS_INSCRICOES = "Você já está inscrito em outra vaga deste edital. Concluir o processo de inscrição apagará a inscrição anterior."

# ------------------------------
# MENSAGENS DE SUCESSO
# ------------------------------
OK_ATUALIZACAO_ED_PESSOA_INSCRICAO = "Atualizou a inscrição para a pessoa"
OK_CODIGO_EMAIL_ENVIADO = "Código enviado por e-mail"
OK_CODIGO_EMAIL_VALIDADO = "Código enviado por e-mail validado"
OK_ED_PESSOA_VAGA_CAMPOS = "Salvou dados de preenchimento de campos do candidato"
OK_ED_PESSOA_VAGA_CAMPO_UPLOAD = "Salvou os arquivos do candidato"
OK_EMAIL_VALIDADO = "Endereço de email válido"
OK_INSERCAO_CM_PESSOA = "Pessoa criada"
OK_INSERCAO_ED_PESSOA_FORMACAO = "Inseriu a formação para a pessoa"
OK_INSERCAO_ED_PESSOA_INSCRICAO = "Inseriu a inscrição para a pessoa"
OK_PESSOA_ENCONTRADA = "Pessoa encontrada"
OK_PESSOA_NAO_ENCONTRADA = "Pessoa não encontrada na base de dados"
OK_REMOCAO_ED_PESSOA_FORMACAO = "Removeu a formação para a pessoa"
OK_REMOCAO_ED_PESSOA_VAGA_COTA = "Removeu a informação de cotista para a pessoa"
OK_VAGAID_NA_SESSAO = "Identificador da vaga na sessão"
