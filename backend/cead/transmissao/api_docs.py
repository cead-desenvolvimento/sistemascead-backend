from rest_framework import serializers
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, inline_serializer

from .serializers import TransmissaoConfirmacaoSerializer

# --------------------
# TERMO DE ACEITE
# --------------------

TERMO_GET_RESPONSE = OpenApiResponse(
    response=inline_serializer(
        name="TermoResponse",
        fields={
            "termo": serializers.CharField(
                help_text="Texto completo do termo de aceite vigente."
            ),
        },
    ),
    description="Termo de aceite recuperado com sucesso.",
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "termo": "Eu, abaixo assinado, declaro ciência das normas de uso do espaço..."
            },
        )
    ],
)

TERMO_GET_400 = OpenApiResponse(
    response=inline_serializer(
        name="LimitePorPessoaResponse",
        fields={
            "detail": serializers.CharField(
                help_text="Mensagem de erro detalhando o motivo da rejeição."
            ),
        },
    ),
    description="Limite de transmissões ativas atingido para a pessoa.",
    examples=[
        OpenApiExample(
            "Exemplo de erro",
            value={"detail": "Limite de transmissões ativas atingido."},
        )
    ],
)
TERMO_GET_404 = OpenApiResponse(
    response=inline_serializer(
        name="TermoNotFoundResponse",
        fields={
            "detail": serializers.CharField(
                help_text="Mensagem de erro indicando ausência do termo, limites ou pessoa."
            ),
        },
    ),
    description="Erro ao obter termo, limites ou pessoa.",
    examples=[
        OpenApiExample(
            "Termo não encontrado",
            value={"detail": "Não foi possível encontrar o termo atual."},
        )
    ],
)

TERMO_POST_200 = OpenApiResponse(
    response=inline_serializer(
        name="AceiteTermoSucesso",
        fields={
            "detail": serializers.CharField(
                help_text="Mensagem de sucesso informando aceite do termo."
            ),
        },
    ),
    description="Aceite registrado com sucesso.",
    examples=[
        OpenApiExample(
            "Exemplo de sucesso", value={"detail": "Termo aceito com sucesso."}
        )
    ],
)

TERMO_POST_REQUEST = inline_serializer(
    name="AceiteTermoRequest",
    fields={},  # Não espera campos no POST
)

TERMO_VIEW_DOCS = {
    "get": {
        "operation_id": "Termo de Aceite para Solicitação de Transmissão",
        "description": (
            "Exibe o termo de responsabilidade/uso que o requisitante deve aceitar "
            "para solicitar uma nova transmissão. Limita a quantidade de transmissões ativas "
            "por pessoa, conforme política institucional."
        ),
        "tags": ["Transmissão"],
        "responses": {
            200: TERMO_GET_RESPONSE,
            400: TERMO_GET_400,
            404: TERMO_GET_404,
        },
    },
    "post": {
        "description": (
            "Registra o aceite do termo pelo requisitante. "
            "Gera uma hash de controle na sessão do usuário, necessária para prosseguir com a solicitação de transmissão."
        ),
        "tags": ["Transmissão"],
        "responses": {200: TERMO_POST_200},
        "request": TERMO_POST_REQUEST,
    },
}

# --------------------
# ESPAÇO FÍSICO
# --------------------


# Serializer igual ao usado na view
class EspacoFisicoSelecionarDocSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID do espaço físico.")
    espaco_fisico = serializers.CharField(help_text="Nome do espaço físico.")


# GET - Resposta de sucesso
ESPACO_FISICO_GET_200 = OpenApiResponse(
    response=EspacoFisicoSelecionarDocSerializer(many=True),
    description="Lista de espaços físicos disponíveis.",
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value=[
                {"id": 1, "espaco_fisico": "Auditório Principal"},
                {"id": 2, "espaco_fisico": "Laboratório de Informática"},
            ],
        ),
    ],
)

# GET - Erro 404
ESPACO_FISICO_GET_404 = OpenApiResponse(
    response=inline_serializer(
        name="EspacoFisicoNaoEncontrado",
        fields={"detail": serializers.CharField()},
    ),
    description="Nenhum espaço físico ativo cadastrado.",
    examples=[
        OpenApiExample(
            "Nenhum espaço físico encontrado",
            value={"detail": "Nenhum espaço físico disponível para seleção."},
        ),
    ],
)

# POST - Request
ESPACO_FISICO_POST_REQUEST = inline_serializer(
    name="EspacoFisicoSelecionarRequest",
    fields={
        "id": serializers.IntegerField(
            help_text="ID do espaço físico a ser selecionado."
        )
    },
)

