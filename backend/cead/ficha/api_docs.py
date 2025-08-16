from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse

from cead.serializers import CPFSerializer
from .messages import (
    ERRO_ED_PESSOA_VAGA_VALIDACAO_GEROU_FICHA_JA_EXISTE,
    ERRO_GET_FI_EDITAL_FUNCAO_OFERTA,
    OK_CPF_HASH_VALIDADO,
)
from .serializers import *

DOCS_LISTAR_MUNICIPIOS_VIEW = {
    "summary": "Buscar municípios por nome",
    "tags": ["Ficha - Acesso Público"],
    "description": (
        "Busca municípios cadastrados, filtrando por nome parcial (case-insensitive). "
        "Requer o parâmetro `search`. Retorna resultados paginados."
    ),
    "responses": {
        200: CmMunicipioSerializer(many=True),
    },
}

DOCS_CPF_CODIGO_PESSOA_VALIDACAO_VIEW = {
    "summary": "Valida código do candidato e CPF para acesso à ficha",
    "description": (
        "Recebe um código de validação (da URL) e um CPF (no payload) e valida se o candidato pode acessar o preenchimento da ficha."
        "\n\n"
        "Verifica vínculo do CPF com o código, existência do curso associado e se a ficha já foi gerada."
        "\n\n"
        "Em caso de sucesso, salva identificadores na sessão para os próximos passos."
    ),
    "tags": ["Ficha - Acesso Público"],
    "parameters": [
        OpenApiParameter(
            name="codigo",
            type=str,
            location=OpenApiParameter.PATH,
            required=True,
            description="Código de validação recebido por e-mail.",
        ),
    ],
    "request": CPFSerializer,
    "responses": {
        201: OpenApiResponse(
            description=OK_CPF_HASH_VALIDADO,
            examples=[
                OpenApiExample(
                    "Exemplo de resposta de sucesso",
                    value={"detail": OK_CPF_HASH_VALIDADO},
                )
            ],
        ),
        400: OpenApiResponse(
            description=f"{ERRO_GET_FI_EDITAL_FUNCAO_OFERTA} OU {ERRO_ED_PESSOA_VAGA_VALIDACAO_GEROU_FICHA_JA_EXISTE}",
            examples=[
                OpenApiExample(
                    "Erro associação de edital/função/oferta",
                    value={"detail": ERRO_GET_FI_EDITAL_FUNCAO_OFERTA},
                ),
                OpenApiExample(
                    "Erro de ficha já gerada",
                    value={
                        "detail": ERRO_ED_PESSOA_VAGA_VALIDACAO_GEROU_FICHA_JA_EXISTE
                    },
                ),
            ],
        ),
    },
}

DOCS_CADASTRO_ENDERECO_TELEFONE_BANCO_VIEW = {
    "summary": "Consulta e salva endereço, telefones e banco do candidato",
    "description": (
        "**GET:** Retorna os dados atuais de endereço, telefones e banco da pessoa vinculada à sessão de validação.\n\n"
        "**POST:** Salva ou atualiza endereço, telefones e dados bancários após validação. Requer que o candidato esteja com sessão válida e ainda não tenha gerado ficha."
    ),
    "tags": ["Ficha - Acesso Público"],
    "request": {"POST": CadastroEnderecoTelefoneBancoRequestSerializer},
    "responses": {
        "GET": OpenApiResponse(
            description="Dados atuais de endereço, telefones e banco (GET).",
            examples=[
                OpenApiExample(
                    "Exemplo GET",
                    value={
                        "endereco": {
                            "cep": "30310150",
                            "logradouro": "Rua Cobre",
                            "numero": "200",
                            "complemento": "",
                            "bairro": "Cruzeiro",
                            "cm_municipio": {
                                "municipio": "Belo Horizonte",
                                "cm_uf": {"sigla": "MG", "uf": "Minas Gerais"},
                            },
                        },
                        "telefones": [{"ddd": "34", "numero": "988431334"}],
                        "banco": {
                            "codigo_banco": 341,
                            "agencia": 6699,
                            "conta": 21042,
                            "digito_verificador_conta": 0,
                        },
                    },
                )
            ],
        ),
        "POST": OpenApiResponse(
            description="Dados de endereço, telefone e banco salvos com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo POST",
                    value={
                        "success": "Dados de endereço, telefone e banco salvos com sucesso."
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Dados inválidos (UF, município, campos obrigatórios ou erros de validação)."
        ),
        500: OpenApiResponse(description="Erro ao salvar os dados do candidato."),
    },
}

DOCS_CADASTRO_FI_PESSOA_FICHA_APIVIEW = {
    "summary": "Consulta e salva o preenchimento da ficha do candidato",
    "description": (
        "**GET:** Retorna todos os dados preenchidos pelo candidato na ficha, prontos para exibição/edição.\n\n"
        "**POST:** Salva ou atualiza as respostas do candidato à ficha de inscrição, com todas as validações necessárias. "
        "Impede novo preenchimento caso a ficha já esteja cadastrada."
    ),
    "tags": ["Ficha - Acesso Público"],
    "request": FiPessoaFichaPostSerializer,
    "responses": {
        200: OpenApiResponse(
            response=FiPessoaFichaPostSerializer,
            description="Dados atuais do preenchimento da ficha.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta GET",
                    value={
                        "area_ultimo_curso_superior": "Exatas",
                        "estado_civil": "Casado(a)",
                        "sexo": "Masculino",
                        "tipo_documento": "RG",
                        "data_nascimento": "1986-01-09",
                        "profissao": "Analista de TI",
                        "numero_documento": "12478056",
                        "orgao_expedidor": "SSP",
                        "data_emissao": "2000-06-12",
                        "nome_conjuge": "Maria Cecilia Izidorio Barbosa",
                        "nome_pai": "Tarcisio Figueiredo Marangon",
                        "nome_mae": "Vera Lucia de Assis Damasceno",
                        "ultimo_curso_titulacao": "Mestrado em Ciência da Computação",
                        "instituicao_titulacao": "Universidade Federal de Juiz de Fora",
                        "fi_funcao_bolsista": 5,
                        "ac_curso_oferta": 4,
                    },
                )
            ],
        ),
        201: OpenApiResponse(
            description="Ficha salva com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta POST sucesso",
                    value={"success": "Ficha salva com sucesso."},
                )
            ],
        ),
        400: OpenApiResponse(
            description="Dados inválidos.",
            examples=[
                OpenApiExample(
                    "Dados inválidos",
                    value={
                        "nome_mae": ["Campo obrigatório."],
                        "ac_curso_oferta": ["Curso não encontrado."],
                    },
                ),
            ],
        ),
        500: OpenApiResponse(description="Erro ao salvar a ficha do candidato."),
    },
}

DOCS_GERAR_FICHA_PDF_APIVIEW = {
    "summary": "Gera e retorna o PDF da ficha do candidato",
    "description": (
        "Gera um arquivo PDF com todas as informações da ficha preenchida pelo candidato, "
        "e retorna o arquivo binário para download (Content-Type: application/pdf)."
        "\n\nA chamada a este endpoint só ocorre após a ficha ser salva com sucesso."
    ),
    "tags": ["Ficha - Acesso Público"],
    "responses": {
        200: OpenApiResponse(
            description="PDF gerado com sucesso. A resposta é um arquivo binário (Content-Type: application/pdf)."
        ),
    },
}
