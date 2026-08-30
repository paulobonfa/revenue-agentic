# Revenue Agentic

**Agente de análise e planejamento de receita, powered by Revenue Mechanics / Equações Bonfarianas 2.1.0-rc1.**

**Revenue Agentic** é o produto agentic deste repositório. **Revenue Mechanics** é seu motor matemático determinístico: o agente interpreta o problema e comunica a decisão; a skill governa o workflow; o código executa os cálculos e os gates de confiabilidade.

A versão 2.0 substitui a ideia de uma coleção de fórmulas isoladas por uma pequena **álgebra geradora**. O objetivo é permitir que um gestor de tráfego, CRO, CRM, vendas ou C-level parta de um resultado e o decomponha até as variáveis que o produziram — ou faça o caminho inverso e calcule o que precisa mudar para atingir uma meta.


## Componente principal: Agent Skill

A partir da v2.1, o principal componente do Revenue Agentic é a **Revenue Mechanics Agent Skill** em [`skills/revenue-mechanics/SKILL.md`](skills/revenue-mechanics/SKILL.md). Ela transforma o framework em uma capacidade reutilizável por agentes de IA: a IA interpreta o problema e escolhe o workflow, enquanto o motor Python determinístico executa os cálculos e aplica os gates de confiabilidade.

**Arquitetura:**

```text
Usuário → Agent/LLM → Revenue Mechanics Skill → solver determinístico → engine matemático
                                     ↓
                         ICO + guards + consistência
```

A escolha por **skill-first** é deliberada: o conhecimento e o workflow precisam ser portáveis e composáveis; cálculos não devem depender do raciocínio probabilístico de um LLM. Um runner de agente é fornecido em [`agent/revenue_mechanics_agent.py`](agent/revenue_mechanics_agent.py) apenas como camada opcional de orquestração.

### Uso direto da skill

```bash
python skills/revenue-mechanics/scripts/validate_skill.py
python skills/revenue-mechanics/scripts/revenue_solver.py media-funnel --input skills/revenue-mechanics/assets/example_input.json
```

Veja [`skills/revenue-mechanics/references/WORKFLOWS.md`](skills/revenue-mechanics/references/WORKFLOWS.md) para os modos suportados.

A decisão arquitetural e o benchmarking estão documentados em [`docs/AGENT_ARCHITECTURE.md`](docs/AGENT_ARCHITECTURE.md).

## Princípio

> **Resultado → decomposição → diagnóstico → alavanca → meta**
>
> **Meta → variáveis necessárias → limites → plano**

O núcleo prático pode ser resumido como:

\[
\boxed{Resultado = Volume \times Probabilidades \times Valor}
\]

## O que mudou na v2

Foram removidos do core os modelos que não atingiram o gate de produção ou que exigiam sofisticação desproporcional ao ICP, incluindo a antiga curva logarítmica de saturação, o ARR triangular, `RC = T(1-churn)` e o LTV triangular.

Entraram no lugar:

- cadeia universal de funil;
- cadeia universal de custo;
- cadeia de valor econômico esperado;
- Revenue/CRO solver reversível;
- base ativa e MRR por estoque/fluxo;
- MRR bridge, GRR e NRR;
- eficiência marginal observada;
- elasticidade-arco para intervalos discretos;
- verificações automáticas de consistência dos dados;
- classificação explícita de confiabilidade por família.

## Núcleo matemático

### 1. Fluxo

\[
N_{i+1}=N_i p_i
\]

\[
N_n=N_0\prod_i p_i
\]

### 2. Custo entre etapas

\[
c_{i+1}=\frac{c_i}{p_i}
\]

### 3. Valor econômico esperado

\[
V_i=p_iV_{i+1}
\]

### 4. Receita transacional

\[
Revenue=Outcome\times AverageValue
\]

### 5. Aquisição paga

\[
Impressions=\frac{1000\,Budget}{CPM}
\]

### 6. Estado/estoque

\[
Stock_t=Stock_{t-1}+Inflows_t-Outflows_t
\]

### 7. Crescimento multiplicativo

\[
\frac{Y_1}{Y_0}=\prod_i\left(\frac{x_{i,1}}{x_{i,0}}\right)^{a_i}
\]

### 8. Eficiência marginal observada

\[
mCost=\frac{\Delta Cost}{\Delta Outcome}
\]

## Exemplo: de CPM até CAC

\[
CPC=\frac{CPM}{1000\,CTR}
\]

Se `q = Sessions/Clicks`:

\[
CPS=\frac{CPC}{q}
\]

Se `CVR_{S,L}=Leads/Sessions`:

\[
CPL=\frac{CPS}{CVR_{S,L}}
\]

Se `CVR_{L,C}=Customers/Leads`:

\[
CAC_{media}=\frac{CPL}{CVR_{L,C}}
\]

Logo:

\[
\boxed{CAC_{media}=\frac{CPM}{1000\,CTR\,q\,CVR_{S,L}\,CVR_{L,C}}}
\]

A mesma cadeia pode ser invertida para calcular o **CPL máximo**, **CPC máximo**, **CPM máximo** ou uma **conversão mínima** compatível com a economia final do negócio.

## Confiabilidade e uso

O ICO (Índice de Confiabilidade Operacional) **não é uma probabilidade estatística**. Ele é uma governança de produção baseada em cinco critérios: validade matemática, robustez dos dados, validação externa, estabilidade das premissas e utilidade para o ICP.

- **CORE_A (≥95):** identidade/diagnóstico, liberado para produção.
- **CORE_B (90–94,99):** planejamento condicionado, liberado com premissas explícitas.
- **CONDITIONAL (80–89,99):** disponível apenas com avisos e escopo.
- **EXPERIMENTAL (<80):** não entra no produto principal.

Veja [`docs/VALIDATION_REPORT.md`](docs/VALIDATION_REPORT.md) e [`docs/MATHEMATICAL_SPEC.md`](docs/MATHEMATICAL_SPEC.md).

## Validação automatizada

```bash
python scripts/validate_production.py
```

O comando valida primeiro a estrutura da Agent Skill e depois executa a suíte matemática, os workflows JSON-in/JSON-out, os guards e o stress test. O mesmo gate roda automaticamente no GitHub Actions em Python 3.10, 3.11 e 3.12.

O gate executa:

1. testes determinísticos sintéticos;
2. fixtures de comunidade;
3. cases públicos;
4. testes round-trip das variações algébricas;
5. stress test aleatório de 20.000 cenários;
6. gate mínimo de confiabilidade do core.

## Escopo deliberado

Este projeto **não tenta substituir MMM, modelos bayesianos, causal inference ou forecasting financeiro avançado**. Eles podem ser apropriados em operações maiores, mas não são necessários para a maioria das decisões do ICP do framework.

A regra é parcimônia: **complexidade só entra quando reduz materialmente o erro da decisão.**
