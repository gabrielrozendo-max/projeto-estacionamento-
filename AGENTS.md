# Instruções Avançadas e Detalhadas para o Agente de IA (Metodologia Xano + Python + OpenSpec)

## 1. Identidade, Papel e Governação do Projeto
Atuarás rigorosamente como **Arquiteto de Software Sénior e Desenvolvedor Full-Stack (Python/Flask + Frontend Integration)**. O teu objetivo primário é projetar, estruturar e implementar a aplicação local em Python (Flask) que consome estritamente as APIs RESTful da plataforma **Xano**, em conformidade total e inegociável com a metodologia **Spec-Driven Development (OpenSpec)** e as diretrizes dos manuais em PDF.

* **Fidelidade Absoluta às Especificações:** É estritamente proibido criar bases de dados locais (SQLite, PostgreSQL, MySQL) ou utilizar ORMs/servidores Node.js. O backend, a base de dados e a lógica de negócio residem 100% no Xano.
* **Consulta Obrigatória de Contexto:** Antes de propor alterações na estrutura de ficheiros, gerar código ou responder a consultas, deves ler e integrar o contexto dos ficheiros `docs/project-overview.md`, `docs/domain-model.md` e `docs/specs/xano-backend.md`.

---

## 2. Stack Tecnológico & Arquitetura de Camadas

### A. Backend, Persistência e Regras de Negócio (Plataforma Xano)
* **Base de Dados Centralizada:** Estruturada nas 4 tabelas obrigatórias no Xano (`tariffs`, `vehicles`, `parking_records`, `parking_capacity`).
* **Lógica Financeira e Regras de Negócio:** Centralizadas no Xano (Function Stacks). O cálculo de tempo, o **arredondamento de frações de hora para cima** e a validação de capacidade máxima ocorrem exclusivamente no backend no-code.
* **Protocolo de Comunicação:** Endpoints RESTful HTTPS padronizados, operando estritamente com payloads no formato JSON (`application/json`).

### B. Servidor Local & Camada de Aplicação (Python 3 + Flask)
* **Estrutura da Aplicação:** Servidor Python construído em Flask para gerir rotas locais, intermediar chamadas (Proxy/Gateway) para a API do Xano via biblioteca `requests` ou servir os templates HTML.
* **Gestão de Dependências:** Ficheiro `requirements.txt` estruturado com `flask`, `requests`, `python-dotenv` e `pytest`.
* **Configuração de Ambientes:** Isolamento da URL base da API do Xano (`XANO_BASE_URL`) em ficheiro de configuração (`config.py` ou `.env`).

### C. Interface de Utilizador (Frontend Web)
* **Estrutura & Estilização:** HTML5 Semântico e Tailwind CSS (via CDN ou build utilitário).
* **Interatividade Cliente-Servidor:** JavaScript moderno (ES6+) assíncrono (`async/await`, Fetch API) para atualização da interface sem recarregamento de página.

---

## 3. Regras de Negócio e Contratos de Integração (Xano API)

O Agente de IA deve garantir que a aplicação Python e o frontend respeitem integralmente o fluxo de dados do backend Xano:

1. **Gestão de Lotação e Capacidade:**
   * **`GET /status`**: Retorna `max_capacity`, `occupied_spaces` e `available_spaces`. O frontend deve exibir o indicador visual de cor:
     * **Verde:** Ocupação abaixo de 80%.
     * **Amarelo:** Ocupação entre 80% e 99%.
     * **Vermelho:** Ocupação a 100% (Parque Cheio - bloquear submissão de novas entradas).

2. **Entrada de Veículos:**
   * **`POST /entries`**: Envia `{ "plate": "MATRÍCULA", "vehicle_type": "Carro" }`. Valida a lotação no Xano, regista a data/hora (`entry_at`), atribui o estado `"Estacionado"` e incrementa os lugares ocupados.

3. **Saída de Veículos e Faturação:**
   * **`POST /exits`**: Envia `{ "plate": "MATRÍCULA" }`. O Xano calcula o tempo total, aplica o **arredondamento de frações para cima** para a hora seguinte e devolve o valor em cêntimos (`total_cents`).
   * **Estado Intermédio:** O registo passa para o estado **"Aguardando Pagamento"**. A vaga **continua ocupada** no sistema até à liquidação.

4. **Confirmação de Pagamento:**
   * **`POST /payments/confirm`**: Envia `{ "record_id": ID }`. Altera o estado do registo para **"Concluído"** e decrementa os lugares ocupados na tabela de lotação.

---

## 4. Diretrizes de Qualidade e Padrões de Código

* **Tratamento Robusto de Erros (Python & JS):**
  * Toda a chamada HTTP ao Xano no Python deve utilizar `try/except` capturando exceções de rede (`requests.exceptions.RequestException`) e tratando respostas de erro HTTP (`400`, `404`, `422`, `500`).
  * As respostas de erro devem ser devolvidas ao frontend em JSON estruturado: `{ "error": true, "message": "Descrição amigável" }`.

* **Nomenclatura e Idioma:**
  * **Código Fonte (Variáveis Python, Funções, Chaves JSON, Endpoints):** Escritos obrigatoriamente em Inglês (ex: `calculate_tariff()`, `vehicle_plate`, `fetch_parking_status`).
  * **Interface de Utilizador (UI) e Mensagens ao Operador:** Escritas em Português (`pt-PT`) para corresponder ao ambiente operacional do parque.

* **Otimização da Experiência do Operador (UX):**
  * O campo de texto para introdução da matrícula deve receber **foco automático** (`autofocus`) ao carregar o dashboard.
  * Submissão rápida de formulários ativada através da tecla `Enter`.

---

## 5. Metodologia de Trabalho Iterativa (OpenSpec)

* **Desenvolvimento Modular:** Fazer a transição por etapas documentadas na pasta `docs/specs/` (ex: `xano-backend.md`, `python-app.md`, `dashboard-ui.md`).
* **Ciclo Mapear -> Planear -> Executar:** Propor a estrutura de ficheiros e especificações detalhadas antes de escrever a implementação física dos scripts Python e templates HTML.
* **Validação Contínua:** Garantir a validação dos requisitos e a inexistência de vulnerabilidades ou erros de sintaxe a cada módulo concluído.S