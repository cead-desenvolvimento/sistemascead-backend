# Administração do **Sistema de Pedido de Transmissão**

## O que você precisa saber antes de começar

- **Login:** O requisitante deve estar logado no sistema.
- **Permissão:** O requisitante deve pertencer ao grupo **"Requisitantes de transmissão"**.
- **Acesso:** O login é realizado com o CPF, **sem pontos ou traços**. O requisitante precisa estar cadastrado previamente na tabela `cm_pessoa`.
  - O cadastro inclui nome, CPF e e-mail.
  - Para cadastrar um novo requisitante, utilize o Admin do Django e clique em **(Comum) Pessoas**.

## Como funciona o sistema

- O requisitante acessa o sistema em [https://sistemascead.ufjf.br/transmissao/](https://sistemascead.ufjf.br/transmissao/) e segue o fluxo orientado na tela.
- O fluxo é protegido por sessão e _hash_ da sessão.
- As datas e horários disponíveis são automaticamente gerenciados pelo sistema conforme a configuração feita pela equipe.

## Configuração e administração

Para que o sistema funcione corretamente, é necessário configurar, no painel administrativo do Django:

- **Limites de atendimento da equipe:** tabela `tr_limites`.
- **Termo de aceite:** tabela `tr_termo`.
- **Espaço físico:** ao menos um espaço ativo em `tr_espaco_fisico`, preenchendo os campos de tempo necessário para vistoria/montagem e desmontagem de equipamentos.
- **Disponibilidade da equipe:** tabela `tr_disponibilidade_equipe`.

A configuração é evidente para profissionais da área, e o _frontend_ irá exibir mensagens de erro, no fluxo do pedido de transmissão, caso alguma etapa esteja pendente. No painel administrativo, procure pela palavra **(Transmissão)** para encontrar os cadastros relevantes.

## Sobre a recusa de transmissões

O sistema não possui aceite de transmissão, pois a confirmação depende de outras etapas fora do sistema, devido à complexidade do evento. No entanto, **transmissões recusadas devem ser marcadas no sistema** para liberar a agenda, já que um pedido impede novas solicitações para o mesmo período.

## Envio de e-mail

Ao final do processo, caso haja e-mails cadastrados na tabela `tr_transmissao_email`, as notificações serão enviadas automaticamente com os dados da transmissão. Útil para para informar aos interessados.
