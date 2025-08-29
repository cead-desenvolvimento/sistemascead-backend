from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from cead.serializers import CPFSerializer, GetPessoaEmailSerializer
from .serializers import *

DOCS_EDITAIS_FASE_INSCRICAO_VIEW = {
    "summary": "Lista editais abertos para inscrição",
    "description": "Retorna todos os editais que estão na fase de inscrição (data atual entre início e fim).",
    "tags": ["Inscrição"],
    "responses": {
        200: OpenApiResponse(
            response=GetEditaisSerializer(many=True),
            description="Lista de editais em fase de inscrição.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {
                            "id": 1,
                            "numero": "05",
                            "ano": "2024",
                            "descricao": "Edital 05/2024",
                            "vagas": [
                                {"id": 10, "descricao": "Professor", "quantidade": 5},
                                {"id": 11, "descricao": "Tutor", "quantidade": 3},
                            ],
                        }
                    ],
                )
            ],
        )
    },
}

DOCS_VAGAS_EDITAL_FASE_INSCRICAO_VIEW = {
    "summary": "Lista vagas de um edital aberto",
    "description": (
        "**GET:** Retorna todas as vagas de um edital se a fase de inscrição estiver aberta.\n\n"
        "**POST:** Coloca na sessão qual vaga o candidato escolheu."
    ),
    "tags": ["Inscrição"],
    # Se quiser, pode adicionar os parâmetros de rota (ano, numero) aqui.
    "responses": {
        200: OpenApiResponse(
            response=GetVagasSerializer(many=True),
            description="Lista de vagas do edital.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {"id": 10, "descricao": "Professor", "quantidade": 5},
                        {"id": 11, "descricao": "Tutor", "quantidade": 3},
                    ],
                ),
                OpenApiExample(
                    "Vaga marcada",
                    value={"detail": "Vaga marcada na sessão com sucesso."},
                ),
            ],
        ),
        302: OpenApiResponse(
            description="Inscrições encerradas para o edital.",
            examples=[
                OpenApiExample(
                    "Inscrições encerradas",
                    value={"detail": "Inscrições encerradas para este edital."},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Edital ou vaga não encontrada.",
            examples=[
                OpenApiExample(
                    "Edital não encontrado", value={"detail": "Edital não encontrado."}
                ),
                OpenApiExample(
                    "Vaga não encontrada", value={"detail": "Vaga não encontrada."}
                ),
            ],
        ),
        500: OpenApiResponse(
            description="Erro interno ou múltiplos editais.",
            examples=[
                OpenApiExample(
                    "Múltiplos editais",
                    value={"detail": "Mais de um edital encontrado."},
                ),
                OpenApiExample(
                    "Erro ao buscar vagas",
                    value={"detail": "Erro ao buscar vagas: erro qualquer"},
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Requisição malformada.",
            examples=[
                OpenApiExample(
                    "Vaga id ausente", value={"detail": "ID da vaga não informado."}
                ),
            ],
        ),
    },
}

DOCS_VALIDAR_CPF_VIEW = {
    "summary": "Valida CPF para inscrição na vaga",
    "description": "Valida o CPF informado, verifica existência na base e requisitos de sessão. Armazena o candidato na sessão se válido.",
    "tags": ["Inscrição"],
    "request": CPFSerializer,
    "responses": {
        200: OpenApiResponse(
            description="CPF válido e candidato encontrado.",
            examples=[
                OpenApiExample(
                    "Pessoa encontrada",
                    value={"detail": "Pessoa encontrada com sucesso."},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="CPF válido mas não cadastrado.",
            examples=[
                OpenApiExample(
                    "Pessoa não encontrada",
                    value={"detail": "Pessoa não cadastrada.", "cpf": "12345678901"},
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação de CPF ou sessão.",
            examples=[
                OpenApiExample("CPF inválido", value={"cpf": ["CPF inválido."]}),
                OpenApiExample(
                    "Sessão inválida",
                    value={"detail": "Vaga não selecionada na sessão."},
                ),
            ],
        ),
    },
}

DOCS_CRIAR_PESSOA_VIEW = {
    "summary": "Cadastra nova pessoa para inscrição",
    "description": "Cria um novo registro de pessoa se não existir, já vinculado à sessão.",
    "tags": ["Inscrição"],
    "request": CmPessoaPostSerializer,
    "responses": {
        201: OpenApiResponse(
            description="Pessoa criada com sucesso.",
            examples=[
                OpenApiExample(
                    "Pessoa criada",
                    value={"detail": "Pessoa criada com sucesso.", "pessoa_id": 1},
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação ou apresentação.",
            examples=[
                OpenApiExample(
                    "Erro de apresentação",
                    value={
                        "detail": "Erro na apresentação de dados.",
                        "errors": {"nome": ["Nome obrigatório"]},
                    },
                ),
            ],
        ),
        500: OpenApiResponse(
            description="Erro interno na criação.",
            examples=[
                OpenApiExample(
                    "Erro de inserção",
                    value={"detail": "Erro ao inserir pessoa: algum erro"},
                ),
            ],
        ),
    },
}

DOCS_ENVIAR_CODIGO_EMAIL_VIEW = {
    "summary": "Envia código de validação por e-mail",
    "description": (
        "Envia um código de verificação para o e-mail do candidato da sessão. "
        "Gera o código de acordo com o hash e bloco de tempo.\n\n"
        "**GET:** Retorna informações truncadas para exibir mensagem de sucesso.\n\n"
        "**POST:** Envia o código."
    ),
    "tags": ["Inscrição"],
    "responses": {
        "GET": OpenApiResponse(
            response=GetPessoaEmailSerializer,
            description="Dados truncados do candidato.",
        ),
        "POST": OpenApiResponse(
            description="Código enviado com sucesso.",
            examples=[
                OpenApiExample(
                    "Código enviado",
                    value={"detail": "Código enviado por e-mail com sucesso."},
                )
            ],
        ),
    },
}

DOCS_VERIFICAR_CODIGO_VIEW = {
    "summary": "Valida código enviado por e-mail",
    "description": "Valida o código digitado pelo candidato para liberar acesso ao restante da inscrição.",
    "tags": ["Inscrição"],
    "request": {
        "application/json": {
            "type": "object",
            "properties": {"codigo": {"type": "string", "maxLength": 5}},
            "required": ["codigo"],
        }
    },
    "responses": {
        200: OpenApiResponse(
            description="Código validado com sucesso.",
            examples=[
                OpenApiExample(
                    "Código validado", value={"detail": "Código validado com sucesso."}
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de código ausente, expirado ou incorreto.",
            examples=[
                OpenApiExample(
                    "Código ausente", value={"detail": "Código não informado."}
                ),
                OpenApiExample("Código expirado", value={"detail": "Código expirado."}),
                OpenApiExample(
                    "Código incorreto", value={"detail": "Código incorreto."}
                ),
            ],
        ),
    },
}

DOCS_ASSOCIAR_PESSOA_VAGA_COTA_VIEW = {
    "summary": "Consulta, marca ou remove cota da vaga do candidato",
    "description": "Permite listar cotas disponíveis, marcar uma cota na inscrição do candidato ou removê-la.",
    "tags": ["Inscrição"],
    "request": {
        "application/json": {
            "type": "object",
            "properties": {"cota": {"type": "integer"}},
            "required": ["cota"],
        }
    },
    "responses": {
        200: OpenApiResponse(
            response=PessoaVagaCotaSerializer,
            description="Consulta de cotas feita com sucesso ou remoção de cota realizada.",
        ),
        201: OpenApiResponse(
            response=CotaMarcadaSerializer,
            description="Cota marcada com sucesso.",
        ),
        400: OpenApiResponse(
            description="Erro ao marcar ou remover cota.",
            examples=[
                OpenApiExample(
                    "Erro marcar cota", value={"detail": "Erro ao marcar cota."}
                ),
                OpenApiExample(
                    "Erro remover cota", value={"detail": "Erro ao remover cota."}
                ),
            ],
        ),
        404: OpenApiResponse(
            description="Cota do candidato não encontrada.",
            examples=[
                OpenApiExample(
                    "Cota não encontrada",
                    value={"detail": "Cota do candidato não encontrada."},
                )
            ],
        ),
    },
}

DOCS_LISTAR_PESSOA_FORMACAO_VIEW = {
    "summary": "Lista, adiciona ou remove formação acadêmica da pessoa",
    "description": "Permite consultar, adicionar ou remover formações do candidato da inscrição.",
    "tags": ["Inscrição"],
    "responses": {
        200: OpenApiResponse(
            description="Consulta de formações do candidato ou remoção feita com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "pessoa_formacoes": [
                            {
                                "id": 1,
                                "titulacao": "Mestre",
                                "formacao": "Educação",
                                "inicio": "2012-01-01",
                                "fim": "2014-01-01",
                            }
                        ]
                    },
                ),
                OpenApiExample(
                    "Removida", value={"detail": "Formação removida com sucesso."}
                ),
            ],
        ),
        201: OpenApiResponse(
            description="Formação adicionada com sucesso.",
            examples=[
                OpenApiExample(
                    "Formação adicionada",
                    value={"detail": "Formação adicionada com sucesso."},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro ao inserir ou remover formação.",
            examples=[
                OpenApiExample(
                    "Erro ao inserir",
                    value={"detail": "Erro ao inserir formação: erro"},
                ),
                OpenApiExample(
                    "Erro ao remover",
                    value={"detail": "Erro ao remover formação: erro"},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="Formação não encontrada.",
            examples=[
                OpenApiExample(
                    "Não encontrada", value={"detail": "Formação não encontrada."}
                ),
            ],
        ),
    },
}

DOCS_LISTAR_FORMACAO_VIEW = {
    "summary": "Lista todas as formações acadêmicas disponíveis",
    "description": "Permite pesquisar por todas as formações possíveis para adicionar ao currículo da inscrição.",
    "tags": ["Inscrição"],
    "parameters": [
        # parâmetro de query string (?termo=...), se quiser explicitar:
        # OpenApiParameter(
        #     name="termo",
        #     type=str,
        #     location=OpenApiParameter.QUERY,
        #     required=False,
        #     description="Termo para busca nas formações.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de formações disponíveis.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "formacoes_disponiveis": [
                            {"id": 1, "titulacao_nome": "Pedagogia (Graduação)"},
                            {"id": 2, "titulacao_nome": "Matemática (Mestrado)"},
                        ]
                    },
                )
            ],
        ),
    },
}

DOCS_ALERTA_INSCRICAO_VIEW = {
    "summary": "Informa status de inscrição do candidato",
    "description": "Retorna alertas se o candidato já está inscrito nesta vaga ou em outra do mesmo edital.",
    "tags": ["Inscrição"],
    "responses": {
        200: OpenApiResponse(
            description="Status de inscrição do candidato.",
            examples=[
                OpenApiExample(
                    "Já inscrito nesta vaga",
                    value={"alerta_inscricao": "Já está inscrito nesta vaga."},
                ),
                OpenApiExample(
                    "Já inscrito no mesmo edital (com múltiplas inscrições)",
                    value={
                        "alerta_inscricao": "Já está inscrito em outra vaga deste edital (com múltiplas inscrições permitidas)."
                    },
                ),
                OpenApiExample(
                    "Já inscrito no mesmo edital (sem múltiplas inscrições)",
                    value={
                        "alerta_inscricao": "Já está inscrito em outra vaga deste edital (sem múltiplas inscrições permitidas)."
                    },
                ),
                OpenApiExample("Não inscrito", value={"alerta_inscricao": None}),
            ],
        ),
        400: OpenApiResponse(
            description="Mais de uma vaga encontrada para os dados informados.",
            examples=[
                OpenApiExample(
                    "Erro múltiplas vagas",
                    value={
                        "detail": "Mais de uma vaga encontrada para os dados informados."
                    },
                ),
            ],
        ),
    },
}

DOCS_VAGA_CAMPOS_VIEW = {
    "summary": "Lista os campos exigidos na vaga",
    "description": "Retorna os campos (checkbox, combobox, datebox) exigidos para preenchimento na inscrição da vaga selecionada.",
    "tags": ["Inscrição"],
    "responses": {
        200: OpenApiResponse(
            description="Campos da vaga retornados.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "checkboxes": [
                            {
                                "id": 1,
                                "descricao": "Tempo de experiência",
                                "pontuacao": 10,
                                "obrigatorio": True,
                            }
                        ],
                        "comboboxes": {
                            "Certificados": [
                                {
                                    "id": 2,
                                    "descricao": "Certificado A",
                                    "pontuacao": 5,
                                    "obrigatorio": True,
                                }
                            ]
                        },
                        "dateboxes": [
                            {
                                "id": 3,
                                "descricao": "Experiência EAD",
                                "fracao_pontuacao": 2,
                                "multiplicador_fracao_pontuacao": 365,
                                "pontuacao_maxima": 20,
                            }
                        ],
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            description="Erro ao buscar campos da vaga.",
            examples=[
                OpenApiExample(
                    "Erro campos", value={"message": "Erro ao buscar campos da vaga."}
                )
            ],
        ),
    },
}

DOCS_PESSOA_VAGA_CAMPO_VIEW = {
    "summary": "Consulta e marca campos preenchidos pelo candidato",
    "description": (
        "Consulta e marca quais campos da vaga foram preenchidos pelo candidato, registrando a pontuação.<br><br>"
        "**GET:** Retorna os campos já preenchidos ou pendentes para o candidato.<br>"
        "**POST:** Marca os campos informados e atualiza a pontuação do candidato.<br>"
        "<br>"
        "**Formato do retorno:**<br>"
        " - `checkboxes`: lista dos campos de checkbox preenchidos.<br>"
        " - `comboboxes`: lista dos campos de combobox preenchidos.<br>"
        " - `dateboxes`: lista dos campos de datebox preenchidos.<br>"
    ),
    "tags": ["Inscrição"],
    "request": PessoaVagaCampoRequestSerializer,
    "responses": {
        200: PessoaVagaCampoResponseSerializer,
        201: OpenApiResponse(
            description="Campos preenchidos/marcados com sucesso.",
            examples=[
                OpenApiExample(
                    "Campos marcados",
                    value={"detail": "Campos marcados com sucesso."},
                    summary="Campos registrados",
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro ao registrar marcação de campo.",
            examples=[
                OpenApiExample(
                    "Erro checkbox",
                    value={"detail": "Erro ao inserir campo checkbox: já marcado."},
                    summary="Erro ao marcar checkbox",
                ),
                OpenApiExample(
                    "Erro combobox",
                    value={"detail": "Erro ao inserir campo combobox: valor inválido."},
                    summary="Erro ao marcar combobox",
                ),
                OpenApiExample(
                    "Erro datebox",
                    value={"detail": "Erro ao inserir campo datebox: data inválida."},
                    summary="Erro ao marcar datebox",
                ),
            ],
        ),
    },
}

DOCS_BAIXAR_ARQUIVO_INSCRICAO_VIEW = {
    "summary": "Baixa arquivo enviado na inscrição",
    "description": "Permite baixar o arquivo (PDF ou imagem) enviado pelo candidato em algum campo da inscrição.",
    "tags": ["Inscrição"],
    "parameters": [
        # Se quiser detalhar:
        # OpenApiParameter(
        #     name="caminho",
        #     type=str,
        #     location=OpenApiParameter.QUERY,
        #     required=True,
        #     description="Caminho do arquivo na inscrição.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Arquivo enviado para download.",
            examples=[OpenApiExample("Arquivo", value={"file": "..."})],
        ),
        403: OpenApiResponse(
            description="Arquivo não pertence ao candidato ou formato inválido.",
            examples=[
                OpenApiExample(
                    "Erro arquivo",
                    value={"detail": "Arquivo não autorizado ou inválido."},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Arquivo não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro arquivo", value={"detail": "Arquivo não encontrado."}
                )
            ],
        ),
    },
}

DOCS_ANEXAR_ARQUIVOS_VIEW = {
    "summary": "Anexa arquivos aos campos da inscrição",
    "description": (
        "**GET:** Retorna os arquivos já anexados.\n\n"
        "**POST:** Salva ou atualiza os arquivos do candidato."
    ),
    "tags": ["Inscrição"],
    "request": {
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "checkbox_1": {"type": "string", "format": "binary"},
                "combobox_2": {"type": "string", "format": "binary"},
                "datebox_3": {"type": "string", "format": "binary"},
            },
        }
    },
    "responses": {
        200: OpenApiResponse(
            description="Arquivos anexados com sucesso.",
            examples=[
                OpenApiExample(
                    "Arquivos anexados",
                    value={"detail": "Arquivos anexados com sucesso."},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro ao anexar arquivo.",
            examples=[
                OpenApiExample(
                    "Erro tipo campo", value={"detail": "Tipo de campo inválido."}
                ),
                OpenApiExample(
                    "Erro criar pasta",
                    value={"detail": "Erro ao criar pasta de upload: erro"},
                ),
                OpenApiExample(
                    "Arquivo inválido",
                    value={"detail": "Arquivo inválido: erro"},
                ),
            ],
        ),
        500: OpenApiResponse(
            description="Erro interno ao anexar.",
        ),
    },
}

DOCS_FINALIZAR_INSCRICAO_VIEW = {
    "summary": "Finaliza inscrição do candidato na vaga",
    "description": (
        "Finaliza o processo de inscrição do candidato na vaga selecionada. "
        "Grava a pontuação final e a data de submissão. Requer que todas as etapas anteriores estejam válidas na sessão. "
        "Se faltar algum arquivo obrigatório, retorna erro."
    ),
    "tags": ["Inscrição"],
    "responses": {
        201: OpenApiResponse(
            description="Inscrição criada com sucesso.",
            examples=[
                OpenApiExample(
                    "Inscrição criada",
                    value={"sucesso": True, "detail": "Inscrição criada com sucesso."},
                )
            ],
        ),
        200: OpenApiResponse(
            description="Inscrição atualizada com sucesso.",
            examples=[
                OpenApiExample(
                    "Inscrição atualizada",
                    value={
                        "sucesso": True,
                        "detail": "Inscrição atualizada com sucesso.",
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro ao finalizar inscrição.",
            examples=[
                OpenApiExample(
                    "Falta arquivo obrigatório",
                    value={
                        "detail": "Faltam arquivos obrigatórios: ['checkbox_10', 'combobox_22']"
                    },
                ),
                OpenApiExample(
                    "Erro ao inserir inscrição",
                    value={
                        "sucesso": False,
                        "detail": "Erro ao inserir inscrição: descrição do erro",
                    },
                ),
            ],
        ),
    },
}

DOCS_GET_INSCRICAO_VIEW = {
    "summary": "Consulta os dados da inscrição do candidato",
    "description": (
        "Retorna os dados da inscrição do candidato na vaga atualmente selecionada na sessão. "
        "Inclui pontuação, data e informações gerais da inscrição."
    ),
    "tags": ["Inscrição"],
    "responses": {
        200: OpenApiResponse(
            description="Dados da inscrição encontrados com sucesso.",
            examples=[
                OpenApiExample(
                    "Inscrição encontrada",
                    value={
                        "cm_pessoa_id": 123,
                        "ed_vaga_id": 456,
                        "pontuacao": 25,
                        "data": "2024-06-19T18:30:00Z",
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            description="Inscrição não encontrada.",
            examples=[
                OpenApiExample(
                    "Inscrição não encontrada",
                    value={"detail": "Inscrição não encontrada."},
                )
            ],
        ),
    },
}
