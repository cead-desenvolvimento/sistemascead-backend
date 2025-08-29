from drf_spectacular.utils import OpenApiExample, OpenApiResponse


DOCS_LISTAR_FI_DATAFREQUENCIA_MOODLE_API_VIEW = {
    "summary": "Lista meses com acesso registrado no Moodle",
    "description": "Retorna os meses (FiDatafrequencia) que possuem registros de acesso no Moodle para relatórios.",
    "tags": ["Financeiro - Relatório Moodle"],
    "responses": {
        200: OpenApiResponse(
            description="Meses com registros de acesso no Moodle.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {"id": 42, "descricao": "jun/2024"},
                        {"id": 41, "descricao": "mai/2024"},
                    ],
                )
            ],
        ),
    },
}

DOCS_SELECAO_CURSOS_RELATORIO_MOODLE_API_VIEW = {
    "summary": "Lista cursos para o mês selecionado no relatório Moodle",
    "description": (
        "Retorna os cursos que possuem registros de acesso no Moodle para o mês (fi_datafrequencia_id) informado."
    ),
    "tags": ["Financeiro - Relatório Moodle"],
    "parameters": [
        # Se quiser explicitar o parâmetro de rota:
        # OpenApiParameter(
        #     name="fi_datafrequencia_id",
        #     type=int,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="ID do mês para filtro do relatório Moodle.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Cursos disponíveis para o mês informado.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {
                            "ac_curso_oferta__ac_curso__id": 1,
                            "ac_curso_oferta__ac_curso__nome": "Matemática",
                        },
                        {
                            "ac_curso_oferta__ac_curso__id": 2,
                            "ac_curso_oferta__ac_curso__nome": "Física",
                        },
                    ],
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro ao buscar datafrequência.",
            examples=[
                OpenApiExample(
                    "Erro datafrequencia inválida",
                    value={"detail": "Datafrequência inválida."},
                )
            ],
        ),
    },
}

DOCS_RELATORIO_MOODLE_API_VIEW = {
    "summary": "Relatório detalhado de acessos no Moodle",
    "description": (
        "Retorna os registros de acesso no Moodle filtrados por mês (fi_datafrequencia_id) e opcionalmente por cursos."
    ),
    "tags": ["Financeiro - Relatório Moodle"],
    "parameters": [
        # Exemplo de parâmetros, se quiser explicitar:
        # OpenApiParameter(
        #     name="fi_datafrequencia_id",
        #     type=int,
        #     location=OpenApiParameter.PATH,
        #     required=True,
        #     description="ID do mês para filtro do relatório Moodle.",
        # ),
        # OpenApiParameter(
        #     name="cursos",
        #     type=str,
        #     location=OpenApiParameter.QUERY,
        #     required=False,
        #     description="Lista de IDs de cursos separados por vírgula para filtrar.",
        # ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Registros detalhados de acessos no Moodle.",
            examples=[
                OpenApiExample(
                    "Exemplo resposta",
                    value=[
                        {
                            "coordenador": "João Coordenador 123.456.789-00",
                            "cursos": [
                                {
                                    "id": 1,
                                    "nome": "Matemática",
                                    "pessoas": [
                                        {
                                            "pessoa": "Maria Bolsista 111.222.333-44",
                                            "registros": [
                                                {
                                                    "moodle_id": 987,
                                                    "ultimo_acesso": "2024-06-18T10:00:00Z",
                                                    "data_consulta": "2024-06-19T08:00:00Z",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                )
            ],
        ),
        400: OpenApiResponse(
            description="Erro ao buscar datafrequência.",
            examples=[
                OpenApiExample(
                    "Erro datafrequencia inválida",
                    value={"detail": "Datafrequência inválida."},
                )
            ],
        ),
    },
}
