# Visão Geral: Sistema Web de Estacionamento

**Objetivo Principal**
Desenvolver uma aplicação web para gerir o fluxo de veículos num parque de estacionamento, permitindo o acesso via navegador (browser) para automatizar o registo de entradas e saídas, o controlo de lugares e o cálculo de pagamentos.

**Público-Alvo (Utilizadores)**
* Operadores de caixa (acesso ao painel web para registo diário e cobrança).
* Administradores (acesso ao painel web para gestão de tarifas, utilizadores e relatórios).

**Funcionalidades Principais**
* **Dashboard Web:** Interface centralizada e responsiva acessível via browser.
* **Registo de Entrada e Saída:** Captura de matrículas e cálculo automático do valor a pagar com base no tempo de permanência.
* **Gestão de Ocupação:** Visualização em tempo real dos lugares disponíveis e ocupados.
* **Histórico e Relatórios:** Registo em base de dados de todas as transações para consulta administrativa.


## Arquitetura Tecnológica

### Frontend
- Tecnologia: Streamlit.
- Linguagem: Python.
- O Streamlit será utilizado exclusivamente para implementar as interfaces do sistema.

### Backend
- Tecnologia: Xano.
- Responsável pelas APIs, regras de negócio, validações e persistência dos dados.

### Desenvolvimento
- Editor: Visual Studio Code.
- Controle de versão: Git e GitHub.
- Documentação e especificações: OpenSpec.
- Agente de IA: Gemini CLI.

### Restrições Arquiteturais
O frontend deve ser desenvolvido exclusivamente com Streamlit.
Não introduzir Flask, React, Vue, Angular, Next.js ou outra tecnologia de frontend sem uma alteração arquitetural explicitamente aprovada.
A migração deverá preservar as funcionalidades existentes do sistema de estacionamento.