# POST - Resposta de sucesso
ESPACO_FISICO_POST_200 = OpenApiResponse(
    response=inline_serializer(
        name="EspacoFisicoSelecionadoResponse",
        fields={"detail": serializers.CharField()},
    ),
    description="Espaço físico selecionado com sucesso.",
    examples=[
        OpenApiExample(
            "Exemplo de sucesso",
            value={"detail": "Espaço físico selecionado com sucesso."},
        ),
    ],
)

# POST - Erro 400
ESPACO_FISICO_POST_400 = OpenApiResponse(
    response=inline_serializer(
        name="EspacoFisicoSelecionarBadRequest",
        fields={"detail": serializers.CharField()},
    ),
    description="ID do espaço físico não informado.",
    examples=[
        OpenApiExample(
            "ID ausente",
            value={"detail": "ID do espaço físico é obrigatório."},
        ),
    ],
)

# POST - Erro 404
ESPACO_FISICO_POST_404 = OpenApiResponse(
    response=inline_serializer(
        name="EspacoFisicoSelecionarNotFound",
        fields={"detail": serializers.CharField()},
    ),
    description="Espaço físico não encontrado.",
    examples=[
        OpenApiExample(
            "Não encontrado",
            value={"detail": "Espaço físico não encontrado."},
        ),
    ],
)

ESPACO_FISICO_VIEW_DOCS = {
    "get": {
        "operation_id": "Listar Espaços Físicos",
        "description": "Retorna todos os espaços físicos ativos disponíveis para solicitação de transmissão.",
        "tags": ["Transmissão"],
        "responses": {
            200: ESPACO_FISICO_GET_200,
            404: ESPACO_FISICO_GET_404,
        },
    },
    "post": {
        "operation_id": "Selecionar Espaço Físico",
        "description": "Seleciona um espaço físico ativo e armazena na sessão do usuário para a solicitação de transmissão.",
        "tags": ["Transmissão"],
        "request": ESPACO_FISICO_POST_REQUEST,
        "responses": {
            200: ESPACO_FISICO_POST_200,
            400: ESPACO_FISICO_POST_400,
            404: ESPACO_FISICO_POST_404,
        },
    },
}


# --------------------
# DATAS DISPONÍVEIS
# --------------------


class DatasDisponiveisDocSerializer(serializers.Serializer):
    inicio_periodo = serializers.DateField(
        help_text="Primeira data disponível do período pesquisado (YYYY-MM-DD)."
    )
    fim_periodo = serializers.DateField(
        help_text="Última data disponível do período pesquisado (YYYY-MM-DD)."
    )
    datas_disponiveis = serializers.ListField(
        child=serializers.DateField(),
        help_text="Lista de datas livres para reserva no período informado.",
    )


DATAS_DISPONIVEIS_GET_200 = OpenApiResponse(
    response=DatasDisponiveisDocSerializer,
    description="Lista de datas disponíveis para reserva de transmissão.",
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "inicio_periodo": "2024-07-16",
                "fim_periodo": "2024-07-31",
                "datas_disponiveis": [
                    "2024-07-17",
                    "2024-07-19",
                ],
            },
        ),
    ],
)

DATAS_DISPONIVEIS_ERROR = OpenApiResponse(
    response=inline_serializer(
        name="DatasDisponiveisError", fields={"detail": serializers.CharField()}
    ),
    description="Mensagem de erro (sessão inválida, espaço inexistente, etc).",
    examples=[
        OpenApiExample("Erro sessão", value={"detail": "Sessão inválida."}),
        OpenApiExample(
            "Espaço não encontrado", value={"detail": "Espaço físico não encontrado."}
        ),
        OpenApiExample(
            "Equipe indisponível",
            value={"detail": "Equipe indisponível para o período."},
        ),
        OpenApiExample(
            "Datas obrigatórias", value={"detail": "Informe as datas início e fim."}
        ),
        OpenApiExample(
            "Data inválida", value={"detail": "Data final menor que inicial."}
        ),
    ],
)

# --- Request body POST ---
DATAS_DISPONIVEIS_POST_REQUEST = inline_serializer(
    name="DatasDisponiveisRequest",
    fields={
        "inicio": serializers.DateField(help_text="Data inicial (YYYY-MM-DD)."),
        "fim": serializers.DateField(help_text="Data final (YYYY-MM-DD)."),
    },
)

# --- Response sucesso POST ---
DATAS_DISPONIVEIS_POST_200 = OpenApiResponse(
    response=inline_serializer(
        name="DatasDisponiveisPeriodoSelecionado",
        fields={"detail": serializers.CharField()},
    ),
    description="Período selecionado com sucesso para a próxima etapa.",
    examples=[
        OpenApiExample(
            "Exemplo de sucesso", value={"detail": "Período selecionado com sucesso."}
        ),
    ],
)

