from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse

from cead.serializers import (
    AcCursoIdNomeSerializer,
    AcCursoOfertaIdDescricaoSerializer,
)
from .serializers import *

DOCS_LISTAR_CURSOS_COM_BOLSISTAS_ATIVOS_APIVIEW = {
    "summary": "Lista cursos com bolsistas ativos",
    "description": (
        "Retorna todos os cursos que possuem pelo menos um bolsista ativo atualmente (vínculo não encerrado e oferta vinculada)."
    ),
    "tags": ["Financeiro - Vínculos"],
    "responses": {
        200: OpenApiResponse(
            response=AcCursoIdNomeSerializer(many=True),
            description="Lista de cursos com bolsistas ativos.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {"id": 1, "nome": "Licenciatura em Matemática"},
                        {"id": 2, "nome": "Licenciatura em Computação"},
                    ],
                )
            ],
        )
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_CURSOS_COM_BOLSISTAS_INATIVOS_APIVIEW = {
    "summary": "Listar cursos com bolsistas inativos",
    "description": (
        "Retorna a lista de cursos que possuem pelo menos um bolsista inativo, "
        "ou seja, fichas vinculadas ao curso que já foram encerradas "
        "(com `data_fim_vinculacao` preenchida)."
    ),
    "responses": {
        200: {
            "description": "Lista de cursos encontrados",
            "examples": {
                "application/json": [
                    {"id": 10, "nome": "Licenciatura em Matemática"},
                    {"id": 12, "nome": "Engenharia de Produção"},
                ]
            },
        },
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão"},
    },
    "tags": ["Financeiro - Bolsistas"],
}


DOCS_CURSO_COM_BOLSISTAS_ATIVOS_APIVIEW = {
    "summary": "Lista bolsistas ativos de um curso",
    "description": (
        "Retorna todos os bolsistas (pessoas com ficha ativa) vinculados ao curso informado, com dados detalhados de cada bolsista."
    ),
    "tags": ["Financeiro - Vínculos"],
    "parameters": [
        OpenApiParameter(
            name="ac_curso_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID do curso para consultar os bolsistas ativos.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=BolsistaSerializer(many=True),
            description="Lista de bolsistas ativos do curso.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {
                            "id": 101,
                            "nome": "Pessoa 1",
                            "cpf": "12345678901",
                            "email": "pessoa1@gmail.com",
                            "data_inicio_vinculacao": "2024-01-10",
                            # ... outros campos do BolsistaSerializer ...
                        }
                    ],
                )
            ],
        ),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_CURSO_COM_BOLSISTAS_INATIVOS_APIVIEW = {
    "summary": "Listar bolsistas inativos de um curso",
    "description": (
        "Retorna a lista de bolsistas inativos associados a um curso específico. "
        "Considera-se inativo aquele cuja ficha ainda não possui data de início de vinculação (`data_inicio_vinculacao` nula)."
    ),
    "parameters": [
        {
            "name": "ac_curso_id",
            "in": "path",
            "required": True,
            "description": "ID do curso para buscar bolsistas inativos",
            "schema": {"type": "integer"},
        }
    ],
    "responses": {
        200: {
            "description": "Lista de bolsistas inativos do curso",
            "examples": {
                "application/json": [
                    {
                        "id": 101,
                        "nome": "Maria da Silva",
                        "edital": "Edital 11/2025",
                        "data_inicio_vinculacao": None,
                        "data_fim_vinculacao": None,
                    },
                    {
                        "id": 102,
                        "nome": "João Pereira",
                        "edital": "Edital 16/2025",
                        "data_inicio_vinculacao": None,
                        "data_fim_vinculacao": None,
                    },
                ]
            },
        },
        401: {"description": "Não autenticado"},
        403: {"description": "Sem permissão"},
        404: {"description": "Curso não encontrado"},
    },
    "tags": ["Financeiro - Bolsistas"],
}

