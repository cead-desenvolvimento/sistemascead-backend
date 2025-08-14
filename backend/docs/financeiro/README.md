# App: Financeiro - Vínculos de Bolsistas

## Visão Geral

Este app gerencia o **controle financeiro e de vínculos de bolsistas** nos cursos da instituição, incluindo associações de edital, função e oferta, acompanhamento de fichas, ajustes de datas de vínculo e relatórios rápidos de situação dos bolsistas.  
É voltado principalmente para as equipes financeira, administrativa e de gestão acadêmica.

## Funcionalidades Principais

- **Listar cursos com bolsistas ativos:** Permite visualizar rapidamente todos os cursos que possuem pelo menos um bolsista ativo.
- **Listar bolsistas ativos de um curso:** Consulta detalhada dos bolsistas atualmente vinculados a um curso específico.
- **Consultar últimas fichas cadastradas:** Exibe as inscrições/fichas de bolsistas mais recentes, facilitando o acompanhamento.
- **Atualizar datas de vínculo:** Permite à equipe financeira corrigir datas de início e/ou fim do vínculo de bolsistas.
- **Listar editais e ofertas vigentes:** Exibe apenas editais e ofertas de curso que estão atualmente válidos, para garantir a associação correta.
- **Listar funções de bolsista com ficha UAB:** Facilita a gestão de funções específicas do programa UAB.
- **Associar edital, função e oferta:** Permite criar, atualizar, consultar ou remover associações entre edital, função de bolsista e oferta de curso (estrutura essencial para o vínculo correto de bolsistas).

## Fluxo de Uso

1. **Equipe financeira/gestão acessa o módulo**, autenticada via JWT e permissões específicas.
2. **Consulta os cursos, bolsistas e fichas** conforme a demanda operacional.
3. **Atualiza dados de vínculo** de bolsistas quando necessário (ex: prorrogação, desligamento).
4. **Cria ou ajusta associações de edital-função-oferta** para permitir novos vínculos.
5. **Gera relatórios e consultas rápidas** para prestação de contas ou acompanhamento de gestão.

## Principais Endpoints (Views)

- **Listar cursos com bolsistas ativos:**  
  `GET /backend/financeiro/cursos-bolsistas-ativos/`
- **Listar bolsistas de um curso:**  
  `GET /backend/financeiro/curso/{ac_curso_id}/bolsistas-ativos/`
- **Listar últimas fichas:**  
  `GET /backend/financeiro/ultimas-fichas/`
- **Atualizar datas de vínculo de um bolsista:**  
  `PUT /backend/financeiro/atualizar-vinculo/`  
  (informando o id da ficha e as novas datas)
- **Listar editais atuais:**  
  `GET /backend/financeiro/editais-atuais/`
- **Listar ofertas de curso atuais:**  
  `GET /backend/financeiro/ofertas-atuais/`
- **Listar funções com ficha UAB:**  
  `GET /backend/financeiro/funcoes-ficha-uab/`
- **Associar edital-função-oferta:**  
  `GET/POST/PUT /backend/financeiro/associar-edital-funcao-oferta/`
- **Remover/consultar associação específica:**  
  `GET/DELETE /backend/financeiro/associar-edital-funcao-oferta/{id}/`

## Permissões e Segurança

- **Autenticação JWT obrigatória**
- Permissões específicas para cada operação, como:
    - `IsGerenciadorDataVinculacaoFichas` (ajustes e consultas financeiras)
    - `IsAssociadorEditalFuncaoFichaOferta` (associações entre editais, funções e ofertas)
- Todas as operações respeitam as regras de negócio para evitar inconsistências em vínculos.

## Público-alvo

- **Equipe financeira**: gerenciamento do vínculo e dados cadastrais de bolsistas.
- **Equipe administrativa**: manutenção de editais, ofertas e funções disponíveis.
- **Gestores acadêmicos**: consulta de informações para tomada de decisão e prestação de contas.

## Observações Técnicas

- Todas as views são baseadas em APIView do DRF, com documentação automática via drf-spectacular.
- Utiliza autenticação via JWT.
- Os endpoints retornam dados serializados prontos para frontend/admin.
- Os modelos utilizados (bolsista, curso, oferta, edital, função) vêm do core acadêmico.
- Algumas operações (POST/PUT de associação) utilizam update_or_create para evitar duplicidades.
- O filtro de datas garante que só vínculos ativos sejam considerados em relatórios e consultas.
- O sistema suporta múltiplos tipos de funções (inclusive UAB) e associações complexas entre edital, função e oferta.

---

> Este manual serve como referência para desenvolvedores e operadores financeiros do sistema. Sugestões de novos fluxos e melhorias podem ser registradas neste documento.
