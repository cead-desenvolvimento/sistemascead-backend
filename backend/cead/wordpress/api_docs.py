from drf_spectacular.utils import OpenApiExample, OpenApiResponse


DOCS_GET_CURSOS_ATIVOS_DO_POLO = {
    "summary": "Lista cursos ativos de um polo",
    "description": "Retorna os cursos ativos associados a um polo pelo nome do polo.",
    "tags": ["Wordpress"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_polo",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do polo.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Cursos ativos do polo encontrados.",
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
        404: OpenApiResponse(
            description="Polo não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"detail": "Polo não encontrado."},
                )
            ],
        ),
    },
}

DOCS_GET_CURSO_CONTATO = {
    "summary": "Contato do curso pelo nome",
    "description": "Retorna dados de contato do curso especificado pelo nome.",
    "tags": ["Wordpress"],
    "parameters": [
        # Se desejar explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_curso",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do curso.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Dados de contato do curso retornados.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "nome": "Matemática",
                        "email": "contato@matematica.ufjf.br",
                        "cm_pessoa_coordenador": {"nome": "João Coordenador"},
                        "telefone_formatado": "(32) 99999-9999",
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            description="Curso não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"detail": "Curso não encontrado."},
                )
            ],
        ),
    },
}

DOCS_GET_CURSO_DESCRICAO_PERFIL_EGRESSO = {
    "summary": "Descrição e perfil do egresso de um curso",
    "description": "Retorna a descrição e perfil do egresso para o curso pelo nome.",
    "tags": ["Wordpress"],
    "parameters": [
        # Se desejar explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_curso",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do curso.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Descrição e perfil do egresso retornados.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "descricao": "Curso focado em formação crítica...",
                        "perfil_egresso": "Profissionais capacitados para...",
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            description="Curso não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"detail": "Curso não encontrado."},
                )
            ],
        ),
    },
}

DOCS_GET_POLOS = {
    "summary": "Lista todos os polos",
    "description": "Retorna todos os polos cadastrados no sistema.",
    "tags": ["Wordpress"],
    "responses": {
        200: OpenApiResponse(
            description="Lista de polos retornada.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {
                            "id": 1,
                            "cm_pessoa_coordenador": "Maria Coordenadora",
                            "nome": "Polo Juiz de Fora",
                            "email": "contato@polo.ufjf.br",
                            "ativo": True,
                            "latitude": -21.7542,
                            "longitude": -43.3492,
                            "apresentacao": "Polo da região sudeste...",
                            "telefone_formatado": "(32) 99999-9999",
                            "logradouro": "Rua Exemplo",
                            "numero": "123",
                            "complemento": "Sala 5",
                            "bairro": "Centro",
                            "cep_formatado": "36000-000",
                            "municipio_uf": "Juiz de Fora/MG",
                        }
                    ],
                )
            ],
        ),
    },
}

DOCS_GET_POLOS_INFORMACOES = {
    "summary": "Consulta informações detalhadas de polos",
    "description": (
        "Recebe uma lista de nomes de polos e retorna informações detalhadas de cada um."
    ),
    "tags": ["Wordpress"],
    "request": {
        "application/json": {
            "type": "object",
            "properties": {
                "polo": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "array", "items": {"type": "string"}},
                    ],
                    "example": ["Polo Juiz de Fora", "Polo Rio de Janeiro"],
                }
            },
            "required": ["polo"],
        }
    },
    "responses": {
        200: OpenApiResponse(
            description="Informações dos polos retornadas.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {
                            "nome": "Polo Juiz de Fora",
                            "email": "contato@polo.ufjf.br",
                            "ativo": True,
                            "latitude": -21.7542,
                            "longitude": -43.3492,
                            "apresentacao": "Polo da região sudeste...",
                            "telefone_formatado": "(32) 99999-9999",
                            "logradouro": "Rua Exemplo",
                            "numero": "123",
                            "complemento": "Sala 5",
                            "bairro": "Centro",
                            "cep_formatado": "36000-000",
                            "municipio_uf": "Juiz de Fora/MG",
                        }
                    ],
                )
            ],
        ),
        400: OpenApiResponse(
            description="Nenhum polo fornecido.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"error": "Nenhum polo fornecido."},
                )
            ],
        ),
    },
}

