# Production Gates

Uma família só entra no core quando passa simultaneamente pelos gates abaixo.

## Gate 1 — domínio matemático
- análise dimensional coerente;
- inversões reproduzem a identidade original;
- limites de taxas em `[0,1]` quando representam probabilidades;
- casos de zero e infinito tratados explicitamente;
- nenhuma circularidade apresentada como informação nova.

## Gate 2 — round trip
Cada variação algébrica deve reconstruir a variável original. A suíte atual executa centenas de cenários aleatórios por identidade.

## Gate 3 — confronto externo
Para cada família, usar três classes de evidência:
1. cenário sintético neutro;
2. situação publicada pela comunidade;
3. case ou definição pública verificável.

Formas algébricas inversas não recebem “evidência empírica independente” artificial: por serem a mesma identidade, são validadas por prova/round-trip. A evidência externa é aplicada à família que a identidade representa.

## Gate 4 — integridade dos dados
Uma identidade deve ser capaz de detectar dados incompatíveis. O motor usa erro relativo e tiers A–D. Dados `D` (>10% de discrepância) não devem alimentar planejamento reverso sem investigação.

## Gate 5 — produção
- `CORE_A`: ICO ≥95;
- `CORE_B`: ICO ≥90;
- média do Production Core (A+B) ≥94;
- erro máximo do stress test de identidades < `1e-10`;
- 100% dos testes automatizados aprovados.

## Gate 6 — causalidade
Nenhuma identidade deve ser transformada automaticamente em afirmação causal. “CVR explica mecanicamente a variação” é diferente de “a nova página causou a variação”.
