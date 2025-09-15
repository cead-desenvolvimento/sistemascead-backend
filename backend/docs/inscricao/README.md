# App: Inscrição Pública em Editais

## Visão Geral

Este app controla **todo o fluxo de inscrição pública do candidato** em vagas de editais de processos seletivos. Ele cuida desde a abertura do edital, seleção da vaga, cadastro/validação do candidato, escolha de cotas, registro de formações, preenchimento de campos específicos da vaga (incluindo anexos/arquivos), até a finalização e submissão da inscrição.

O fluxo é **guiado e seguro**: todas as etapas dependem de validações em sessão e envio de código por e-mail, garantindo que apenas o próprio candidato avance e preencha. O controle do fluxo de inscrição é feito por hash na sessão, impedindo cadastros com problemas. O sistema permite edição da inscrição e inscrições em várias vagas do mesmo edital, se assim prever o edital.

> _Por que o candidato pode editar a inscrição até o fim do prazo de inscrição?_

O sistema é para o candidato, e não para o administrador dele e nem para o desenvolvedor.

## Funcionalidades Principais

-   **Listagem de editais abertos para inscrição**
-   **Seleção de vaga pelo candidato**
-   **Validação de CPF e cadastro/atualização dos dados pessoais**
-   **Envio e validação de código por e-mail**
-   **Escolha e marcação de cotas (ações afirmativas)**
-   **Registro de formação acadêmica**
-   **Alerta sobre inscrição duplicada ou concorrente**
-   **Preenchimento e marcação dos campos exigidos na vaga (checkbox, combobox, datebox)**
-   **Upload de arquivos obrigatórios (PDF, imagens, etc)**
-   **Download dos arquivos enviados**
-   **Finalização da inscrição, com validação de etapa e submissão segura**
-   **Documentação detalhada via drf-spectacular/OpenAPI**

## Fluxo Resumido de Uso

1. **Candidato acessa lista de editais abertos** (apenas os com inscrição vigente).
2. **Escolhe o edital e a vaga** (salva na sessão).
3. **Valida o CPF** (se já existir na base, recupera dados; senão, segue para cadastro).
4. **Cadastra/atualiza dados pessoais** (vincula à sessão).
5. **Recebe código de validação por e-mail** e valida no sistema.
6. **Seleciona cota (se houver)**.
7. **Registra e gerencia formações acadêmicas**.
8. **Visualiza alertas de inscrições concorrentes** (na mesma vaga ou edital).
9. **Preenche campos específicos exigidos na vaga** (pontuação, datas, anexos, uploads).
10. **Finaliza a inscrição** (se tudo estiver válido, registra inscrição e salva data).

## Principais Endpoints (Views)

-   **Editais em fase de inscrição:**  
    `GET /backend/inscricao/editais/`

-   **Vagas de um edital:**  
    `GET/POST /backend/inscricao/edital/{ano}/{numero}/vagas/`  
    (GET lista vagas, POST marca vaga na sessão)

-   **Validação de CPF:**  
    `POST /backend/inscricao/validar-cpf/`

-   **Cadastro de pessoa:**  
    `POST /backend/inscricao/criar-pessoa/`

-   **Envio de código por e-mail:**  
    `GET/POST /backend/inscricao/enviar-codigo/`

-   **Validação do código recebido:**  
    `POST /backend/inscricao/verificar-codigo/`

-   **Cotas:**  
    `GET/POST/DELETE /backend/inscricao/cotas/`  
    (listar, marcar, remover cotas)

-   **Formação acadêmica:**  
    `GET/POST/DELETE /backend/inscricao/formacao/`  
    (listar, adicionar, remover formação)

-   **Campos da vaga:**  
    `GET /backend/inscricao/vaga/campos/`  
    (lista campos checkbox, combobox, datebox)

-   **Marcação dos campos da vaga:**  
    `GET/POST /backend/inscricao/vaga/campos/preencher/`  
    (consulta ou marca campos e pontuação)

-   **Upload de arquivos:**  
    `GET/POST /backend/inscricao/vaga/anexar-arquivos/`

-   **Download de arquivos enviados:**  
    `GET /backend/inscricao/vaga/baixar-arquivo/`

-   **Finalização da inscrição:**  
    `POST /backend/inscricao/finalizar/`

-   **Alerta sobre inscrições concorrentes:**  
    `GET /backend/inscricao/alerta-inscricao/`

## Permissões e Segurança

-   **Controle total de sessão:** cada etapa depende de dados e hashes válidos.
-   **Candidato só acessa/edita a própria inscrição.**
-   **Proteção contra concorrência/duplicidade de inscrição** (no mesmo edital/vaga).
-   **Validação de uploads e campos obrigatórios.**
-   **Código de e-mail é temporário e expira após 10 minutos.**
-   **Fluxo "obrigatório":** etapas só avançam se as anteriores estiverem corretas.

## Público-alvo

-   **Candidatos:** realizam o preenchimento guiado.
-   **Equipe de suporte e acadêmica:** podem orientar candidatos e auditar registros.
-   **Administradores:** consumo dos dados para validação, relatórios e classificação.

## Observações Técnicas

-   API baseada no DRF, com views APIView e GenericAPIView.
-   Utiliza sessões do Django para todo controle de estado.
-   Uploads organizados por candidato/vaga, com validação de pertencimento.
-   Campos dinâmicos de vaga são configurados no banco e respeitados pelo fluxo.
-   Pontuação automática calculada conforme regras da vaga.
-   Todas as rotas e respostas documentadas via drf-spectacular/OpenAPI.
-   Respostas de erro detalhadas para frontend e suporte.

---

> Este documento pode ser expandido com detalhes de regras internas do edital, exemplos de payloads ou dúvidas frequentes do suporte.
