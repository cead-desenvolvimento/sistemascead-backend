# Guia para usuários do grupo **Acadêmico - administradores**

As tarefas no sistema são divididas em dois grupos:

-   Telas administrativas;
-   Painel administrativo.

---

## Telas administrativas

As ''telas administrativas'' foram criadas para para reunir as funcionalidades mais usadas pela equipe em um ambiente mais simples e direcionado.

Em [https://sistemascead.ufjf.br/](https://sistemascead.ufjf.br/) há um menu com breve descrição da funcionalidade do item. As principais são:

### Associação usuário — edital

Permite associar uma pessoa a um edital específico. Útil para um coordenador acompanhar inscrições, validar e obter relatórios de um edital específico. O grupo Administradores - acadêmico possui acesso a todas as funções de todos os editais.

> **Não basta apenas associar a pessoa. Se ela não tiver senha cadastrada não conseguirá acesso!**

### Relatório de inscrição e validação dos editais

Exibe relatórios com o status de inscrição e validação de candidatos em editais.

### Validação de documentos do edital

Interface de validação de documentos submetidos pelos candidatos nos editais e atribuição de notas.

### Lançamento de frequência

Tela para lançamento da frequência mensal dos bolsistas. Para lançar frequência, a pessoa deve:

-   Ser coordenador de curso (cadastro do curso painel administrativo);
-   Estar no grupo ''lançadores de frequência'';
-   Possuir senha para acesso ao sistema.

### Lançamento de frequência — disciplinas

Permite o cadastro e inativação das disciplinas associadas ao curso, para que o coordenador as veja no lançamento de frequência.

> **Mudar o nome da disciplina faz com que todo o histórico de lançamento mude! Utilize a edição com cautela.**

---

## Painel administrativo

Apenas usuários com _status_ de ''membro da equipe'' possuem acesso ao painel administrativo, que é utilizado para o gerenciamento de dados essenciais. ''Membro da equipe'' refere-se ao tipo de cadastro do usuário feito pelo suporte. Todos os dados das ''telas administrativas'' podem ser visualizados e modificados pelo painel. Conforme já mencionado, as telas são para facilitar a manipulação dos dados.

### Acesso ao Painel Administrativo

-   Clicar no botão ''Admin'' quando logado [https://sistemascead.ufjf.br/](https://sistemascead.ufjf.br/), ou;
-   Ir até [https://sistemascead.ufjf.br/backend/admin/](https://sistemascead.ufjf.br/backend/admin/).

---

## Painel Administrativo: Visão Geral

A equipe do acadêmico também possui acesso limitado ao painel administrativo Django, com permissão para adicionar e modificar modelos essenciais à sua rotina.

### Modelos de maior interesse

| Módulo                               | Ação disponível      | Descrição                                                        |
| ------------------------------------ | -------------------- | ---------------------------------------------------------------- |
| (Acadêmico) Cursos                   | Adicionar, Modificar | Cadastro de cursos ofertados no CEAD                             |
| (Acadêmico) Cursos - ofertas         | Adicionar, Modificar | Cadastro de ofertas e associação com cursos                      |
| (Acadêmico) Cursos - ofertas - polos | Adicionar, Modificar | Polos vinculados a cada oferta de curso                          |
| (Acadêmico) Mantenedores             | Adicionar, Modificar | Instituições ou organizações responsáveis por cursos             |
| (Acadêmico) Tipos de curso           | Adicionar, Modificar | Classificações dos cursos (ex.: graduação, especialização, etc.) |
| (Comum) Formações                    | Adicionar, Modificar | Formações acadêmicas reconhecidas pelo sistema                   |
| (Comum) Titulações                   | Adicionar, Modificar | Títulos acadêmicos (ex.: Especialista, Mestre, Doutor)           |

Esses modelos são utilizados com frequência por administradores acadêmicos. O cadastro correto desses itens é essencial para o funcionamento de diversas funcionalidades, como inscrições, vinculação de fichas, geração de relatórios e exibição no site institucional do CEAD. O cadastro e edição são intituivos, exceto o cadastro dos editais, que não é trivial e será abordado em outro arquivo.

### Modelos com permissão apenas de visualização

Além dos modelos acima, diversos outros estarão visíveis no painel, mas não precisam (nem devem) ser alterados diretamente. Esses modelos são usados como base por outras funcionalidades.

Exemplos:

-   Municípios;
-   Pessoas;
-   Unidades da Federação;
-   Fichas;
-   Frequências;
-   etc.

Esses modelos são utilizados em segundo plano por diversas funcionalidades do sistema. Qualquer alteração nesses dados deve ser feita com cautela, ou preferencialmente sob orientação da equipe técnica.

Em regra esses dados são tratados por outras equipes ou por usuários externos.

---

## Recomendações gerais

-   Sempre confira os dados antes de salvar;
-   Use a busca do Django admin para localizar rapidamente um curso ou oferta;
-   Evite alterar diretamente modelos no Django admin sem orientação prévia;
-   Sempre que possível, utilize as telas específicas para evitar erros.

Para mais detalhes sobre permissões ou ajustes, entre em contato com a equipe de suporte técnico.
