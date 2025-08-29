# App: Editais

## Visão Geral

Este app é responsável por **gerenciar os processos seletivos (editais)** do sistema, desde a criação do edital, gerenciamento de vagas, inscrições, validações, envio de notificações aos aprovados por e-mail, até a geração de relatórios.  
É voltado principalmente para equipes acadêmicas, administrativas e de apoio, que precisam controlar inscrições, avaliações e comunicações relacionadas aos editais de cursos e bolsas.

## Funcionalidades Principais

- **Cadastro e consulta de editais**: Permite criar e listar processos seletivos, com controle de datas de inscrição, validação e validade.
- **Gerenciamento de vagas**: Cada edital pode possuir diversas vagas, cada uma com campos e critérios personalizados (verificar manual do usuário).
- **Inscrição de candidatos**: Candidatos podem se inscrever nas vagas de um edital, preenchendo campos e anexando documentos.
- **Validação das inscrições**: Avaliadores validam inscrições, atribuem pontuações, justificam decisões e aprovam/reprovam documentos enviados.
- **Envio de e-mails automáticos**: Permite disparar emails (individuais ou em massa) para candidatos solicitando preenchimento de ficha.
- **Controle de cotas e formação**: Gerencia cotas (ações afirmativas) e titulações/formações dos inscritos.
- **Relatórios**: Gera relatórios para acompanhamento dos editais, vagas, inscritos e resultados.
- **Permissões de acesso**: Controle fino de permissões para cada ação, de acordo com grupos de usuários (acadêmico, validador, financeiro, etc).

## Principais Modelos Envolvidos

- `EdEdital` — Define o edital (processo seletivo) e suas datas.
- `EdVaga` — Define cada vaga/disponibilidade dentro de um edital.
- `EdPessoaVagaInscricao` — Inscrição de uma pessoa em uma vaga.
- `EdPessoaVagaValidacao` — Registra a validação, pontuação e status do inscrito.
- `EdPessoaVagaJustificativa` — Registra justificativas de avaliação.
- `EdPessoaVagaCampoCheckbox`, `EdPessoaVagaCampoCombobox`, `EdPessoaVagaCampoDatebox` — Armazenam os campos preenchidos pelos inscritos (incluindo uploads).
- `EdCota`, `EdPessoaFormacao` — Gerenciam cotas e formações vinculadas.

## Fluxo Geral de Uso

1. **Criação do edital** pela equipe administrativa/acadêmica.
2. **Cadastro das vagas** e definição dos campos/criterios de cada vaga.
3. **Abertura das inscrições** para candidatos.
4. **Validação das inscrições** por avaliadores, com atribuição de notas e justificativas.
5. **Envio de notificações** (ex: resultado, solicitação de documentos, etc).
6. **Consulta e geração de relatórios** para acompanhamento e prestação de contas.

## Permissões e Perfis

- **Acadêmico - administradores:** acesso total aos editais, inclusive relatórios e envio de emails.
- **Validador de editais:** pode validar inscrições e lançar pontuações/justificativas.
- **Financeiro:** pode visualizar alguns relatórios, associar editais a funções, e lançar frequência.
- **Emissor de mensagem de ficha:** pode enviar emails para candidatos de vagas específicas.

## Observações Técnicas

- O app utiliza **DRF (Django REST Framework)** para expor endpoints de consulta, validação, envio de email e relatórios.
- O envio de e-mails utiliza o backend do Django, com validação de sessão segura via hash.
- Vários endpoints possuem documentação automática usando **drf-spectacular** e decorators `@extend_schema`.

## Regras de Negócio Importantes

- Só é possível validar inscrições no período de validação do edital.
- Apenas usuários vinculados ao edital (ou admins) têm acesso às ações.
- O preenchimento de ficha é feito apenas via link único enviado por e-mail (digest SHA-256).
- Cada tipo de campo (checkbox, combobox, datebox) tem regras próprias de pontuação.
- Relatórios e listagens respeitam as permissões do usuário.

## Público-Alvo

- Equipe acadêmica/admin (controle total do processo)
- Validadores (banca avaliadora)
- Equipe financeira (para integração com pagamento/bolsas)
- Usuários externos/candidatos (apenas via preenchimento de ficha)

---

**Dúvidas comuns:**

- *Como cadastrar um novo edital?*  
  Acesse a área administrativa e use a opção “Novo Edital”.

- *Como enviar e-mails de ficha para todos os candidatos?*  
  Use o endpoint/botão de envio em massa, após selecionar a vaga.

- *Como restringir ações de validação?*  
  A permissão é concedida por grupo no Django Admin.

---

> **Este arquivo pode (e deve) ser expandido conforme novas regras de negócio ou fluxos surgirem!**
