from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse

from cead.messages import (
    ERRO_GET_ARQUIVO,
    ERRO_GET_EDITAL,
    ERRO_GET_VAGA,
    ERRO_GET_VAGAS,
    ERRO_GET_PESSOA_VAGA_VALIDACAO,
)
from cead.serializers import CmPessoaIdNomeCpfSerializer
from .messages import *
from .serializers import *


DOCS_ENVIAR_EMAIL_APIVIEW = {
    "summary": "Envia e-mail para preenchimento da ficha para o candidato selecionado",
    "description": (
        "Envia um e-mail para a preenchimento de ficha para o candidato selecionado, referente à vaga atualmente registrada na sessão do usuário."
        "\n\n**Pré-requisito:** a sessão deve conter 'vaga_id' e 'vaga_id_hash' válidos, criados em _editais/enviar_emails/_"
        "\n\n**Nota:** o e-mail é a única forma de preencher a ficha, haja vista que há um digest SHA-256 que será validado no início do preenchimento."
    ),
    "tags": ["Editais - Mensagens"],
    "parameters": [
        OpenApiParameter(
            name="email",
            type=str,
            location=OpenApiParameter.PATH,
            description="E-mail do candidato a ser notificado.",
        )
    ],
    "responses": {
        200: OpenApiResponse(
            description="E-mail enviado para preenchimento da ficha Fulano da Silva",
            examples=[
                OpenApiExample(
                    "Exemplo de sucesso",
                    value={
                        "detail": "E-mail enviado para preenchimento da ficha Fulano da Silva"
                    },
                )
            ],
        ),
        404: OpenApiResponse(description="Pessoa/Vaga não encontrada."),
        500: OpenApiResponse(description="Erro ao enviar e-mail."),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_ENVIAR_EMAILS_APIVIEW = {
    "summary": "Envia e-mails de ficha para vários candidatos de uma vaga",
    "description": (
        "Envia e-mails de ficha de inscrição para todos os candidatos validados na vaga atualmente registrada na sessão do usuário."
        "\n\n**Pré-requisito:** a sessão deve conter 'vaga_id' e 'vaga_id_hash' válidos, criados em _editais/enviar_emails/_."
        "\n\nVocê pode opcionalmente limitar até qual candidato o envio deve ocorrer, usando o campo `enviar_ate` no corpo da requisição."
        "\n\n**Nota:** _editais/enviar_emails/_ traz os candidatos organizados por nota, logo `enviar_ate` considerará candidatos em ordem de pontuação."
        "\n\n**Nota:** o e-mail é a única forma de preencher a ficha, haja vista que há um digest SHA-256 que será validado no início do preenchimento."
    ),
    "tags": ["Editais - Mensagens"],
    "request": {
        "application/json": {
            "schema": {
                "type": "object",
                "properties": {
                    "enviar_ate": {
                        "type": "string",
                        "format": "email",
                        "description": "E-mail do último candidato a receber o e-mail (opcional).",
                    }
                },
                "example": {"enviar_ate": "ultimo@exemplo.com"},
            }
        }
    },
    "responses": {
        200: OpenApiResponse(
            description=EMAILS_BOLSA_ENVIADOS,
            examples=[
                OpenApiExample(
                    "Exemplo de sucesso",
                    value={
                        "numero_emails_enviados": 10,
                        "nome_ultima_pessoa_que_o_email_foi_enviado": "Fulano da Silva",
                        "detail": EMAILS_BOLSA_ENVIADOS,
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description=EMAILS_BOLSA_ENVIADOS + " (registros individuais dos erros)"
        ),
        404: OpenApiResponse(description=ERRO_GET_PESSOAVAGAVALIDACOES),
        500: OpenApiResponse(description=ERRO_ENVIO_EMAIL),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_EDITAIS_EMISSORES_MENSAGEM_FICHA_APIVIEW = {
    "summary": "Lista editais passíveis de envio de mensagem para preenchimento de ficha",
    "description": (
        "Retorna uma lista dos editais para os quais o usuário autenticado pode emitir e-mails para preenchimento da ficha de inscrição."
        "\n\n- Se o usuário pertence ao grupo 'Acadêmico - administradores', retorna todos os editais disponíveis para emissão."
        "\n- Para outros usuários (em permission_classes), retorna apenas editais associados ao usuário (ed_edital_pessoa), já encerrados para validação e ainda dentro da validade."
    ),
    "tags": ["Editais - Mensagens"],
    "responses": {
        200: OpenApiResponse(
            response=ListarEditaisEmissoresMensagemFichaSerializer(many=True),
            description="Lista editais passíveis de envio de mensagem para preenchimento de ficha.",
        ),
        404: OpenApiResponse(description=ERRO_GET_PESSOA),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_EDITAIS_RELATORIOS_APIVIEW = {
    "summary": "Lista editais disponíveis para relatórios",
    "description": (
        "Retorna uma lista dos editais que o usuário pode visualizar nos relatórios."
        "\n\n- Usuários do grupo 'Acadêmico - administradores' recebem todos os editais cadastrados."
        "\n- Outros usuários recebem apenas os editais para os quais estão associados (ed_edital_pessoa)."
    ),
    "tags": ["Editais - Relatórios"],
    "responses": {
        200: OpenApiResponse(
            response=ListarEditaisRelatorioSerializer(many=True),
            description="Lista de editais disponíveis para visualização de relatórios.",
        ),
        404: OpenApiResponse(description=ERRO_GET_PESSOA),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_EDITAIS_VALIDACAO_APIVIEW = {
    "summary": "Lista editais disponíveis para validação",
    "description": (
        "Retorna uma lista de editais (no período de validação e ainda válidos) que o usuário autenticado pode validar."
        "\n\n- Usuários do grupo 'Acadêmico - administradores' recebem todos os editais."
        "\n- Outros usuários recebem apenas os editais nos quais estão associados (ed_edital_pessoa)."
    ),
    "tags": ["Editais - Validação"],
    "responses": {
        200: OpenApiResponse(
            response=ListarEditaisValidacaoSerializer(many=True),
            description="Lista de editais disponíveis para validação.",
        ),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_EDITAL_JUSTIFICATIVA_APIVIEW = {
    "summary": "Lista editais disponíveis para visualização de justificativa",
    "description": (
        "Retorna os editais que já encerraram o período de validação, mas ainda estão dentro do período de validade. "
        "Para consulta de justificativas relacionadas ao processo seletivo, preenchidas pelo validador."
    ),
    "tags": ["Editais - Justificativas"],
    "responses": {
        200: OpenApiResponse(
            response=ListarEditalJustificativaSerializer(many=True),
            description="Lista de editais disponíveis para justificativas.",
        ),
        500: OpenApiResponse(description=ERRO_GET_EDITAL),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_VAGAS_EMISSORES_MENSAGEM_FICHA_APIVIEW = {
    "summary": "Lista vagas de um edital para emissão de mensagem para preenchimento da ficha",
    "description": (
        "Retorna todas as vagas do edital identificado pelo ano e número, para as quais o usuário autenticado pode emitir ficha."
        "\n\n- Exige permissão especial para emissão de mensagens de ficha."
        "\n- Utilizado para seleção de vagas no momento de envio de ficha para candidatos. A seleção de candidatos é feita apenas quando se seleciona a vaga."
    ),
    "tags": ["Editais - Mensagens"],
    "parameters": [
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            description="id do edital.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=ListarVagasEmissoresMensagemFichaSerializer(many=True),
            description="Lista de vagas do edital.",
        ),
        404: OpenApiResponse(description=ERRO_GET_EDITAL),
        500: OpenApiResponse(description=ERRO_GET_VAGAS),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_VAGAS_RELATORIO_APIVIEW = {
    "summary": "Lista vagas de um edital para relatórios",
    "description": (
        "Retorna todas as vagas associadas ao edital identificado pelos parâmetros de ano e número, "
        "para que o usuário autenticado possa consultar informações detalhadas em relatórios."
        "\n\n- Exige permissões de acesso ao relatório e ao edital específico."
    ),
    "tags": ["Editais - Relatórios"],
    "parameters": [
        OpenApiParameter(
            name="ano",
            type=int,
            location=OpenApiParameter.PATH,
            description="Ano do edital.",
        ),
        OpenApiParameter(
            name="numero",
            type=int,
            location=OpenApiParameter.PATH,
            description="Número do edital.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=ListarVagasRelatorioSerializer(many=True),
            description="Lista de vagas do edital.",
        ),
        404: OpenApiResponse(description=ERRO_GET_EDITAL),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_VAGAS_VALIDACAO_APIVIEW = {
    "summary": "Lista vagas de um edital para validação",
    "description": (
        "Retorna todas as vagas do edital identificado pelo ano e número, "
        "permitindo que o usuário autenticado faça o processo de validação das inscrições nestas vagas."
        "\n\n- Exige permissão de validador de editais."
    ),
    "tags": ["Editais - Validação"],
    "parameters": [
        OpenApiParameter(
            name="ano",
            type=int,
            location=OpenApiParameter.PATH,
            description="Ano do edital.",
        ),
        OpenApiParameter(
            name="numero",
            type=int,
            location=OpenApiParameter.PATH,
            description="Número do edital.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=ListarVagasValidacaoSerializer(many=True),
            description="Lista de vagas do edital para validação.",
        ),
        404: OpenApiResponse(description=ERRO_GET_EDITAL),
        500: OpenApiResponse(description=ERRO_GET_VAGAS),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_VALIDAR_VAGA_APIVIEW = {
    "summary": "Consulta informações e valida candidatos de uma vaga",
    "description": (
        "GET: Retorna informações detalhadas de uma vaga (ex: descrição, máximo de pontos) e os dados paginados dos inscritos para validação."
        "\nPOST: Permite ao validador enviar a validação de um candidato (pontuação, justificativa, arquivos validados e pontuações individuais)."
        "\n\n- Permite somente em período de validação do edital."
        "\n- Paginador disponível via parâmetros `page` e `page_size` no GET."
        "\n- POST aceita pontuação, justificativa e listas de arquivos/documentos com pontuação individual."
        "\n- Erros específicos para fora de prazo, formato de IDs, tipo de documento e pontuação inválida."
    ),
    "tags": ["Editais - Validação"],
    "parameters": [
        OpenApiParameter(
            name="vaga_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID da vaga.",
        ),
        OpenApiParameter(
            name="page",
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Número da página (pagina os inscritos).",
        ),
        OpenApiParameter(
            name="page_size",
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Tamanho da página (máx. 20, padrão: 10).",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=ValidarVagaGetSerializer,
            description=(
                "GET: Informações detalhadas da vaga e candidatos para validação.\n"
                "POST: Resposta de sucesso da validação."
            ),
            examples=[
                OpenApiExample(
                    "GET - Exemplo de resposta",
                    value={
                        "id": 123,
                        "descricao": "Vaga de Professor Matemática",
                        "maximo_de_pontos": 30,
                    },
                ),
                OpenApiExample(
                    "POST - Exemplo de resposta de sucesso",
                    value={
                        "inscrito_id": 9876,
                        "pontuacao": 22,
                        "justificativa": "",
                        "arquivo_valido": ["checkbox-11", "combobox-15"],
                        "pontuacoes_documentos": {
                            "checkbox-11": 5.0,
                            "combobox-15": 17.0,
                        },
                    },
                ),
            ],
        ),
        201: OpenApiResponse(
            description=OK_DADOS_CANDIDATO,
        ),
        400: OpenApiResponse(
            description=(
                ERRO_EDITAL_FORA_PRAZO_VALIDACAO
                + " ou "
                + ERRO_POST_PESSOAVAGAVALIDACAO
            ),
            examples=[
                OpenApiExample(
                    "Erro fora do prazo",
                    value={"non_field_errors": [ERRO_EDITAL_FORA_PRAZO_VALIDACAO]},
                ),
                OpenApiExample(
                    "Erro de inscrição inexistente",
                    value={"inscrito_id": ["Inscrição não encontrada para essa vaga."]},
                ),
            ],
        ),
        404: OpenApiResponse(description=ERRO_GET_VAGA),
    },
    "request": {"application/json": ValidarVagaPostSerializer},
    "auth": [{"type": "bearer"}],
}

DOCS_EMITIR_MENSAGEM_FICHA_VAGA_APIVIEW = {
    "summary": "Lista candidatos de uma vaga para envio de mensagem de ficha",
    "description": (
        "Retorna uma lista de candidatos inscritos em uma vaga específica, "
        "para os quais pode ser emitida mensagem de solicitação de ficha."
        "\n\nUtilizada para selecionar quem receberá o e-mail (_editais/enviar_email/{email}_, _editais/enviar_emails/_)."
    ),
    "tags": ["Editais - Mensagens"],
    "parameters": [
        OpenApiParameter(
            name="vaga_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID da vaga.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=EmitirMensagemFichaVagaSerializer(many=True),
            description="Lista de candidatos da vaga.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {
                            "pessoa_id": 1234,
                            "pessoa_nome": "Maria Eduarda",
                            "pessoa_email": "ma*****@ex*********",
                            "pontuacao": 19.5,
                            "codigo": "XyZ123A",
                        },
                        {
                            "pessoa_id": 4321,
                            "pessoa_nome": "João Silva",
                            "pessoa_email": "jo*****@em*********",
                            "pontuacao": 17.0,
                            "codigo": "AB12CD",
                        },
                    ],
                )
            ],
        ),
        404: OpenApiResponse(description=ERRO_GET_VAGA),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_VERIFICA_VALIDACAO_APIVIEW = {
    "summary": "Consulta situação da validação de um candidato em uma vaga",
    "description": (
        "Retorna informações sobre a validação de um candidato específico em uma vaga, incluindo o nome do responsável pela validação, a pontuação e a data da validação."
        "\n\nUtilizado para exibir o status da validação do candidato na tela de validação."
    ),
    "tags": ["Editais - Validação"],
    "parameters": [
        OpenApiParameter(
            name="vaga_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID da vaga.",
        ),
        OpenApiParameter(
            name="pessoa_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID do candidato.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=VerificaValidacaoSerializer,
            description="Informações sobre a validação do candidato na vaga.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value={
                        "nome_responsavel_validacao": "José I D",
                        "pontuacao": 17.5,
                        "data": "09/09/2019 às 19:15:00",
                    },
                )
            ],
        ),
        404: OpenApiResponse(description=ERRO_GET_PESSOA_VAGA_VALIDACAO),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_BAIXAR_ARQUIVOS_APIVIEW = {
    "summary": "Baixa ou exibe arquivos enviados por candidatos",
    "description": (
        "Permite ao usuário autenticado baixar ou visualizar arquivos anexados a inscrições de candidatos, "
        "relacionados a determinada vaga e campo específico do edital. "
        "\n\nNecessita permissões específicas e validação de vínculo do usuário com o edital/vaga."
        "\n\nÉ a única forma de acessar os arquivos, que estão protegidos por X-Accel-Redirect"
    ),
    "tags": ["Editais - Validação"],
    "parameters": [
        OpenApiParameter(
            name="vaga_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID da vaga relacionada ao arquivo.",
        ),
        OpenApiParameter(
            name="pessoa_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID do candidato (pessoa).",
        ),
        OpenApiParameter(
            name="campo_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID do campo/documento do edital relacionado ao arquivo.",
        ),
        OpenApiParameter(
            name="tipo",
            type=str,
            location=OpenApiParameter.PATH,
            required=True,
            description="Tipo do campo (ex: 'checkbox', 'combobox', 'datebox').",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Arquivo retornado para download ou visualização (resposta binária, tipo file/pdf/imagem)."
        ),
        404: OpenApiResponse(description=ERRO_GET_ARQUIVO),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_PESSOAS_PARA_ASSOCIACAO_APIVIEW = {
    "summary": "Lista as pessoas que estao cadastradas com o CPF no Django e que existem em cm_pessoa",
    "description": (
        "Retorna uma lista de pessoas (id, nome, cpf) que podem ser associadas a um edital. "
        "Permite filtrar por nome ou CPF parcial usando query string."
        "\n\nExemplo de uso: `/api/pessoas/associar/?nome=Rodrigo` ou `/api/pessoas/associar/?cpf=12345678901`"
    ),
    "tags": ["Editais - Administração"],
    "parameters": [
        OpenApiParameter(
            name="nome",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filtro por nome da pessoa (parcial ou completo).",
        ),
        OpenApiParameter(
            name="cpf",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filtro por CPF da pessoa (parcial ou completo).",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=CmPessoaIdNomeCpfSerializer(many=True),
            description="Lista de pessoas para associação.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {"id": 1, "nome": "Rodrigo Marangon", "cpf": "12345678901"},
                        {"id": 2, "nome": "Maria Eduarda", "cpf": "10987654321"},
                    ],
                )
            ],
        ),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_LISTAR_EDITAIS_ASSOCIAR_EDITAL_PESSOA_APIVIEW = {
    "summary": "Lista editais disponíveis para associação de pessoas",
    "description": (
        "Retorna uma lista de editais em que o usuário autenticado pode associar pessoas. "
        "Utilizado principalmente em funcionalidades administrativas para designar pessoas a editais específicos. Exemplos: validação, relatórios."
    ),
    "tags": ["Editais - Administração"],
    "responses": {
        200: OpenApiResponse(
            response=ListarEditaisAssociacaoEditalPessoaSerializer(many=True),
            description="Lista de editais disponíveis para associação de pessoas.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {
                            "id": 10,
                            "numero": 2025,
                            "ano": 1,
                            "descricao": "Edital Bolsas 2025",
                            "data_fim_validacao": "2025-06-30",
                            "data_validade": "2025-12-31",
                        }
                    ],
                )
            ],
        ),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_BUSCAR_USUARIO_POR_CPF_VIEW = {
    "summary": "Busca usuário pelo CPF",
    "description": (
        "Recebe um CPF como parâmetro de rota e retorna o ID do usuário Django correspondente, caso exista."
        "\n\nÚtil para criar um botão de edição de usuário numa tela."
    ),
    "tags": ["Editais - Administração"],
    "parameters": [
        OpenApiParameter(
            name="cpf",
            type=str,
            location=OpenApiParameter.PATH,
            required=True,
            description="CPF do usuário a ser buscado.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=UsuarioPorCpfSerializer,
            description="ID do usuário Django correspondente ao CPF.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value={"id": 42},
                )
            ],
        ),
        404: OpenApiResponse(
            description="Usuário não encontrado para o CPF informado."
        ),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_ASSOCIAR_EDITAL_PESSOA_APIVIEW = {
    "summary": "Consulta e associa pessoas a um edital",
    "description": (
        "**GET:** Retorna a lista de pessoas já associadas ao edital informado, com dados detalhados de cada associação. "
        "Útil para visualizar e gerenciar vínculos (para validação/relatórios) de participantes no edital."
        "\n\n"
        "**POST:** Associa uma nova pessoa ao edital informado. "
        "Requer no payload ao menos o ID da pessoa e informações de vínculo. "
        "Se a pessoa já estiver associada, atualiza os dados do vínculo."
        "\n\n"
        "Ambos os métodos são utilizados em telas administrativas para o gerenciamento manual de participações em editais."
    ),
    "tags": ["Editais - Administração"],
    "request": EdPostEditalPessoaSerializer,
    "responses": {
        200: OpenApiResponse(
            response=EdPostEditalPessoaSerializer,
            description="Pessoa já estava associada ao edital e teve seus dados de vínculo atualizados.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta para associação já existente",
                    value={
                        "id": 101,
                        "cm_pessoa": 1,
                        "ed_edital": 10,
                        "tipo_vinculo": "Participante",
                    },
                )
            ],
        ),
        201: OpenApiResponse(
            response=EdPostEditalPessoaSerializer,
            description="Pessoa associada ao edital com sucesso.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta para nova associação",
                    value={
                        "id": 102,
                        "cm_pessoa": 2,
                        "ed_edital": 10,
                        "tipo_vinculo": "Coordenador",
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            description="Dados inválidos ou associação já existente.",
        ),
        404: OpenApiResponse(
            description="Edital não encontrado ou fora do período permitido."
        ),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_ASSOCIAR_EDITAL_PESSOA_RETRIEVE_DESTROY_APIVIEW = {
    "summary": "Consulta ou remove associação de pessoa a edital (mixin)",
    "description": (
        "GET: Retorna os dados da associação entre uma pessoa e um edital, incluindo dados da pessoa."
        "\nDELETE: Remove a associação."
    ),
    "tags": ["Editais - Administração"],
    "parameters": [
        OpenApiParameter(
            name="editalpessoa_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID da associação entre pessoa e edital.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            response=EdGetEditalPessoaSerializer,
            description="Dados da associação de pessoa a edital.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta GET",
                    value={
                        "id": 222,
                        "cm_pessoa": {
                            "id": 1,
                            "nome": "Rodrigo Marangon",
                            "cpf": "12345678901",
                        },
                    },
                )
            ],
        ),
        204: OpenApiResponse(description="Associação removida (DELETE)."),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_ENVIAR_JUSTIFICATIVA_POR_EMAIL_APIVIEW = {
    "summary": "Envia justificativa redigida pelo avaliador por e-mail ao candidato",
    "description": (
        "Envia a justificativa registrada para um candidato em uma vaga específica por e-mail, "
        "permitindo informar ao candidato os motivos de alteração, indeferimento ou ajustes em sua avaliação."
    ),
    "tags": ["Editais - Justificativas"],
    "parameters": [
        OpenApiParameter(
            name="vaga_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID da vaga.",
        ),
        OpenApiParameter(
            name="pessoa_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID do candidato.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Mensagem enviada para {PRIMEIRO_NOME}, e-mail: {EMAIL_MASCARADO}",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value={
                        "detail": "Rodrigo, foi enviada mensagem para para r.********@gm*******"
                    },
                )
            ],
        ),
        404: OpenApiResponse(
            description=ERRO_GET_PESSOAVAGAINSCRICAO + " ou " + ERRO_GET_EDITAL
        ),
        500: OpenApiResponse(description=ERRO_ENVIO_EMAIL),
    },
    "auth": [{"type": "bearer"}],
}

DOCS_RELATORIO_DO_EDITAL_APIVIEW = {
    "summary": "Gera relatório de inscritos de um edital",
    "description": (
        "Retorna uma lista detalhada dos inscritos no edital especificado, incluindo pontuação, justificativa, responsáveis, datas e situação de confirmação.\n\n"
        "Utilizado para exportar, visualizar e analisar os dados completos do processo seletivo de um edital.\n\n"
        "### Ordenação das inscrições\n"
        "1. Candidatos **sem justificativa** (válidos), em ordem decrescente de pontuação real.\n"
        "2. Candidatos **com justificativa** (indeferidos), aparecem ao final, também ordenados pela pontuação real.\n\n"
        "As pontuações são numéricas; se não houver pontuação real, usa-se a pontuação informada como fallback."
    ),
    "tags": ["Editais - Relatórios"],
    "parameters": [
        OpenApiParameter(
            name="id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="Ano do edital.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista detalhada dos inscritos do edital.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        {
                            "protocolo": 1234,
                            "vaga": "Professor Matemática",
                            "nome": "Maria Eduarda",
                            "cpf": "123.456.789-01",
                            "email": "ma*****@ex*****.com",
                            "pontuacao_informada": 20,
                            "pontuacao_real": 18,
                            "responsavel_validacao": "Rodrigo Marangon",
                            "data_inscricao": "19/06/2025 14:30",
                            "data_validacao": "20/06/2025 09:00",
                            "justificativa_pontuacao": "Documentação incompleta.",
                            "confirmado": "Sim",
                        }
                    ],
                )
            ],
        ),
        404: OpenApiResponse(description=ERRO_GET_EDITAL),
    },
    "auth": [{"type": "bearer"}],
}


DOCS_RELATORIO_DA_VAGA_APIVIEW = {
    "summary": "Gera relatório de inscritos de uma vaga",
    "description": (
        "Retorna uma lista detalhada dos inscritos na vaga especificada, com informações sobre pontuação, responsáveis, datas, justificativas e situação de confirmação.\n\n"
        "Utilizado para análise, exportação e acompanhamento do processo seletivo em uma vaga específica de um edital.\n\n"
        "### Ordenação das inscrições\n"
        "1. Candidatos **sem justificativa** (válidos), em ordem decrescente de pontuação real.\n"
        "2. Candidatos **com justificativa** (indeferidos), aparecem ao final, também ordenados pela pontuação real.\n\n"
        "As pontuações são numéricas; se não houver pontuação real, usa-se a pontuação informada como fallback."
    ),
    "tags": ["Editais - Relatórios"],
    "parameters": [
        OpenApiParameter(
            name="vaga_id",
            type=int,
            location=OpenApiParameter.PATH,
            required=True,
            description="ID da vaga.",
        ),
    ],
    "responses": {
        200: OpenApiResponse(
            description="Lista detalhada dos inscritos da vaga.",
            examples=[
                OpenApiExample(
                    "Exemplo de resposta",
                    value=[
                        # candidato válido
                        {
                            "protocolo": 5555,
                            "nome": "João Silva",
                            "cpf": "987.654.321-00",
                            "email": "jo***@em***.com",
                            "pontuacao_informada": 18,
                            "pontuacao_real": 16,
                            "responsavel_validacao": "Maria Eduarda",
                            "data_inscricao": "15/06/2025 10:30",
                            "data_validacao": "17/06/2025 09:15",
                            "justificativa_pontuacao": "",
                            "confirmado": "Sim",
                        },
                        # candidato com justificativa
                        {
                            "protocolo": 5556,
                            "nome": "Ana Costa",
                            "cpf": "123.456.789-01",
                            "email": "an***@em***.com",
                            "pontuacao_informada": 20,
                            "pontuacao_real": 0,
                            "responsavel_validacao": "Rodrigo Marangon",
                            "data_inscricao": "16/06/2025 14:00",
                            "data_validacao": "18/06/2025 11:20",
                            "justificativa_pontuacao": "Documentação incompleta.",
                            "confirmado": "Não",
                        },
                    ],
                )
            ],
        ),
        404: OpenApiResponse(description=ERRO_GET_VAGA),
    },
    "auth": [{"type": "bearer"}],
}