# --- Docs da view ---
DATAS_DISPONIVEIS_VIEW_DOCS = {
    "get": {
        "operation_id": "Listar Datas Disponíveis",
        "description": (
            "Retorna as datas disponíveis para reserva de transmissão, "
            "considerando espaço físico, agendas existentes, buffers de preparo e limites institucionais."
        ),
        "tags": ["Transmissão"],
        "responses": {
            200: DATAS_DISPONIVEIS_GET_200,
            400: DATAS_DISPONIVEIS_ERROR,
            404: DATAS_DISPONIVEIS_ERROR,
        },
    },
    "post": {
        "operation_id": "Selecionar Período de Datas Disponíveis",
        "description": (
            "Recebe o período desejado (início e fim) e valida se está disponível para reserva. "
            "Salva o período na sessão do usuário para a próxima etapa da transmissão."
        ),
        "tags": ["Transmissão"],
        "request": DATAS_DISPONIVEIS_POST_REQUEST,
        "responses": {
            200: DATAS_DISPONIVEIS_POST_200,
            400: DATAS_DISPONIVEIS_ERROR,
            404: DATAS_DISPONIVEIS_ERROR,
        },
    },
}

# --------------------
# DATAS FIM VÁLIDAS
# --------------------


class DatasFimValidasDocSerializer(serializers.Serializer):
    datas_fim_validas = serializers.ListField(
        child=serializers.DateField(),
        help_text="Lista de datas finais válidas, a partir da data de início fornecida.",
    )


DATAS_FIM_VALIDAS_GET_200 = OpenApiResponse(
    response=DatasFimValidasDocSerializer,
    description="Lista de datas de fim válidas para o intervalo, segundo as regras do sistema.",
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={"datas_fim_validas": ["2024-07-17", "2024-07-18", "2024-07-19"]},
        )
    ],
)

DATAS_FIM_VALIDAS_GET_400 = OpenApiResponse(
    response=inline_serializer(
        name="DatasFimValidasErro", fields={"detail": serializers.CharField()}
    ),
    description="Erro na requisição (formato inválido, data antes do permitido, etc).",
    examples=[
        OpenApiExample(
            "Sem parâmetro", value={"detail": "Parâmetro 'inicio' é obrigatório."}
        ),
        OpenApiExample(
            "Data inválida", value={"detail": "Data de início antes do permitido."}
        ),
    ],
)

DATAS_FIM_VALIDAS_VIEW_DOCS = {
    "get": {
        "operation_id": "Listar Datas de Fim Válidas",
        "description": (
            "Retorna a lista de datas finais possíveis para completar um período de transmissão, "
            "a partir da data de início informada por parâmetro `?inicio=YYYY-MM-DD`. "
            "A lista respeita os limites institucionais de agendamento (dias permitidos, buffers, limites por mês e semana, etc)."
        ),
        "tags": ["Transmissão"],
        "parameters": [
            {
                "name": "inicio",
                "required": True,
                "in": "query",
                "description": "Data de início desejada (YYYY-MM-DD).",
                "schema": {"type": "string", "format": "date"},
            }
        ],
        "responses": {
            200: DATAS_FIM_VALIDAS_GET_200,
            400: DATAS_FIM_VALIDAS_GET_400,
        },
    }
}


# --------------------
# HORÁRIOS DISPONÍVEIS
# --------------------


class HorarioDocSerializer(serializers.Serializer):
    inicio = serializers.CharField(help_text="Hora inicial no formato HH:MM.")
    fim = serializers.CharField(help_text="Hora final no formato HH:MM.")


class DiaDisponivelDocSerializer(serializers.Serializer):
    data = serializers.DateField(help_text="Data disponível no formato YYYY-MM-DD.")
    dia_semana = serializers.CharField(
        help_text="Dia da semana (1=segunda, ..., 7=domingo)."
    )
    horarios = HorarioDocSerializer(
        many=True, help_text="Lista de blocos de horários disponíveis."
    )


class ListaDiasDisponiveisDocSerializer(serializers.Serializer):
    dias = DiaDisponivelDocSerializer(many=True, help_text="Lista de dias disponíveis.")


# GET - Sucesso
HORARIOS_GET_200 = OpenApiResponse(
    response=ListaDiasDisponiveisDocSerializer,
    description="Lista de dias e horários disponíveis para seleção.",
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "dias": [
                    {
                        "data": "2024-07-15",
                        "dia_semana": "1",
                        "horarios": [
                            {"inicio": "08:00", "fim": "10:00"},
                            {"inicio": "10:30", "fim": "12:00"},
                        ],
                    },
                    {
                        "data": "2024-07-16",
                        "dia_semana": "2",
                        "horarios": [],
                    },
                ]
            },
        ),
    ],
)

