# Revenue Agentic Architecture — Why the core is Skill-first

## Decision

Revenue Agentic ships primarily as a **portable Revenue Mechanics Agent Skill** backed by a deterministic Python engine. A thin agent runner is optional.

```text
User
  ↓
General-purpose Agent / LLM
  ↓
Revenue Mechanics Skill
  ↓
Deterministic solver
  ↓
Validated mathematical engine
  ↓
ICO + data-consistency + model guards
```

## Why not a standalone autonomous agent as the core?

The central value of Revenue Mechanics is not autonomous action; it is **repeatable domain procedure plus mathematically exact calculation**.

A standalone agent would make the probabilistic LLM the center of the architecture. That creates an unnecessary failure mode: arithmetic, formula selection and boundary conditions could drift with prompting or model changes.

The skill-first pattern keeps responsibilities clean:

- **LLM/agent:** interprets the business question, maps metrics to the right workflow, identifies missing/incompatible data, explains results and distinguishes diagnosis from causality.
- **Skill:** defines procedure, guardrails, reliability policy and when to load detailed domain references.
- **Solver/engine:** performs deterministic arithmetic and refuses mathematically invalid inputs.
- **Agent runner:** optional orchestration wrapper for deployments that want autonomous multi-step interaction.

## Benchmarking basis

The choice follows current agent architecture patterns:

1. **Agent Skills open specification** defines a portable skill as a directory with `SKILL.md` plus optional `scripts/`, `references/` and `assets/`, designed for progressive disclosure.
   - https://agentskills.io/specification

2. **OpenAI Agents SDK (2026)** explicitly incorporates progressive disclosure via skills and tool use, while keeping the agent harness separate from computation/sandbox infrastructure.
   - https://openai.com/index/the-next-evolution-of-the-agents-sdk/

3. **OpenAI GPT-5.6 builder guidance** recommends moving deterministic filtering, aggregation and orchestration into programmatic tool calling so model tokens are reserved for judgment.
   - https://openai.com/index/builders-guide-to-gpt-5-6/

4. **Anthropic Agent Skills** likewise frames skills as portable procedural knowledge with executable scripts and on-demand references instead of creating a new bespoke agent for each domain.
   - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

## Production principle

> The model must never be the numerical source of truth when a validated deterministic function exists.

The architecture therefore optimizes for:

- portability;
- composability;
- auditability;
- reproducibility;
- low context overhead;
- mathematical reliability;
- independence from any single model provider.

## When the optional agent is useful

Use `agent/revenue_mechanics_agent.py` when the deployment needs the model to:

- accept natural-language questions;
- choose among multiple Revenue Mechanics workflows;
- iteratively ask for/collect missing business inputs;
- execute solver calls;
- compare scenarios;
- generate an executive or operational explanation.

The agent remains an orchestration layer and must not replace the solver.
