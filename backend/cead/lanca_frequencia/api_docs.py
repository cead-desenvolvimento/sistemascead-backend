from drf_spectacular.utils import OpenApiExample, OpenApiResponse


DOCS_LANCA_FREQUENCIA_PREVIA_API_VIEW = {
    "summary": "Prévia do lançamento de frequência",
    "description": (
        "Recebe os dados de frequência selecionados pelo coordenador e retorna uma prévia formatada. "
        "Essa prévia permite ao usuário confirmar visualmente os dados antes de realizar o lançamento definitivo. "
        "Nenhum dado é salvo no banco nesta etapa."
    ),
    "request": {
        "application/json": {
            "example": {
                "bolsistas": [
                    {
                        "ficha_id": 123,
                        "autorizar_pagamento": True,
                        "disciplinas": [10, 11],
                    },
                    {"ficha_id": 456, "autorizar_pagamento": False, "disciplinas": []},
                ]
            }
        }
    },
    "responses": {
        200: {
            "description": "Prévia gerada com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "preview": [
                            {
                                "ficha_id": 123,
                                "nome": "Maria da Silva",
                                "cpf": "123.456.789-00",
                                "funcao": "Tutor",
                                "curso": "Especialização em Gestão Escolar",
                                "autorizar_pagamento": True,
                                "disciplinas": ["Matemática I", "Estatística Aplicada"],
                                "disciplinas_ids": [10, 11],
                            },
                            {
                                "ficha_id": 456,
                                "nome": "João Souza",
                                "cpf": "987.654.321-00",
                                "funcao": "Coordenador de Polo",
                                "curso": "Licenciatura em Pedagogia",
                                "autorizar_pagamento": False,
                                "disciplinas": [],
                                "disciplinas_ids": [],
                            },
                        ]
                    }
                }
            },
        },
        400: {"description": "Erro de requisição, dados inválidos ou vazios"},
        404: {"description": "Ficha ou disciplina não encontrada"},
    },
}


DOCS_LANCA_FREQUENCIA_API_VIEW = {
    "summary": "Lançamento mensal de frequência pelos coordenadores",
    "description": (
        "Permite ao coordenador lançar a frequência mensal dos bolsistas sob sua coordenação. "
        "No GET, traz os bolsistas, disciplinas e fichas do mês anterior. No POST, grava a frequência lançada."
    ),
    "tags": ["Financeiro - Frequência"],
    "responses": {
        200: OpenApiResponse(
            description="Dados necessários para lançamento retornados com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo GET",
                    value=[
                        {
                            "coordenador": {"nome": "João Coordenador"},
                            "curso": {"nome": "Matemática"},
                            "disciplinas_do_curso": [
                                {"id": 1, "nome": "Álgebra"},
                                {"id": 2, "nome": "Cálculo"},
                            ],
                            "bolsistas": [
                                {
                                    "id": 123,
                                    "cm_pessoa": "Maria Bolsista",
                                    "cpf": "111.222.333-44",
                                    "fi_funcao_bolsista": "Tutor",
                                    "disciplinas": [1, 2],
                                }
                            ],
                        }
                    ],
                )
            ],
        ),
        201: OpenApiResponse(
            description="Frequência lançada com sucesso.",
            examples=[
                OpenApiExample(
                    "POST OK", value={"detail": "Frequência lançada com sucesso."}
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação ao lançar frequência.",
            examples=[
                OpenApiExample(
                    "Erro: Sem ficha",
                    value={"detail": "Não há ficha para lançar frequência."},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="Erro ao buscar recursos necessários para lançamento.",
            examples=[
                OpenApiExample(
                    "Erro: Coordenador não encontrado",
                    value={"detail": "Coordenador não encontrado."},
                ),
                OpenApiExample(
                    "Erro: Curso não encontrado",
                    value={"detail": "Curso(s) do coordenador não encontrado(s)."},
                ),
                OpenApiExample(
                    "Erro: Ficha não encontrada",
                    value={"detail": "Ficha não encontrada: 123"},
                ),
                OpenApiExample(
                    "Erro: Disciplina não encontrada",
                    value={"detail": "Disciplina não encontrada: 99"},
                ),
            ],
        ),
        409: OpenApiResponse(
            description="Erro: Frequência já lançada.",
            examples=[
                OpenApiExample(
                    "Erro: Frequência já lançada",
                    value={"detail": "Frequência já lançada."},
                ),
            ],
        ),
        422: OpenApiResponse(
            description="Erro: Fora do período de lançamento.",
            examples=[
                OpenApiExample(
                    "Erro: Fora do período",
                    value={
                        "detail": "Não está em período de lançamento de frequência."
                    },
                ),
            ],
        ),
        500: OpenApiResponse(
            description="Erro interno ao lançar disciplina.",
            examples=[
                OpenApiExample(
                    "Erro: Problema ao lançar disciplina",
                    value={
                        "detail": "Erro ao inserir frequência da disciplina: Exception('erro X')"
                    },
                ),
            ],
        ),
    },
    "request": {
        "application/json": {
            "type": "object",
            "properties": {
                "bolsistas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ficha_id": {"type": "integer", "example": 123},
                            "autorizar_pagamento": {"type": "boolean", "example": True},
                            "disciplinas": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "example": [1, 2],
                            },
                        },
                        "required": ["ficha_id", "autorizar_pagamento", "disciplinas"],
                    },
                }
            },
            "required": ["bolsistas"],
        }
    },
}

