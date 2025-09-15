# App: Integração Wordpress – Polos e Cursos

## Por que este app existe?

O site do CEAD consultava diretamente a base de dados do sistema antigo. A base foi normalizada e migrada para PostgreSQL.
Este app foi criado para **substituir todas as consultas do site ao banco antigo**, provendo uma API REST padronizada.

> **O consumo dessas APIs estão prontos em https://github.com/cead-desenvolvimento/sistemascead-wordpress**

## Visão Geral

O app oferece endpoints públicos (REST) para integração de dados institucionais de polos e cursos, prontos para consumo no Wordpress ou em qualquer outro site/sistema.  
Toda a lógica de atualização, disponibilidade e padronização das informações passa a ser centralizada no sistema novo, sem dependências do banco legado.

## Funcionalidades Principais

-   **Listagem de cursos ativos de um polo**
-   **Contato do curso** (email, coordenador, telefone)
-   **Descrição e perfil do egresso do curso**
-   **Listagem e detalhes de polos**
-   **Consulta detalhada de um ou mais polos**
-   **Lista de polos ativos cadastrados**
-   **Polos ativos de um curso**
-   **Detalhes completos de um polo**
-   **Texto de apresentação do polo**
-   **Nome do polo só se houver oferta ativa**
-   **Horários de funcionamento do polo**

## Exemplos de Endpoints

-   `GET /backend/wordpress/polos/`
-   `GET /backend/wordpress/curso/{nome_curso}/contato/`
-   `GET /backend/wordpress/curso/{nome_curso}/descricao-perfil-egresso/`
-   `GET /backend/wordpress/polo/{nome_polo}/cursos/`
-   `GET /backend/wordpress/polo/{nome_polo}/`
-   `POST /backend/wordpress/polos/informacoes/`
-   `GET /backend/wordpress/polos/ids/`
-   `GET /backend/wordpress/polo/{nome_polo}/apresentacao/`
-   `GET /backend/wordpress/polo/{nome_polo}/oferta-ativa/`
-   `GET /backend/wordpress/polo/{nome_polo}/horario-funcionamento/`

## Público-Alvo

-   **Equipe de comunicação institucional**
-   **Secretarias e polos**
-   **Desenvolvedores de portais Wordpress**
-   **Usuários do site do CEAD** (visitantes, alunos, comunidade externa)

## Regras de Negócio

-   Apenas cursos e polos ativos/ofertados atualmente aparecem como disponíveis.
-   As informações exibidas no site agora são sempre extraídas do banco central do sistema acadêmico.
-   O nome informado nos endpoints deve ser igual ao cadastrado no sistema para resultados corretos.

## Observações Técnicas

-   Todas as respostas são em JSON padronizado, prontos para uso direto em sites.
-   Serializers específicos para cada tipo de consulta garantem consistência.
-   Endpoints sem autenticação, mas facilmente adaptáveis para uso restrito.
-   API documentada via drf-spectacular/OpenAPI.

---

> **Resumo:** Este app existe para manter o site do CEAD funcional e atualizado após o fim do banco antigo, centralizando as integrações em uma API REST moderna e segura.