DOCS_GET_POLOS_IDS = {
    "summary": "Lista de IDs de polos cadastrados",
    "description": "Retorna a lista completa com os IDs de todos os polos cadastrados no sistema.",
    "tags": ["Wordpress"],
    "responses": {
        200: OpenApiResponse(
            description="Lista de IDs de polos retornada.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={"polos_ids": [2727, 2728, 2785]},
                )
            ],
        ),
    },
}

DOCS_GET_POLOS_ATIVOS_DO_CURSO = {
    "summary": "Lista polos ativos de um curso pelo nome do curso",
    "description": "Retorna os polos que possuem ofertas ativas para o curso especificado.",
    "tags": ["Wordpress"],
    "parameters": [
        # Caso queira explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_curso",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do curso.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Polos ativos retornados.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {"nome": "Polo Juiz de Fora"},
                        {"nome": "Polo Rio de Janeiro"},
                    ],
                )
            ],
        ),
        404: OpenApiResponse(
            description="Curso não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"detail": "Curso não encontrado."},
                )
            ],
        ),
    },
}

DOCS_GET_POLO = {
    "summary": "Detalhes completos de um polo pelo nome",
    "description": "Retorna as informações completas de um polo identificado pelo nome.",
    "tags": ["Wordpress"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_polo",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do polo.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Detalhes do polo retornados.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "id": 1,
                        "cm_pessoa_coordenador": "Maria Coordenadora",
                        "nome": "Polo Juiz de Fora",
                        "email": "contato@polo.ufjf.br",
                        "ativo": True,
                        "latitude": -21.7542,
                        "longitude": -43.3492,
                        "apresentacao": "Polo da região sudeste...",
                        "telefone_formatado": "(32) 99999-9999",
                        "logradouro": "Rua Exemplo",
                        "numero": "123",
                        "complemento": "Sala 5",
                        "bairro": "Centro",
                        "cep_formatado": "36000-000",
                        "municipio_uf": "Juiz de Fora/MG",
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            description="Polo não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"detail": "Polo não encontrado."},
                )
            ],
        ),
    },
}

DOCS_GET_POLO_APRESENTACAO = {
    "summary": "Apresentação resumida do polo",
    "description": "Retorna o texto de apresentação do polo pelo nome.",
    "tags": ["Wordpress"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_polo",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do polo.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Texto de apresentação retornado.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value={
                        "apresentacao": "O Polo Juiz de Fora é referência na região..."
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            description="Polo não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"detail": "Polo não encontrado."},
                )
            ],
        ),
    },
}

DOCS_GET_POLO_NOME_COM_OFERTA_ATIVA = {
    "summary": "Nome do polo se houver oferta ativa",
    "description": (
        "Retorna o nome do polo somente se ele possuir alguma oferta ativa atualmente."
    ),
    "tags": ["Wordpress"],
    "parameters": [
        # Caso queira explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_polo",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do polo.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Nome do polo retornado com oferta ativa.",
            examples=[
                OpenApiExample("Exemplo resposta", value={"nome": "Polo Juiz de Fora"}),
            ],
        ),
        404: OpenApiResponse(
            description="Polo não encontrado ou sem oferta ativa.",
            examples=[
                OpenApiExample(
                    "Erro polo não encontrado",
                    value={"detail": "Polo não encontrado."},
                ),
                OpenApiExample(
                    "Erro sem oferta ativa",
                    value={"detail": "Polo sem oferta ativa."},
                ),
            ],
        ),
    },
}

DOCS_GET_POLO_HORARIO_FUNCIONAMENTO = {
    "summary": "Horários de funcionamento do polo",
    "description": "Retorna a lista de horários de funcionamento do polo pelo nome.",
    "tags": ["Wordpress"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="nome_polo",
        #     type=str,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="Nome do polo.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista de horários retornada.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {"dia_semana": 1, "hora_inicio": "08:00", "hora_fim": "12:00"},
                        {"dia_semana": 3, "hora_inicio": "13:00", "hora_fim": "17:00"},
                    ],
                )
            ],
        ),
        404: OpenApiResponse(
            description="Polo não encontrado.",
            examples=[
                OpenApiExample(
                    "Erro",
                    value={"detail": "Polo não encontrado."},
                )
            ],
        ),
    },
}
