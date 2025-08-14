# App: Frequência de Bolsistas

## Visão Geral

Este app é responsável por **registrar, controlar e consultar a frequência mensal dos bolsistas** vinculados a cursos e projetos, integrando as etapas essenciais entre ficha, disciplinas, frequência e autorização de pagamento.  
O módulo é utilizado por **coordenadores**, **equipe financeira** e **gestores administrativos** para garantir a conformidade dos pagamentos e controle de atuação dos bolsistas.

## Funcionalidades Principais

- **Lançamento de frequência mensal:** O coordenador responsável lança a frequência dos bolsistas sob sua coordenação, apontando disciplinas trabalhadas e autorizando o pagamento.
- **Cadastro de disciplinas por curso:** Administração das disciplinas vinculadas a cada curso, para lançamento preciso da atuação do bolsista.
- **Listagem de meses com frequência registrada:** Histórico dos meses para os quais já houve frequência lançada (para relatórios e consultas).
- **Relatórios administrativos:** Geração de relatórios sintéticos por mês, curso, coordenador e bolsistas, permitindo gestão efetiva dos vínculos e pagamentos.
- **Controle de permissões:** Cada endpoint possui autenticação JWT e restrições de perfil (coordenador, editor de disciplinas, visualizador administrativo etc).

## Fluxo Resumido de Uso

1. **Bolsista gera a ficha** e tem seu vínculo ativo em uma oferta de curso.
2. **Coordenador acessa o sistema** e vê os cursos sob sua responsabilidade.
3. **Sistema lista os bolsistas ativos com ficha** e as disciplinas cadastradas em cada curso.
4. **Coordenador seleciona bolsistas, aponta disciplinas e autoriza pagamento** (lança frequência do mês vigente).
5. **Sistema registra a frequência** e impede lançamento duplicado ou fora do período.
6. **Equipe financeira e gestão consultam relatórios administrativos** por mês, curso e coordenador.

## Endpoints e Funcionalidades

- **Lançamento de frequência mensal:**  
  `GET/POST /backend/frequencia/`  
  - GET: Lista bolsistas, disciplinas e fichas do mês anterior para coordenador.
  - POST: Lança frequência para os bolsistas do mês atual, apontando disciplinas e autorização de pagamento.

- **Listar meses com frequência lançada:**  
  `GET /backend/frequencia/meses/`  
  - Retorna até 6 meses anteriores com frequência já registrada.

- **Listar cursos com disciplinas:**  
  `GET /backend/frequencia/cursos/`  
  - Lista cursos que possuem ao menos uma disciplina cadastrada.

- **Cadastrar/gerenciar disciplinas do curso:**  
  `GET/POST /backend/frequencia/curso/{id}/disciplinas/`  
  - GET: Lista disciplinas do curso.
  - POST: Cadastra nova disciplina.
  - PUT: Atualiza disciplina.

- **Relatório administrativo de frequência:**  
  `GET /backend/frequencia/relatorio/{mes_id}/`  
  - Retorna relatório completo por mês, curso, coordenador e bolsistas.

- **Relatório pessoal do coordenador:**  
  `GET /backend/frequencia/relatorio-coordenador/{mes_id}/`  
  - Retorna o próprio relatório do coordenador para o mês corrente.

## Regras de Negócio e Validações

- **Só bolsista com ficha ativa pode ter frequência lançada.**
- **Coordenador só pode lançar frequência para seus próprios cursos.**
- **Só pode lançar frequência no período habilitado do mês vigente.**
- **Frequência lançada autoriza pagamento do bolsista para o mês/disciplina.**
- **Não é permitido lançar frequência duplicada nem editar meses antigos.**
- **Toda disciplina deve estar cadastrada e ativa para lançamento válido.**

## Perfis e Permissões

- **Coordenador:** Lança frequência de seus cursos, consulta relatórios pessoais.
- **Editor de disciplina:** Mantém cadastro/edição de disciplinas dos cursos.
- **Visualizador administrativo:** Consulta relatórios sintéticos de frequência.
- **Financeiro:** Consome relatórios para processamento de pagamento dos bolsistas.

## Público-Alvo

- **Coordenadores:** Operação do lançamento mensal, acompanhamento da equipe.
- **Equipe administrativa/financeira:** Consulta de relatórios e prestação de contas.
- **Gestores acadêmicos:** Acompanhamento macro do cumprimento de carga horária dos bolsistas.

## Observações Técnicas

- Todas as views são baseadas em APIView, com autenticação JWT e uso de DRF.
- Uso de serializers para garantir integridade dos dados e respostas padronizadas.
- Lançamento e consulta de frequência sempre referenciam a ficha vigente do bolsista.
- Os relatórios se baseiam no vínculo entre ficha, frequência e disciplina.
- API documentada via drf-spectacular/OpenAPI.

---

> Este documento deve ser revisado em caso de alteração no fluxo de vínculo do bolsista ou nas regras de lançamento de frequência.