DOCS_LISTAR_FI_DATAFREQUENCIA_API_VIEW = {
    "summary": "Lista meses com frequência lançada",
    "description": "Retorna até 6 últimos meses para os quais há frequência lançada (para consulta/relatório).",
    "tags": ["Financeiro - Frequência"],
    "responses": {
        200: OpenApiResponse(
            description="Lista de meses de frequência",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {"id": 42, "mes": 6, "ano": 2024, "mes_ano": "jun/2024"},
                        {"id": 41, "mes": 5, "ano": 2024, "mes_ano": "mai/2024"},
                    ],
                )
            ],
        ),
    },
}

DOCS_LISTAR_CURSOS_COM_DISCIPLINAS_API_VIEW = {
    "summary": "Lista cursos com disciplinas cadastradas",
    "description": "Retorna cursos que possuem pelo menos uma disciplina cadastrada.",
    "tags": ["Financeiro - Frequência"],
    "responses": {
        200: OpenApiResponse(
            description="Cursos com disciplinas",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {"id": 1, "nome": "Matemática"},
                        {"id": 2, "nome": "Física"},
                    ],
                )
            ],
        ),
    },
}

DOCS_DISCIPLINAS_CURSO_API_VIEW = {
    "summary": "Lista ou cadastra disciplinas de um curso",
    "description": "GET retorna todas as disciplinas do curso. POST cadastra uma nova disciplina.",
    "tags": ["Financeiro - Frequência"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="ac_curso_id",
        #     type=int,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="ID do curso.",
        # ),
    ],
    "request": {
        "application/json": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "example": "Algoritmos"},
                "ativa": {"type": "boolean", "example": True},
            },
            "required": ["nome"],
        }
    },
    "responses": {
        200: OpenApiResponse(
            description="Lista de disciplinas do curso",
            examples=[
                OpenApiExample(
                    "Exemplo GET",
                    value=[
                        {"id": 1, "nome": "Álgebra Linear"},
                        {"id": 2, "nome": "Geometria"},
                    ],
                )
            ],
        ),
        201: OpenApiResponse(
            description="Disciplina criada com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo POST",
                    value={"id": 3, "nome": "Algoritmos", "ativa": True, "ac_curso": 1},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Curso não encontrado.",
            examples=[
                OpenApiExample(
                    "Curso não encontrado",
                    value={"detail": "Curso não encontrado."},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação na criação.",
            examples=[
                OpenApiExample(
                    "Erro de validação", value={"nome": ["Este campo é obrigatório."]}
                )
            ],
        ),
    },
}

DOCS_DISCIPLINAS_CURSO_RETRIEVE_UPDATE_DESTROY_API_VIEW = {
    "summary": "Consulta ou atualiza uma disciplina",
    "description": "Permite recuperar ou atualizar (PUT) os dados de uma disciplina.",
    "tags": ["Financeiro - Frequência"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="id",
        #     type=int,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="ID da disciplina.",
        # ),
    ],
    "request": {
        "application/json": {
            "type": "object",
            "properties": {
                "nome": {"type": "string", "example": "Algoritmos"},
                "ativa": {"type": "boolean", "example": True},
                "ac_curso": {"type": "integer", "example": 1},
            },
            "required": ["nome", "ac_curso"],
        }
    },
    "responses": {
        200: OpenApiResponse(
            description="Disciplina consultada/atualizada com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo",
                    value={"id": 3, "nome": "Algoritmos", "ativa": True, "ac_curso": 1},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação.",
            examples=[
                OpenApiExample(
                    "Erro de validação", value={"nome": ["Este campo é obrigatório."]}
                )
            ],
        ),
    },
}

DOCS_RELATORIO_ADMINISTRATIVO_LANCAMENTO_API_VIEW = {
    "summary": "Relatório administrativo de frequência por mês",
    "description": "Traz relatório de lançamentos de frequência do mês informado, com cursos, coordenadores e bolsistas.",
    "tags": ["Financeiro - Frequência"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="fi_datafrequencia_id",
        #     type=int,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="ID do mês da frequência a ser consultada.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Relatório retornado com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "mes_ano_datafrequencia_mes_anterior": "mai/2024",
                        "cursos": [
                            {
                                "coordenador": {"nome": "João Coordenador"},
                                "curso": {"nome": "Matemática"},
                                "bolsistas": [
                                    {
                                        "cm_pessoa": "Maria Bolsista",
                                        "cpf": "111.222.333-44",
                                        "fi_funcao_bolsista": "Tutor",
                                        "disciplinas": [
                                            {"nome": "Álgebra Linear"},
                                            {"nome": "Cálculo"},
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro de parâmetro ou permissão.",
            examples=[
                OpenApiExample(
                    "Datafrequência obrigatória",
                    value={"detail": "Datafrequência obrigatória."},
                ),
                OpenApiExample(
                    "Datafrequência não permitida",
                    value={"detail": "Datafrequência antiga não permitida."},
                ),
                OpenApiExample(
                    "Datafrequência vazia",
                    value={
                        "detail": "Datafrequência vazia: 99",
                    },
                ),
                OpenApiExample(
                    "Erro ao buscar cursos",
                    value={"detail": "Erro ao buscar cursos."},
                ),
            ],
        ),
    },
}

DOCS_RELATORIO_LANCAMENTO_API_VIEW = {
    "summary": "Relatório pessoal de lançamentos do coordenador",
    "description": (
        "Retorna o relatório de lançamentos de frequência do mês atual para o coordenador autenticado. "
        "Inclui cursos sob sua coordenação, bolsistas vinculados e disciplinas associadas."
    ),
    "tags": ["Financeiro - Frequência"],
    "responses": {
        200: OpenApiResponse(
            description="Relatório do coordenador retornado.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "mes_ano_datafrequencia_mes_anterior": "mai/2024",
                        "cursos": [
                            {
                                "coordenador": {"nome": "João Coordenador"},
                                "curso": {"id": 1, "nome": "Matemática"},
                                "bolsistas": [
                                    {
                                        "cm_pessoa": "Maria Bolsista",
                                        "cpf": "111.222.333-44",
                                        "fi_funcao_bolsista": "Tutor",
                                        "disciplinas": [
                                            {"nome": "Álgebra Linear"},
                                            {"nome": "Cálculo"},
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro ao buscar cursos do coordenador.",
            examples=[
                OpenApiExample(
                    "Erro ao buscar cursos",
                    value={"detail": "Erro ao buscar cursos do coordenador."},
                )
            ],
        ),
    },
}
