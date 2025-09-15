# App: Solicitação de Transmissão

## Visão Geral

Este app é responsável por **gerenciar e organizar as solicitações de transmissão de eventos** em espaços físicos institucionais.

O módulo garante o controle de disponibilidade, requisitos de aceite de termo, escolha de espaços, horários e comunicação com as equipes responsáveis.

As configurações do sistema definem limites, portanto, datas disponíveis para pedidos.

## Funcionalidades Principais

-   **Aceite de termo de responsabilidade:** O requisitante deve aceitar eletronicamente o termo antes de iniciar a solicitação.
-   **Seleção de espaço físico:** Exibe espaços físicos vistoriados e aprovados pela equipe.
-   **Escolha do período e dos horários:** Usuário escolhe dias e horários livres, conforme disponibilidade da equipe.
-   **Cadastro de observações obrigatórias:** Permite registrar necessidades, justificativas e outros detalhes relevantes da transmissão.
-   **Confirmação e geração de assinatura digital (hash):** Ao final do fluxo, o sistema gera uma confirmação detalhada com todos os dados da solicitação e uma 'assinatura digital' baseada em SHA-256, calculada a partir das informações essenciais do pedido, incluindo local físico e termo de responsabilidade. Essa assinatura serve para garantir a integridade dos dados e comprovar que nenhum campo foi alterado após a confirmação.
-   **Envio automático de e-mails:** Após a confirmação, envia os dados completos para a equipe responsável, que entrará em contato com o requisitante.
-   **Controle de sessões e restrições de múltiplos pedidos:** Limita transmissões simultâneas por pessoa e validações em toda etapa do fluxo.

## Fluxo Resumido de Uso

1. **Usuário acessa a tela inicial e aceita o termo de responsabilidade.**
2. **Seleciona um espaço físico disponível** para transmissão.
3. **Escolhe o período desejado** (datas de início e fim), dentro das regras institucionais.
4. **Visualiza e seleciona horários livres** conforme os dias escolhidos.
5. **Registra uma observação obrigatória** sobre a transmissão.
6. **Confirma a solicitação**, visualizando o resumo e assinatura/hash.
7. **Sistema envia o resumo por e-mail** para a equipe.

## Endpoints e Funcionalidades

-   **Aceite do termo de responsabilidade:**
    `GET/POST /backend/transmissao/termo/`

    -   GET: Exibe o termo vigente e valida limite de pedidos ativos.
    -   POST: Registra o aceite do termo na sessão.

-   **Listar espaços físicos disponíveis:**
    `GET/POST /backend/transmissao/espaco-fisico/`

    -   GET: Lista todos os ambientes ativos para seleção.
    -   POST: Seleciona e registra o espaço físico na sessão do usuário.

-   **Selecionar período (datas):**
    `POST /backend/transmissao/periodo/`

    -   POST: Recebe as datas de início e fim desejadas, valida regras institucionais e armazena na sessão.

-   **Listar horários disponíveis por dia:**
    `GET /backend/transmissao/horarios/`

    -   GET: Lista, para cada dia do período, os horários livres (considerando reservas e buffers do espaço).

-   **Reservar horários e registrar observação:**
    `POST /backend/transmissao/horarios/`

    -   POST: Recebe os horários escolhidos e a observação, valida conflitos e cria o pedido de transmissão.

-   **Confirmação e envio:**
    `GET /backend/transmissao/confirmacao/`

    -   GET: Retorna os dados da solicitação para conferência, envia por e-mail e gera assinatura/hash de segurança.

## Regras de Negócio e Validações

-   **O termo de responsabilidade deve ser aceito antes de qualquer ação.**
-   **Espaços físicos são sujeitos à vistoria e disponibilidade.**
-   **Só é possível reservar horários em dias e horários realmente livres, sem conflitos com outros pedidos ou _buffers_ (tempo de vistoria/montagem/desmontagem).**
-   **Observação é obrigatória no pedido, o evento deve ser sucintamente descrito**
-   **Toda ação é validada em múltiplas etapas, com controle de sessão e hashes para segurança.**
