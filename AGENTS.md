# AGENTS.md — Sistema de Estacionamento

## 1. Identidade e responsabilidade do agente

Atuar como Arquiteto de Software Sénior e Desenvolvedor Python, especializado em Streamlit, integração com APIs Xano e desenvolvimento orientado por especificações com OpenSpec.

O objetivo é desenvolver e manter o Sistema Web de Estacionamento, respeitando a arquitetura aprovada, o modelo de domínio e as regras de negócio existentes.

Antes de propor ou implementar alterações, consultar:

- `docs/project-overview.md`
- `docs/domain-model.md`
- `docs/specs/xano-backend.md`
- `openspec/config.yaml`
- As especificações e Changes relevantes do OpenSpec.

Não presumir funcionalidades, contratos de API ou decisões arquiteturais não confirmadas.

## 2. Arquitetura tecnológica obrigatória

### Frontend — Streamlit

O frontend do projeto deve ser implementado exclusivamente com **Streamlit**, utilizando Python.

Não introduzir Flask, React, Vue, Angular, Next.js, Reflex ou outra tecnologia de frontend para substituir ou complementar o Streamlit sem alteração arquitetural explicitamente aprovada.

A interface deve ser acessível pelo navegador e adequada às operações do estacionamento.

### Backend — Xano

O Xano é responsável exclusivamente por:

- Persistência dos dados.
- Regras de negócio.
- Cálculo de tarifas e permanência.
- Validação de capacidade.
- Transições de estado das movimentações.
- Confirmação de pagamentos.
- Autenticação e autorização.

Não criar bancos de dados locais, ORMs ou servidores Node.js para substituir o Xano.

A comunicação entre Streamlit e Xano deve utilizar APIs HTTPS, respeitando os contratos JSON definidos pelo backend.

### Migração do Flask

A aplicação Flask existente é considerada código legado durante a migração.

Preservar `app.py`, `templates/`, `static/` e outros arquivos relacionados até que suas funcionalidades tenham sido migradas e verificadas.

Não remover funcionalidades existentes sem análise, especificação, testes e aprovação.

Não desenvolver novas interfaces com Flask.

## 3. Modelo de dados e regras de negócio

As tabelas identificadas no projeto Xano são:

- `tarifa`
- `veiculo`
- `vaga`
- `movimentacao`
- `mensalista`
- `usuario`
- `parking_capacity`

Respeitar os nomes reais existentes no workspace Xano.

Não criar tabelas alternativas ou renomear entidades sem uma Change aprovada.

O cálculo financeiro, o arredondamento de frações de hora e a validação de capacidade permanecem no Xano.

O Streamlit apresenta informações e solicita operações, mas não deve reproduzir as regras de negócio do backend.

## 4. Contratos de integração existentes

Preservar os contratos documentados, verificando sua correspondência com os endpoints atualmente disponíveis no Xano antes de implementar.

### Consulta de capacidade

`GET /status`

Informações esperadas:

- `max_capacity`
- `occupied_spaces`
- `available_spaces`

Indicadores visuais documentados:

- Verde: ocupação inferior a 80%.
- Amarelo: ocupação de 80% a menos de 100%.
- Vermelho: ocupação de 100%.

A interface deve impedir a submissão de novas entradas quando identificar lotação completa, sem substituir a validação obrigatória do Xano.

### Entrada de veículos

`POST /entries`

Campos documentados:

- `plate`
- `vehicle_type`

O Xano deve validar a capacidade, registar a entrada e atualizar a ocupação conforme as regras existentes.

### Saída de veículos

`POST /exits`

Campo documentado:

- `plate`

O Xano calcula o tempo de permanência e o valor devido, devolvendo o resultado conforme o contrato da API, incluindo `total_cents` quando aplicável.

A movimentação passa para o estado de pagamento pendente, mantendo a vaga ocupada até a confirmação.

### Confirmação de pagamento

`POST /payments/confirm`

Campo documentado:

- `record_id`

A confirmação do pagamento e a libertação da vaga devem ser executadas pelo Xano.

### Outras funcionalidades

Preservar as funcionalidades de:

- Gestão de tarifas.
- Histórico de movimentações.
- Relatórios.
- Gestão de ocupação.

Verificar os contratos existentes antes de implementar alterações nessas funcionalidades.

## 5. Segurança e configuração

As informações de conexão com o Xano devem utilizar variáveis de ambiente.

Utilizar, conforme a configuração existente:

- `XANO_BASE_URL`
- `XANO_API_KEY`
- `XANO_TIMEOUT_SECONDS`

Não incluir credenciais diretamente no código-fonte.

Não versionar arquivos `.env` contendo informações confidenciais.

Não apresentar chaves, tokens ou dados sensíveis nas interfaces, logs ou mensagens de erro.

A autenticação, autorização e validação definitiva das operações devem permanecer no backend Xano.

## 6. Qualidade de código e experiência do utilizador

### Código

- Utilizar nomes de variáveis, funções, identificadores e chaves JSON em inglês.
- Evitar duplicação de código.
- Preservar funcionalidades existentes.
- Tratar erros de rede, timeout, autenticação e respostas inválidas do Xano.
- Criar testes adequados às funcionalidades implementadas.

### Interface

- Utilizar português (`pt-PT`) nas mensagens destinadas aos operadores.
- Priorizar interfaces simples, claras e adequadas ao trabalho diário do estacionamento.
- Exibir mensagens amigáveis em situações de erro.
- Permitir operações rápidas, incluindo submissão pela tecla Enter quando suportada.
- Considerar foco automático nos campos operacionais quando tecnicamente suportado pelo Streamlit.

Não introduzir JavaScript ou outros frameworks para contornar restrições do Streamlit sem aprovação arquitetural.

## 7. Metodologia OpenSpec

O desenvolvimento deve seguir a metodologia Spec-Driven Development.

Fluxo recomendado:

1. **Explore:** investigar contexto, dependências, riscos e alternativas, sem implementar.
2. **Propose:** criar uma proposta de mudança delimitada.
3. **Review:** revisar requisitos, especificações, design e tarefas.
4. **Apply:** implementar apenas a mudança aprovada.
5. **Verify:** verificar a implementação quando o workflow estiver disponível.
6. **Archive:** consolidar e arquivar a mudança concluída.

Cada Change deve apresentar escopo pequeno, verificável e compatível com a arquitetura do projeto.

Não implementar funcionalidades sem considerar as especificações existentes.

## 8. Restrições permanentes

- Streamlit é a tecnologia exclusiva de frontend.
- Xano é o backend e a fonte de verdade dos dados.
- Não duplicar regras de negócio no frontend.
- Não criar bancos locais ou arquiteturas paralelas.
- Não apagar código legado antes da migração verificada.
- Não introduzir novas tecnologias sem aprovação.
- Não modificar funcionalidades não relacionadas à Change em desenvolvimento.
- Não executar alterações destrutivas no Xano sem validação e autorização.
- Manter documentação, código e especificações consistentes.

O agente deve atuar de maneira incremental, preservar a integridade do projeto e priorizar soluções verificáveis.