DOCS_LISTAR_FICHAS_POR_NOME_OU_CPF = {
    "summary": "Busca pessoas e suas fichas por nome ou CPF",
    "description": (
        "Localiza pessoas a partir do nome ou CPF e retorna a lista de fichas "
        "associadas a cada pessoa. "
        "Cada pessoa aparece apenas uma vez no resultado, com suas fichas agrupadas."
    ),
    "tags": ["Financeiro - Fichas"],
    "responses": {
        200: OpenApiResponse(
            response=CmPessoaComFichasSerializer,
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {
                            "id": 9220,
                            "nome": "Maria da Silva",
                            "cpf": "12345678901",
                            "fichas": [
                                {
                                    "id": 501,
                                    "edital": "Edital 01/2025",
                                    "funcao": "Tutor a Distância",
                                    "curso_oferta": "Oferta X do curso Y",
                                    "data_inicio_vinculacao": "2025-02-01",
                                    "data_fim_vinculacao": None,
                                },
                                {
                                    "id": 438,
                                    "edital": "Edital 02/2024",
                                    "funcao": "Coordenador de Polo",
                                    "curso_oferta": "Oferta X do curso Y",
                                    "data_inicio_vinculacao": "2024-08-01",
                                    "data_fim_vinculacao": "2024-12-31",
                                },
                            ],
                        }
                    ],
                )
            ],
        )
    },
}

DOCS_LISTAR_ULTIMAS_FICHAS_APIVIEW = {
    "summary": "Lista as últimas fichas cadastradas",
    "description": (
        "Retorna uma lista dos bolsistas referentes às fichas mais recentes cadastradas no sistema, "
        "permitindo ao administrador visualizar rapidamente as inscrições recém-efetuadas."
    ),
    "tags": ["Financeiro - Vínculos"],
    "responses": {
        200: OpenApiResponse(
            response=BolsistaSerializer(many=True),
            description="Lista dos bolsistas das últimas fichas cadastradas.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {
                            "id": 101,
                            "nome": "Pessoa 1",
                            "cpf": "12345678901",
                            "email": "pessoa1@gmail.com",
                            "data_inicio_vinculacao": "2024-01-10",
                            # ... outros campos do BolsistaSerializer ...
                        },
                        {
                            "id": 102,
                            "nome": "Maria Eduarda",
                            "cpf": "98765432100",
                            "email": "mariaeduarda@gmail.com",
                            "data_inicio_vinculacao": "2024-01-09",
                        },
                    ],
                )
            ],
        )
    },
    "auth": [{"type": "bearer"}],
}

