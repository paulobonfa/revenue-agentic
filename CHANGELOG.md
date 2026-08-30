# Changelog — Equações Bonfarianas

## [2.0.0-rc1] - 2026-08-29

### Reestruturado
- Framework convertido de coleção de fórmulas para **Revenue Mechanics**, uma álgebra operacional de métricas.
- Separação formal entre identidade, derivação, estimativa, forecast e hipótese causal.
- Introdução dos tiers de produção `CORE_A`, `CORE_B`, `CONDITIONAL` e `EXPERIMENTAL`.

### Adicionado
- Equação universal de funil `N_(i+1) = N_i * p_i`.
- Lei geral de custos `c_(i+1) = c_i / p_i`.
- Cadeia de valor econômico esperado `V_i = p_i * V_(i+1)`.
- CRO solver multiplicativo e cálculo reverso.
- Base ativa por estoque/fluxo, MRR, ARR, MRR Bridge, GRR e NRR.
- CAC de mídia separado de CAC fully loaded.
- mCAC, mROAS e elasticidade-arco com guard contra intervenção estrutural.
- Simple Revenue LTV / Contribution LTV explicitamente condicionados a churn constante.
- Break-even ROAS baseado em contribution margin.
- Consistency Score/Tier para detectar dashboards internamente incompatíveis.
- Suíte de testes sintéticos, comunitários, cases públicos e stress tests.

### Removido do core
- `CPA(x) = a * ln(bx + 1)` como lei geral de saturação.
- `MRR = c * tm * (1-churn)`.
- `ARR = c * tm * 78 * (1-churn)`.
- `RC = T * (1-churn)`.
- LTV triangular.
- Sales Velocity como forecast de receita.

### Corrigido
- Uso de elasticidade diferencial em intervalos discretos: substituído por elasticidade-arco + midpoint quando aplicável.
- ARR passa a significar run-rate anualizado (`12 * MRR`).
- LTV e payback passam a declarar premissas de churn/margem.

## [2.1.0-rc1] - 2026-08-29

### Adicionado
- Produto e agente publicados sob o nome **Revenue Agentic**, mantendo Revenue Mechanics como motor matemático interno.
- Revenue Mechanics como Agent Skill portátil (`skills/revenue-mechanics/SKILL.md`).
- Solver determinístico JSON-in/JSON-out para workflows de mídia, CRO, ecommerce, B2B, assinatura, escala e consistência.
- Referências progressivas de fórmulas, workflows, confiabilidade e guardrails.
- `AGENTS.md` para tornar a skill o ponto de entrada de agentes no repositório.
- Runner opcional para OpenAI Agents SDK em `agent/revenue_mechanics_agent.py`.
- Validador local do pacote Agent Skills.

### Arquitetura
- Skill-first: IA interpreta e orquestra; o motor Python é a autoridade matemática.
- Causalidade, forecast e benchmark permanecem explicitamente separados das identidades determinísticas.
- Benchmarking e decisão arquitetural documentados em `docs/AGENT_ARCHITECTURE.md`.

### Hardening de integração
- Frontmatter alinhado ao schema oficial de skills do Codex; compatibilidade movida para `metadata`.
- Validador da skill tornado dependency-free e integrado ao production gate.
- Oito workflows JSON-in/JSON-out cobertos ponta a ponta, com testes adicionais de payloads inválidos.
- Guards adicionados para valores não finitos/booleanos, períodos fracionários, churn de 100% na base ativa e MRR Bridge negativo.
- GitHub Actions adicionado para executar o gate em Python 3.10, 3.11 e 3.12.
