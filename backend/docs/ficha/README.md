# App: Ficha UAB

## Visão Geral

Este app implementa o **preenchimento público da ficha de inscrição de candidatos** em processos seletivos, garantindo que apenas pessoas autorizadas acessem e preencham suas informações pessoais, endereço, telefone, dados bancários e ficha funcional.  
Seu objetivo principal é centralizar e automatizar o recebimento e validação desses dados, integrando etapas essenciais de coleta com segurança (acesso via código enviado por e-mail), e o PDF gerado está de acordo com as exigências da Portaria 309/2024 CAPES/MEC.

## Importante

A geração da ficha somente é permitida quando houver associação do edital ao tipo de vínculo do bolsista.

-   A associação à oferta do curso é opcional, pois coordenadores gerais não possuem vínculo direto com cursos.

## Funcionalidades Principais

-   **Validação de código e CPF:** Apenas o candidato que recebeu o código por e-mail pode acessar a ficha.
-   **Preenchimento guiado:** O candidato informa endereço, telefones e dados bancários, todos com validação.
-   **Preenchimento da ficha funcional:** Dados pessoais e funcionais são validados e persistidos.
-   **Geração de PDF da ficha:** Após o envio da ficha, o sistema gera um PDF oficial para download, pronto para assinatura ou upload em outros sistemas.
-   **Fluxo de sessão seguro:** Cada etapa valida a sessão e evita que o candidato preencha mais de uma vez ou salte etapas.
-   **Documentação OpenAPI:** Todos os endpoints são documentados via drf-spectacular para integração frontend/backend.

## Fluxo de Uso

1. **Acesso do candidato**  
   O envio do e-mail para o candidato é realizado pela equipe do CEAD por meio de recurso acessível no menu principal do sistema.

2. **Validação do código e CPF**  
   Se válido, sessiona a permissão para continuar o fluxo.

3. **Preenchimento de endereço, telefones e dados bancários**  
   Informações salvas no banco e validadas.

4. **Preenchimento da ficha funcional**  
   Dados pessoais, formação, função, etc.

5. **Geração do PDF da ficha**  
   Download automático do PDF com todas as informações do candidato.

## Principais Endpoints (Views)

-   **Validação de código/CPF**  
    `POST /backend/ficha/validar-codigo/{codigo}/`  
    Recebe o código e CPF, valida o acesso e inicia a sessão do candidato.

-   **Cadastro de endereço, telefones e banco**  
    `GET/POST /backend/ficha/endereco-telefone-banco/`  
    Consulta ou salva os dados informados pelo candidato.

-   **Cadastro/consulta da ficha funcional**  
    `GET/POST /backend/ficha/preencher/`  
    Consulta os dados já preenchidos ou salva novos dados da ficha do candidato.

-   **Geração do PDF**  
    `GET /backend/ficha/pdf/`  
    Gera e retorna o PDF com todas as informações cadastradas.

## Permissões e Segurança

-   **Validação de sessão a cada etapa**  
    Só acessa a etapa se tiver código e hash válidos na sessão.
-   **Bloqueio de múltiplos envios**  
    A ficha pode ser acessada novamente para edição sempre que necessário, utilizando o mesmo link de validação.
-   **Isolamento total entre candidatos**  
    Cada candidato só acessa e preenche sua própria ficha.

## Público-alvo

-   **Candidatos**: Preenchimento da ficha de inscrição via link enviado por e-mail.

## Observações Técnicas

-   Todos os endpoints são baseados em APIView do DRF.
-   Os serializers cuidam das validações de CPF, endereço, telefone, banco e ficha funcional.
-   O PDF é gerado usando `pdfkit` + template HTML, acessando dados já validados.
-   Consome dados de outras apps como cursos, funções, municípios e UF.
-   Validações de banco, UF e município são realizadas contra registros já existentes.
-   O código foi desenhado para ser integrado a sistemas externos via API REST.

---

> Este arquivo serve como base para novos desenvolvedores e também para a equipe operacional entender o fluxo do candidato ao preencher a ficha pública.
