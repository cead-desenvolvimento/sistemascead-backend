# Guia para usuários do grupo **Financeiro - administradores**

As tarefas no sistema são divididas em dois grupos:

-   Telas administrativas;
-   Painel administrativo.

---

## Telas administrativas

As ''telas administrativas'' foram criadas para para reunir as funcionalidades mais usadas pela equipe em um ambiente mais simples e direcionado.

Em [https://sistemascead.ufjf.br/](https://sistemascead.ufjf.br/) há um menu com breve descrição da funcionalidade do item. As principais são:

### Associação edital — função da ficha — oferta

Permite associar um edital a uma função da ficha e a uma oferta. Esse vínculo é fundamental para a geração de ficha do candidato. A tela foi criada para evitar cadastros errados de ficha e confusão nos bolsistas. Com ela, o bolsista poderá gerar somente a ficha designada a ele.

### Envio de e-mail para preenchimento da Ficha UAB

Permite o envio de mensagem por e-mail para que o bolsista aprovado preencha a ficha de cadastro UAB. A ficha só pode ser preenchida com o código enviado.

### Atividades gerais do Financeiro com o cadastro dos bolsistas

Interface para visualizar, editar e gerenciar as fichas dos bolsistas, além de permitir o acompanhamento de sua situação. As datas de início e fim de vínculo do bolsista que a equipe definir farão a ativação/inativação do vínculo do bolsista. É possível também visualizar quais cursos possuem bolsistas ativos.

A tela foi pensada para facilitar o fluxo de ativação/inativação do bolsista, após a percepção de que o sistema antigo faz com que o vínculo seja complexo e nem sempre inativado a contento, por problemas no relacionamento dos dados como eram.

### Lançamento de frequência

Tela para lançamento da frequência mensal dos bolsistas. Para lançar frequência, a pessoa deve:

-   Ser coordenador de curso (cadastro do curso painel administrativo);
-   Estar no grupo ''lançadores de frequência''
-   Possuir senha para acesso ao sistema.

### Lançamento de frequência — disciplinas

Permite o cadastro e inativação das disciplinas associadas ao curso, para que o coordenador as veja no lançamento de frequência.

> **Mudar o nome da disciplina faz com que todo o histórico de lançamento mude! Utilize a edição com cautela.**

### Lançamento de frequência — relatório

Exibe um relatório geral das frequências lançadas, com possibilidade de filtragem por curso.

### Relatório — acesso de bolsistas ao Moodle

Gera um relatório com os registros de acesso dos bolsistas ao ambiente virtual Moodle.

---

## Painel administrativo

Apenas usuários com _status_ de ''membro da equipe'' possuem acesso ao painel administrativo, que é utilizado para o gerenciamento de dados essenciais. ''Membro da equipe'' refere-se ao tipo de cadastro do usuário feito pelo suporte. Todos os dados das ''telas administrativas'' podem ser visualizados e modificados pelo painel. Conforme já mencionado, as telas são para facilitar a manipulação dos dados.

### Acesso ao painel administrativo

-   Clicar no botão ''Admin'' quando logado [https://sistemascead.ufjf.br/](https://sistemascead.ufjf.br/);
-   Ir até [https://sistemascead.ufjf.br/backend/admin/](https://sistemascead.ufjf.br/backend/admin/).

---

## Painel administrativo: visão geral

A equipe financeira também possui acesso limitado ao painel administrativo Django, com permissão para adicionar e modificar modelos essenciais à sua rotina.

### Modelos de maior interesse

| Módulo                                 | Ação disponível      | Descrição                                                              |
| -------------------------------------- | -------------------- | ---------------------------------------------------------------------- |
| (Financeiro) Fichas                    | Adicionar, Modificar | Gerenciamento dos dados das fichas dos bolsistas                       |
| (Financeiro) Frequências               | Adicionar, Modificar | Os dados de lançamento de frequência dos coordenadores                 |
| (Financeiro) Frequências — disciplinas | Adicionar, Modificar | A relação de disciplinas lançadas na frequência                        |
| (Financeiro) Funções dos bolsistas     | Adicionar, Modificar | Define a função do bolsista no sistema (ex.: tutor, coordenador, etc.) |
| (Financeiro) Períodos de lançamento    | Adicionar, Modificar | Períodos válidos para o lançamento de frequência                       |

### Modelos com permissão apenas de visualização

Além dos modelos acima, diversos outros estarão visíveis no painel, mas não precisam (nem devem) ser alterados diretamente. Esses modelos são usados como base por outras funcionalidades.

Exemplos:

-   Editais e seus vínculos;
-   Dados das pessoas;
-   Cotas e marcações;
-   Cursos e ofertas;
-   etc.

Em regra esses dados são tratados por outras equipes ou por usuários externos.

---

# Recomendações gerais

-   Certifique-se de que os vínculos entre **edital, função e oferta** estejam cadastrados antes da data fim de validação dos candidatos, para que os aprovados possam criar a ficha;
-   Utilize os relatórios para verificar inconsistências;
-   Evite alterar diretamente modelos no Django admin sem orientação prévia;
-   Sempre que possível, utilize as telas específicas para evitar erros.

Para mais detalhes sobre permissões ou ajustes, entre em contato com a equipe de suporte técnico.