DOCS_ATUALIZAR_DATA_VINCULO_BOLSISTA_APIVIEW = {
    "summary": "Atualiza datas de início ou fim do vínculo do bolsista",
    "description": (
        "Permite alterar as datas de início e/ou fim do vínculo de um bolsista, informando o ID da ficha e as novas datas no corpo da requisição."
    ),
    "tags": ["Financeiro - Vínculos"],
    "request": AtualizarDataVinculoSerializer,
    "responses": {
        200: OpenApiResponse(
            response=BolsistaSerializer,
            description="Ficha atualizada com sucesso. Retorna os dados completos do bolsista.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta (ficha atualizada)",
                    value={
                        "id": 101,
                        "nome": "Pessoa 1",
                        "cpf": "12345678901",
                        "email": "pessoa1@gmail.com",
                        "data_inicio_vinculacao": "2024-01-10",
                        "data_fim_vinculacao": "2024-06-19",
                        # ... outros campos do BolsistaSerializer ...
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Dados inválidos ou identificador não informado.",
            examples=[
                OpenApiExample(
                    "Identificador obrigatório",
                    value={"detail": ["Identificador da ficha obrigatório."]},
                ),
                OpenApiExample(
                    "Erro de validação",
                    value={"data_inicio_vinculacao": ["Data inválida."]},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="Ficha não encontrada.",
            examples=[
                OpenApiExample(
                    "Ficha não encontrada",
                    value={"detail": ["Ficha não encontrada."]},
                )
            ],
        ),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_ATUALIZAR_FICHA = {
    "summary": "Atualiza datas de vinculação da ficha",
    "description": (
        "Permite ao financeiro editar `data_inicio_vinculacao` e "
        "`data_fim_vinculacao` de uma ficha de bolsista."
    ),
    "tags": ["Financeiro - Fichas"],
    "request": FiPessoaFichaEdicaoFinanceiroSerializer,
    "responses": {
        200: OpenApiResponse(
            response=None,
            description="Ficha atualizada com sucesso",
            examples=[
                OpenApiExample(
                    "Exemplo de sucesso",
                    value={"detail": "Ficha atualizada com sucesso"},
                )
            ],
        ),
        400: OpenApiResponse(
            response=None,
            description="Erro de validação",
            examples=[
                OpenApiExample(
                    "Exemplo de erro",
                    value={"detail": "ID da ficha é obrigatório"},
                )
            ],
        ),
        404: OpenApiResponse(
            response=None,
            description="Ficha não encontrada",
            examples=[
                OpenApiExample(
                    "Exemplo de erro",
                    value={"detail": "Ficha não encontrada"},
                )
            ],
        ),
    },
}

DOCS_DETALHAR_FICHA = {
    "summary": "Detalha uma ficha de bolsista",
    "description": (
        "Retorna as informações de uma ficha específica de bolsista, "
        "incluindo edital, função, curso/oferta e datas de vinculação. "
        "Esse endpoint deve ser usado para carregar os dados antes da edição."
    ),
    "tags": ["Financeiro - Fichas"],
    "responses": {
        200: OpenApiResponse(
            response=FiPessoaFichaEdicaoFinanceiroSerializer,
            description="Dados da ficha retornados com sucesso",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value={
                        "id": 501,
                        "edital": "Edital 01/2025",
                        "funcao": "Tutor a Distância",
                        "curso_oferta": "Matemática - Oferta 2025/1",
                        "data_inicio_vinculacao": "2025-02-01",
                        "data_fim_vinculacao": None,
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            response=None,
            description="Ficha não encontrada",
            examples=[
                OpenApiExample(
                    "Exemplo de erro",
                    value={"detail": "Ficha não encontrada"},
                )
            ],
        ),
    },
}

DOCS_LISTAR_EDITAIS_ATUAIS_APIVIEW = {
    "summary": "Lista editais atuais",
    "description": (
        "Retorna todos os editais com data de validade igual ou superior à data atual, ordenados do mais recente para o mais antigo."
    ),
    "tags": ["Financeiro - Vínculos"],
    "responses": {
        200: OpenApiResponse(
            response=EdEditalSerializer(many=True),
            description="Lista de editais válidos atualmente.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {"id": 23, "descricao": "05/2024"},
                        {"id": 22, "descricao": "04/2024"},
                    ],
                )
            ],
        )
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_OFERTAS_ATUAIS_APIVIEW = {
    "summary": "Lista ofertas atuais de curso",
    "description": (
        "Retorna todas as ofertas de curso com data de término igual ou superior à data atual, ordenadas do mais recente para o mais antigo."
    ),
    "tags": ["Financeiro - Vínculos"],
    "responses": {
        200: OpenApiResponse(
            response=AcCursoOfertaIdDescricaoSerializer(many=True),
            description="Lista de ofertas de curso vigentes atualmente.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {"id": 77, "descricao": "Oferta tal do curso tal"},
                        {"id": 76, "descricao": "Oferta tal do curso tal"},
                    ],
                )
            ],
        )
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_FUNCOES_COM_FICHA_UAB_APIVIEW = {
    "summary": "Lista funções de bolsista com ficha UAB",
    "description": "Retorna todas as funções de bolsista marcadas com ficha UAB.",
    "tags": ["Financeiro - Vínculos"],
    "responses": {
        200: OpenApiResponse(
            response=ListarFuncoesComFichaUABSerializer(many=True),
            description="Lista de funções de bolsista com ficha UAB.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {"id": 1, "funcao": "Coordenador UAB"},
                        {"id": 2, "funcao": "Professor Formador UAB"},
                        {"id": 3, "funcao": "Tutor a Distância"},
                    ],
                )
            ],
        )
    },
    "auth": [{"type": "bearer"}],
}

DOCS_ASSOCIAR_EDITAL_FUNCAO_FICHA_OFERTA_APIVIEW = {
    "summary": "Lista, cria ou atualiza associações entre edital, função e oferta",
    "description": (
        "Permite visualizar, criar ou atualizar a associação entre um edital, uma função de bolsista e uma oferta de curso."
    ),
    "tags": ["Financeiro - Vínculos"],
    "responses": {
        200: OpenApiResponse(
            response=FiGetEditalFuncaoOfertaSerializer(many=True),
            description="Lista de associações edital-função-oferta.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta (GET)",
                    value=[
                        {
                            "id": 10,
                            "ed_edital": 23,
                            "fi_funcao_bolsista": 1,
                            "ac_curso_oferta": 77,
                            "edital": "05/2024",
                            "funcao": "Coordenador",
                            "oferta": "Oferta tal do curso tal",
                        }
                    ],
                )
            ],
        ),
        201: OpenApiResponse(
            response=FiPostEditalFuncaoOfertaSerializer,
            description="Associação criada com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta (POST criado)",
                    value={
                        "ed_edital": 23,
                        "fi_funcao_bolsista": 1,
                        "ac_curso_oferta": 77,
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Falta o id (PUT) ou Associação já existe (POST/PUT)",
            examples=[
                OpenApiExample(
                    "Erro: Falta o id (PUT)",
                    value={"detail": "Falta o id para atualizar a associação."},
                ),
                OpenApiExample(
                    "Erro: Associação já existe (POST/PUT)",
                    value={
                        "non_field_errors": [
                            "Associação edital-função-oferta já existe."
                        ]
                    },
                ),
            ],
        ),
        404: OpenApiResponse(
            description="Associação não encontrada.",
            examples=[
                OpenApiExample(
                    "Erro: Associação não encontrada (PUT)",
                    value={"detail": "Associação não encontrada."},
                )
            ],
        ),
    },
    "request": FiPostEditalFuncaoOfertaSerializer,
    "auth": [{"type": "bearer"}],
}

