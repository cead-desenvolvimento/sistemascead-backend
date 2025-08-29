from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from .serializers import DjUriSerializer

DOCS_IS_ADMIN = {
    "summary": "Verifica se o usuário é admin (staff)",
    "description": (
        "Retorna um objeto indicando se o usuário autenticado possui o atributo `is_staff`."
    ),
    "tags": ["Autenticação"],
    "responses": {
        200: OpenApiResponse(
            response=None,
            examples=[
                OpenApiExample("Exemplo admin", value={"is_staff": True}),
                OpenApiExample("Exemplo não admin", value={"is_staff": False}),
            ],
            description="Retorna se o usuário é staff/admin.",
        ),
        401: OpenApiResponse(description="Não autenticado."),
    },
}

DOCS_OBTER_URIS_PERMITIDAS = {
    "summary": "Obtém URIs permitidas para o usuário autenticado",
    "description": (
        "Retorna a lista de URIs permitidas de acordo com os grupos de permissões "
        "associados ao usuário autenticado. Para construção de menus dinâmicos no frontend."
    ),
    "tags": ["Autenticação"],
    "responses": {
        200: OpenApiResponse(
            response=DjUriSerializer(many=True), description="Lista de URIs permitidas."
        ),
        401: OpenApiResponse(description="Não autenticado."),
    },
    "auth": [{"type": "bearer"}],
}
