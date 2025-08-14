SPECTACULAR_SETTINGS = {
    "TITLE": "Sistemas CEAD",
    "DESCRIPTION": "Descrição da API.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,  # true para ver o /schema no redoc/swagger
    "SERVE_URLCONF": "cead.urls",
    "SCHEMA_PATH_PREFIX": "/backend",
    "SERVERS": [{"url": "/backend", "description": "Nginx Backend Proxy"}],
    # Outras configs úteis: https://drf-spectacular.readthedocs.io/en/latest/settings.html
}