DOCS_ASSOCIAR_EDITAL_FUNCAO_FICHA_OFERTA_RETRIEVE_DESTROY_APIVIEW = {
    "summary": "Recupera ou remove uma associação edital-função-oferta (mixin)",
    "description": (
        "Recupera os detalhes ou remove uma associação específica entre edital, função de bolsista e oferta de curso, a partir do ID da associação."
    ),
    "tags": ["Financeiro - Vínculos"],
    "responses": {
        200: OpenApiResponse(
            response=FiGetEditalFuncaoOfertaSerializer,
            description="Detalhes da associação solicitada.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta (GET)",
                    value={
                        "id": 10,
                        "ed_edital": 23,
                        "fi_funcao_bolsista": 1,
                        "ac_curso_oferta": 77,
                        "edital": "05/2024",
                        "funcao": "Coordenador UAB",
                        "oferta": "Oferta tal do curso tal",
                    },
                )
            ],
        ),
        204: OpenApiResponse(
            description="Associação removida com sucesso.",
        ),
        404: OpenApiResponse(
            description="Associação não encontrada.",
            examples=[
                OpenApiExample(
                    "Erro: Associação não encontrada (GET ou DELETE)",
                    value={"detail": "Associação não encontrada."},
                )
            ],
        ),
    },
    "auth": [{"type": "bearer"}],
}