# GET - Erro (sessão inválida, expirada, sem espaço, etc)
HORARIOS_GET_400 = OpenApiResponse(
    response=inline_serializer(
        name="HorarioDisponivelBadRequest",
        fields={"detail": serializers.CharField()},
    ),
    description="Erro na requisição (sessão inválida, expirou, dados ausentes, etc).",
    examples=[
        OpenApiExample("Erro", value={"detail": "Sessão inválida."}),
        OpenApiExample("Expirado", value={"detail": "Aceite do termo expirado."}),
        OpenApiExample(
            "Espaço não encontrado", value={"detail": "Espaço físico não encontrado."}
        ),
    ],
)

# POST - Request
HORARIOS_POST_REQUEST = inline_serializer(
    name="HorariosDisponiveisRequest",
    fields={
        "horarios": serializers.ListField(
            child=inline_serializer(
                name="HorarioSelecionado",
                fields={
                    "data": serializers.DateField(),
                    "inicio": serializers.CharField(),
                    "fim": serializers.CharField(),
                },
            ),
            help_text="Lista de horários selecionados, cada um com data, início e fim.",
        ),
        "observacao": serializers.CharField(
            help_text="Observação obrigatória do pedido."
        ),
    },
)

# POST - Sucesso
HORARIOS_POST_201 = OpenApiResponse(
    response=inline_serializer(
        name="HorarioSelecionadoResponse",
        fields={
            "detail": serializers.CharField(),
            "id": serializers.IntegerField(),
        },
    ),
    description="Horários reservados e transmissão criada com sucesso.",
    examples=[
        OpenApiExample(
            "Exemplo de sucesso",
            value={"detail": "Horário selecionado com sucesso.", "id": 101},
        ),
    ],
)

# POST - Erro 400 (vários motivos possíveis)
HORARIOS_POST_400 = OpenApiResponse(
    response=inline_serializer(
        name="HorarioSelecionadoBadRequest",
        fields={"detail": serializers.CharField()},
    ),
    description="Erro na validação dos horários ou do payload.",
    examples=[
        OpenApiExample(
            "Sem horário", value={"detail": "Selecione pelo menos um horário."}
        ),
        OpenApiExample(
            "Observação obrigatória", value={"detail": "Observação obrigatória."}
        ),
        OpenApiExample(
            "Conflito",
            value={
                "detail": "2024-07-15 - 08:00-10:00: Conflito com reserva existente."
            },
        ),
    ],
)

HORARIOS_DISPONIVEIS_VIEW_DOCS = {
    "get": {
        "operation_id": "Listar Horários Disponíveis",
        "description": "Retorna dias e horários disponíveis para a transmissão, considerando reservas e restrições.",
        "tags": ["Transmissão"],
        "responses": {
            200: HORARIOS_GET_200,
            400: HORARIOS_GET_400,
        },
    },
    "post": {
        "operation_id": "Reservar Horários de Transmissão",
        "description": "Confirma e reserva os horários selecionados para a transmissão. Exige observação obrigatória.",
        "tags": ["Transmissão"],
        "request": HORARIOS_POST_REQUEST,
        "responses": {
            201: HORARIOS_POST_201,
            400: HORARIOS_POST_400,
        },
    },
}


### CONFIRMAÇÃO
CONFIRMACAO_GET_200 = OpenApiResponse(
    response=TransmissaoConfirmacaoSerializer,
    description="Dados da transmissão criada, prontos para conferência/assinatura digital.",
    examples=[
        OpenApiExample(
            "Exemplo de resposta",
            value={
                "requisitante_nome": "João Silva",
                "requisitante_email": "joao@exemplo.com",
                "requisitante_cpf": "123.456.789-00",
                "espaco_fisico": "Auditório Principal",
                "horarios": [
                    {"inicio": "2024-07-18T08:00", "fim": "2024-07-18T10:00"},
                    {"inicio": "2024-07-19T13:00", "fim": "2024-07-19T16:00"},
                ],
                "observacao": "Transmissão do seminário anual.",
                "assinatura": "93c60f92d2a48...7eead31e",
            },
        )
    ],
)

CONFIRMACAO_GET_400 = OpenApiResponse(
    description="Sessão inválida ou transmissão não encontrada.",
    examples=[
        OpenApiExample(
            "Sessão expirada",
            value={"detail": "Não há transmissão em andamento na sessão atual."},
        ),
        OpenApiExample(
            "Transmissão não encontrada",
            value={"detail": "Transmissão não encontrada."},
        ),
    ],
)

CONFIRMACAO_TRANSMISSAO_VIEW_DOCS = {
    "get": {
        "operation_id": "Confirmação de Transmissão",
        "description": (
            "Retorna os dados completos da transmissão cadastrada (identificação, horários, espaço, "
            "observação, hash/assinatura), esvaziando a sessão. Os dados são enviados por e-mail para o usuário e equipe."
        ),
        "tags": ["Transmissão"],
        "responses": {
            200: CONFIRMACAO_GET_200,
            400: CONFIRMACAO_GET_400,
        },
    }
}
