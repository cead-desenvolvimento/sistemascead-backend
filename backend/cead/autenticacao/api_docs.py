from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from .serializers import DjUriSerializer

DOCS_OBTER_URIS_PERMITIDAS = {
    "summary": "Obtém URIs permitidas e status de administrador",
    "description": (
        "Retorna um objeto contendo:\n"
        "- A lista de URIs permitidas de acordo com os grupos de permissões "
        "associados ao usuário autenticado.\n"
        "- O atributo `is_staff`, indicando se o usuário é administrador."
    ),
    "tags": ["Autenticação"],
    "responses": {
        200: OpenApiResponse(
            response=None,
            examples=[
                OpenApiExample(
                    "Exemplo admin",
                    value={
                        "is_staff": True,
                        "uris": [
                            {"id": 1, "descricao": "Página inicial", "uri": "/home/"},
                            {
                                "id": 2,
                                "descricao": "Administração",
                                "uri": "/backend/admin/",
                            },
                        ],
                    },
                ),
                OpenApiExample(
                    "Exemplo não admin",
                    value={
                        "is_staff": False,
                        "uris": [
                            {"id": 1, "descricao": "Página inicial", "uri": "/home/"},
                        ],
                    },
                ),
            ],
            description="Objeto com a flag de administrador e a lista de URIs permitidas.",
        ),
        401: OpenApiResponse(description="Não autenticado."),
    },
    "auth": [{"type": "bearer"}],
}
