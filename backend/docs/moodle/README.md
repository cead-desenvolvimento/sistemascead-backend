# App: Relatórios de Acesso Moodle

## Visão Geral

Este app oferece **relatórios gerenciais sobre os acessos dos bolsistas ao Moodle**, cruzando os meses de frequência lançada e os cursos vinculados. Ele permite que coordenadores, setor financeiro e gestores acompanhem a efetiva atuação dos bolsistas na plataforma Moodle — essencial para comprovação de atividade e, em muitos casos, autorização do pagamento.

## IMPORTANTE

Os relatórios utilizam o **webservice do Moodle** do [https://ead.ufjf.br/](https://ead.ufjf.br/), que é executado no **container `site-cead`** (verificar cron). O **script de integração** atualiza a tabela `fi_frequencia_moodle`.

> **Observação:** Moodles diferentes do [https://ead.ufjf.br/](https://ead.ufjf.br/) **não são consultados**. Para esses casos, verifique as informações diretamente na tela de relatório.

> **Observação técnica:** A consulta ao Moodle da UEMA foi feita em PHP, com _crawl_ (`preg_match`, etc). Foram abertos dois chamados na UEMA, pedindo acesso ao _webservice_, e é claro que sequer responderam. Não fiz em Django porque gerou muita dependência no projeto. Detalhes técnicos: [https://github.com/cead-desenvolvimento/sistemascead-c10](https://github.com/cead-desenvolvimento/sistemascead-c10)

## Funcionalidades Principais

-   **Listagem dos meses com acessos registrados no Moodle:** Permite selecionar apenas os meses em que houve lançamento de acessos para análise.
-   **Consulta dos cursos com registros de acesso:** Permite filtrar os relatórios por curso em determinado mês, mostrando apenas cursos com algum acesso no Moodle.
-   **Relatório detalhado de acessos:** Gera um relatório com coordenador, cursos, bolsistas e os registros de acesso individualizados, inclusive último acesso, horário de consulta e identificação do usuário no Moodle.

## Fluxo Resumido de Uso

1. **Usuário (coordenador, financeiro ou gestor) acessa a tela de relatórios Moodle.**
2. **Seleciona o mês** (entre os meses em que houve registro de acesso no Moodle).
3. **Seleciona o(s) curso(s) de interesse** (opcional; pode visualizar todos).
4. **Visualiza o relatório detalhado**, com coordenador, cursos, bolsistas e seus registros de acesso no Moodle.

## Endpoints e Funcionalidades

-   **Listar meses com registro de acesso no Moodle:**  
    `GET /backend/relatorio-moodle/meses/`

    -   Retorna todos os meses (FiDatafrequencia) com algum acesso registrado para relatórios.

-   **Listar cursos com registros de acesso em determinado mês:**  
    `GET /backend/relatorio-moodle/cursos/{fi_datafrequencia_id}/`

    -   Retorna cursos disponíveis para o mês selecionado.

-   **Relatório detalhado de acessos no Moodle:**  
    `GET /backend/relatorio-moodle/detalhado/{fi_datafrequencia_id}/?cursos=1,2,3`
    -   Retorna o relatório de acessos filtrado por mês (obrigatório) e, opcionalmente, por lista de cursos.

## Regras de Negócio e Validações

-   **Somente meses com frequência Moodle registrada aparecem para consulta.**
-   **Usuário precisa ter permissão de visualizador de relatório Moodle.**
-   **Cursos só aparecem para seleção se tiverem bolsista com acesso registrado no Moodle naquele mês.**
-   **Relatório detalhado sempre traz último acesso, data/hora da consulta e dados do usuário.**

## Perfis e Permissões

-   **Visualizador de relatório Moodle:** Pode acessar todos os relatórios e realizar consultas por curso e mês.
-   **Equipe financeira e gestores:** Utilizam para acompanhamento, prestação de contas e comprovação de atuação dos bolsistas.

## Público-Alvo

-   **Coordenação acadêmica**
-   **Equipe financeira**
-   **Gestores institucionais**
-   **Auditores**

## Observações Técnicas

-   Todas as views exigem autenticação JWT e permissão específica.
-   Consultas otimizadas usando filtros dinâmicos por mês e curso.
-   Dados serializados e prontos para exibição em painéis/admins ou exportação.
-   Documentação automática via drf-spectacular/OpenAPI.
