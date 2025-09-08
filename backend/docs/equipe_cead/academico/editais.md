# Cadastro e Gerenciamento de Editais

Esta seção orienta sobre o uso do painel administrativo para cadastrar e configurar **editais** no sistema CEAD. Usuários do grupo ''Acadêmico - administradores'' e com _status_ de ''membro da equipe'' possuem acesso a funcionalidade.

---

## Acessando a Seção de Editais

-   Acesse: [https://sistemascead.ufjf.br/backend/admin/cead/ededital/](https://sistemascead.ufjf.br/backend/admin/cead/ededital/) ou;
-   Clique em **(Editais) Editais** no painel administrativo para visualizar ou cadastrar novos editais.

---

## Cadastro de Novo Edital

-   Acesse: [https://sistemascead.ufjf.br/backend/admin/cead/ededital/add/](https://sistemascead.ufjf.br/backend/admin/cead/ededital/add/) ou;
-   Clique em **(Editais) Editais** no painel administrativo, e clique no botão `Adicionar (Editais) Edital`, que se encontra no canto superior direito da tela.

---

## Cadastro do Edital

O formulário de cadastro do edital é direto e envolve principalmente:

-   **Numeração do edital** (o sistema provê o próximo número disponível);
-   **Título do edital**;
-   **Datas de início e fim** das etapas (inscrição, validação, validade);
-   **Permissão para inscrição em múltiplas vagas** do mesmo edital.

> Após preencher os dados principais, clique em **"Salvar e continuar editando"**.

Isso permitirá que o _link_ **"Ir para as vagas"** apareça ao final da página, facilitando o próximo passo: o cadastro dos campos das vagas vinculadas ao edital.

---

## Cadastro dos campos das vagas do edital

Cada edital pode conter **uma ou mais vagas**. Ao clicar em "Ir para as vagas", você será direcionado à edição da primeira vaga cadastrada.

Para cada vaga, você poderá definir os campos de inscrição dos candidatos. Existem **três tipos principais de campo**, que podem ter pontuação e exigir **assinatura digital** no arquivo enviado pelo candidato.

---

### 1. Checkbox (marcação simples)

-   Utilizado para respostas do tipo **"Sim / Não"**

---

### 2. Combobox (seleção de grupos de pontuação)

-   Ideal para situações com múltiplas opções com pesos diferentes  
    (exemplo: número de certificados — 0, 1, 2+ com pontuações distintas)
-   Deve-se definir a **ordem** de exibição
-   Os campos do tipo combobox são agrupados automaticamente pelo mesmo rótulo do campo (EdCampo)

> Se os campos não estiverem agrupados é possível que sejam de dois rótulos de campos diferentes, pois há muitos nomes repetidos, e unificá-los faria perder dados do sistema antigo.

> **Não** é necessário criar campo com pontuação 0, o sistema dará a possibilidade ao candidato de não escolha desse tipo de campo.

---

### 3. Datebox (pontuação por tempo)

-   Utilizado para experiências que pontuam por **períodos de tempo**
    -   Exemplo: _Experiência com EAD: 5 pontos por ano, até no máximo 20 pontos_
-   Deve-se informar:
    -   A pontuação por unidade de tempo;
    -   Qual é a unidade de tempo que multiplica a pontuação;
    -   O limite máximo de pontuação.

---

## Dicas e Cuidados

-   **Salvar para todas as vagas**: Há a possibilidade de aplicar os mesmos campos a várias vagas simultaneamente;
-   **Evite editar ou apagar campos após o início das inscrições**, pois isso pode impactar negativamente os candidatos já inscritos;
    -   **Sempre consulte o suporte técnico antes de realizar essas alterações;**
    -   **É possível haver perda de dados nesse caso!**
-   **Alterar datas do edital** após a criação **não causa problemas**;
-   A inscrição será feita em [https://sistemascead.ufjf.br/inscricao](https://sistemascead.ufjf.br/inscricao), e as datas cadastradas determinam a disponibilidade do edital na tela;
-   O candidato poderá visualizar a justificativa em [https://sistemascead.ufjf.br/editais/justificativa](https://sistemascead.ufjf.br/editais/justificativa), desde que o edital tenha iniciado a época de validação e ainda não tenha passado da data de validade.

---

## Recomendações Finais

-   Use **"Salvar e continuar editando"** com frequência para evitar perda de dados;
-   Utilize o _link_ **"Ir para as vagas"** para navegar rapidamente entre a configuração do edital e suas vagas.

Em caso de dúvidas ou situações específicas, entre em contato com a equipe de suporte técnico.
