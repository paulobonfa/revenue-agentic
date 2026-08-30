# Revenue Mechanics 2.0 — Relatório de Validação para Produção

**Data:** 29/08/2026  
**Build:** 2.1.0-rc1 (core matemático 2.0 + integração skill-first)

## 1. Conclusão executiva

O build revisado passou o gate de produção definido antes da execução final:

- **36/36 testes automatizados aprovados**;
- **20.000 cenários aleatórios de stress test**;
- erro relativo máximo observado entre identidades equivalentes: **5,615×10⁻¹⁶**;
- **ICO Core A: 98,18/100**;
- **ICO Production Core (A+B): 95,96/100**;
- gate de produção: **PASS**.

O ICO não é probabilidade estatística de acerto futuro. Ele é um índice de governança que mede adequação para uso operacional a partir de validade matemática, robustez dos dados, validação externa, estabilidade das premissas e utilidade para o ICP.

A conclusão de produção é restrita ao **Core A+B**. Os módulos condicionais continuam disponíveis, mas não elevam nem reduzem artificialmente o score do núcleo.

---

## 2. Método

Cada família foi confrontada em três classes:

1. **sintético neutro:** cenário gerado sem ajustar números para “dar certo”;
2. **comunidade:** dados publicados por operadores, úteis inclusive para revelar inconsistências de tracking/definição;
3. **case/benchmark público:** dados publicados por plataformas, empresas ou estudos.

### Variações algébricas

Não é cientificamente útil fingir que `CPC = CPM/(1000·CTR)` e `CPM = 1000·CPC·CTR` são dois modelos empíricos independentes. São a mesma identidade rearranjada.

Por isso, **cada variação é testada por round-trip e property tests**, centenas de vezes, enquanto o confronto externo é feito no nível da família matemática representada.

Na suíte atual:

- 500 casos aleatórios para mídia e inversões;
- 500 casos aleatórios para funil/cadeia de custo;
- 500 casos aleatórios para Revenue/ROAS;
- 250 casos para recorrência, comparando solução fechada com iteração;
- 20.000 cenários adicionais no stress test de produção.

Isso é mais rigoroso para as inversões do que repetir três exemplos manuais.

---

## 3. Iterações e falhas encontradas

### Execução 1

20 testes executados, 18 aprovados e 2 reprovados.

As duas reprovações eram **fixtures esperados arredondados incorretamente**:

- solução fechada da base ativa;
- LTV finito em 12 ciclos.

As fórmulas foram recalculadas diretamente e os fixtures corrigidos.

### Execução 2

20/20 aprovados + stress test aprovado.

### Hardening

Depois do primeiro PASS, foram adicionados guards adicionais:

- churn 0% e 100% tratados explicitamente;
- GRR/NRR deixam de mascarar dados impossíveis;
- `marginal_cost` bloqueia interpretação de escala quando há intervenção estrutural marcada;
- payback retorna infinito quando o CAC não pode ser recuperado dentro do modelo.

### Execução final

22/22 aprovados + 20.000 stress cases + gate de confiabilidade aprovado.

### Hardening de integração v2.1

O primeiro teste com o validador oficial de skills encontrou uma chave de frontmatter não aceita (`compatibility`), embora o validador próprio retornasse PASS. A informação foi movida para `metadata`, o validador local passou a rejeitar chaves top-level incompatíveis e o production gate passou a validar a skill antes da matemática.

Também foram adicionados 14 testes de integração e guards, cobrindo os oito workflows JSON-in/JSON-out, payloads inválidos, períodos discretos, churn de 100%, MRR Bridge negativo e números não finitos. Resultado consolidado: 36/36.

---

## 4. ICO por família

| Família | ICO | Tier | Decisão |
|---|---:|---|---|
| Media identities | 99,30 | CORE_A | Produção |
| Aggregation & consistency | 99,05 | CORE_A | Produção |
| Funnel & cost chain | 98,65 | CORE_A | Produção |
| Recurring stock / MRR | 98,35 | CORE_A | Produção |
| Transactional revenue / ecommerce | 98,00 | CORE_A | Produção |
| MRR Bridge / retention | 97,75 | CORE_A | Produção |
| Break-even ROAS | 96,15 | CORE_A | Produção |
| CRO reverse planning | 94,85 | CORE_B | Produção com premissa |
| B2B reverse funnel | 92,20 | CORE_B | Produção com premissa |
| Expected-value chain | 91,30 | CORE_B | Produção com premissa |
| Marginal scale metrics | 90,00 | CORE_B | Produção com guard |
| Arc elasticity | 89,40 | CONDITIONAL | Opcional |
| Simple constant-churn LTV | 88,95 | CONDITIONAL | Opcional |
| Contribution LTV / payback | 88,30 | CONDITIONAL | Opcional |
| Revenue throughput rate | 88,00 | CONDITIONAL | Opcional |

---

## 5. Evidência — mídia

### Sintético

Budget R$12.000, CPM R$40, CTR 2%:

- 300.000 impressões;
- 6.000 cliques;
- CPC R$2.

A derivação `CPC = CPM/(1000·CTR)` reproduziu exatamente R$2.

### Comunidade

Fixture comunitário de Google Ads:

- spend US$5.000;
- 39.200 impressões;
- 941 cliques;
- 26 conversões.

CPC direto e CPC reconstruído por CPM/CTR coincidiram numericamente; o CPA reconstruído por `CPC/CVR` também coincidiu.

Fonte: https://www.reddit.com/r/googleads/comments/1tbawv6/overall_campaign_data/

### Case público 1

The Dental Marketing Firm reportou:

- US$6.256 spend;
- 26.196 impressões;
- 1.677 cliques;
- 317 leads;
- CTR 6,4%;
- CVR 18,9%;
- CPL US$19,74.

Reconstrução:

- CTR ≈ 6,4017%;
- CPL ≈ US$19,735;
- `CPC/CVR` = mesmo CPL.

Fonte: https://www.thedentalmarketingfirm.com/case-study

### Case público 2

Coach2Reach:

- ₹53.210 spend;
- 35.998 impressões;
- 1.073 cliques;
- 25 leads;
- CPL publicado ₹2.128.

Reconstrução: ₹2.128,40.

Fonte: https://sathyanarayanan.co/10x-growth-in-4-weeks-a-google-ads-case-study/

### Definições externas

Google Ads define CTR como cliques/impressões e CPC médio como custo/cliques, coerente com o núcleo.

Fontes:
- https://support.google.com/google-ads/answer/2615875?hl=pt-br
- https://support.google.com/google-ads/answer/14074?hl=pt-BR

**Decisão:** manter sem ajuste matemático.

---

## 6. Evidência — integridade de dados

Um post comunitário Shopify reportou simultaneamente:

- 2.496 sessões;
- CVR 0,89%;
- 33 vendas;
- AOV US$30,79;
- US$804,66 em vendas.

As identidades não fecham:

- `33 / 2.496 = 1,32%`, não 0,89%;
- `33 × 30,79 = US$1.016,07`, não US$804,66.

Fonte: https://www.reddit.com/r/shopify/comments/1cncksm

O framework classificou ambos como Tier D de consistência.

Isso não é defeito da fórmula: é exatamente uma razão para o **Consistency Gate** existir antes de qualquer diagnóstico ou solver.

Posts recentes da própria comunidade continuam relatando divergências de CVR/analytics, reforçando que instrumentação é risco real do ICP.

Exemplo: https://www.reddit.com/r/shopify/comments/1vue909/conversion_rate_has_been_way_off_since_aug_19th/

**Ajuste implementado:** `consistency_score()` e `consistency_tier()`.

---

## 7. Evidência — ecommerce / CRO

SearchBloom publicou um case com:

- sessions +37,2%;
- ecommerce CVR +39,1%;
- AOV +10,9%;
- revenue +111,7%;
- revenue/session +54,3%.

Modelo:

`1,372 × 1,391 × 1,109 = 2,116...`

Previsão mecânica: **+111,65%**, contra +111,7% publicado.

Para Revenue/Session:

`1,391 × 1,109 = 1,5426`

Previsão: **+54,26%**, contra +54,3%.

Fonte: https://www.searchbloom.com/case-studies/ecommerce-seo/beauty-product-shopify-store/

O case também explicita que ordem temporal não prova causalidade. Isso reforça a separação do framework entre **decomposição mecânica** e **efeito causal**.

**Decisão:** Revenue decomposition fica CORE_A; CRO reverse planning fica CORE_B porque o futuro depende de `ceteris paribus`.

---

## 8. Evidência — recorrência e MRR

Baremetrics define MRR como clientes ativos × valor médio faturado por conta e decompõe Net New MRR em New, Expansion e Churned MRR; também lista Reactivation e Contraction como movimentos relevantes.

No exemplo público:

- New MRR = 4.140;
- Expansion = 2.619;
- Reactivation = 473;
- Contraction = 158;
- Churn = 4.622;
- variação líquida = 2.452.

Reconstrução:

`4140 + 2619 + 473 - 158 - 4622 = 2452`.

Fonte: https://baremetrics.com/academy/saas-calculate-mrr

ChartMogul define GRR como retenção de receita excluindo expansão, coerente com o MRR Bridge do framework.

Fonte: https://chartmogul.com/pt-br/saas-metrics/grr/

**Decisão:** antiga fórmula `MRR = c·tm·(1-churn)` removida. Estado/estoque passa a ser a base de produção.

---

## 9. Evidência — LTV simples

Stripe apresenta explicitamente a versão simplificada do modelo SaaS em que lifetime esperado é o inverso do churn constante. Um churn mensal de 5% implica aproximadamente 20 meses de lifetime esperada dentro dessas hipóteses.

Fonte: https://stripe.com/en-br/guides/atlas/business-of-saas

Um caso comunitário relatou:

- 340 clientes;
- US$12/mês;
- MRR US$4.080;
- churn mensal 29%;
- CAC US$45.

Fonte: https://www.reddit.com/r/SaaS/comments/1rxzv8t/charged_12month_for_my_saas_had_340_customers/

O modelo simples produz:

- lifetime ≈ 3,45 ciclos;
- Revenue LTV ≈ US$41,38;
- inferior ao CAC de US$45 antes mesmo de ajustar margem.

A conclusão é coerente com a dificuldade econômica descrita no relato.

**Por que não CORE:** churn por cohort, expansão, preço e margem podem variar. A fórmula permanece como `SimpleRevenueLTV`, nunca como LTV verdadeiro universal.

---

## 10. Evidência — payback e margem

Benchmarkit define CAC Payback usando Sales & Marketing Expenses ajustados por gross margin e alerta que a métrica varia materialmente com ACV. O benchmark 2025 também mostra gross margin mediana distinta para subscription e services.

Fonte: https://www.benchmarkit.ai/2025benchmarks

Isso valida duas decisões:

1. CAC precisa informar escopo;
2. payback precisa usar contribuição/gross margin compatível, não revenue puro.

**Decisão:** payback continua condicional; o core não presume gross margin universal nem benchmark único.

---

## 11. Evidência — break-even ROAS

A derivação é direta:

`Revenue × ContributionMargin = Spend`

Logo:

`ROAS_BE = 1 / ContributionMargin`.

Uma discussão comunitária de PPC apresentou exatamente o raciocínio inverso: com US$2 por clique e US$40 de valor econômico por comprador, 5% de conversão é break-even (`2 / 0,05 = 40`).

Fonte: https://www.reddit.com/r/PPC/comments/1rpgc9y/is_there_even_any_point_in_trying_to_do_ppc/

**Decisão:** CORE_A, desde que `ContributionMargin` esteja corretamente definida.

---

## 12. Saturação: resultado da revisão

A antiga curva:

`CPA(x)=a ln(1+bx)`

foi removida do core.

Razões:

- forma funcional arbitrária para muitos canais;
- exigia calibração que o ICP normalmente não consegue sustentar;
- risco de extrapolação;
- não distinguia claramente mudança de regime e escala.

Substituição operacional:

- `mCAC = ΔSpend/ΔCustomers`;
- `mROAS = ΔRevenue/ΔSpend`;
- elasticidade-arco para intervalos.

### Ajuste encontrado durante testes

A relação diferencial local `mCAC = CAC/ε` não deve usar CAC final com elasticidade estimada num intervalo grande.

Para dados discretos, a produção usa midpoint + elasticidade-arco, que reconstruiu exatamente o slope do intervalo sintético testado.

Módulo permanece `CORE_B`/`CONDITIONAL` porque a interpretação exige regime comparável.

---

## 13. O que conta para produção

### Production Core

A+B alcançou:

**95,96/100**.

Nenhuma família abaixo de 90 entra nesse score.

### Conditional modules

- elasticidade-arco: 89,40;
- LTV churn constante: 88,95;
- Contribution LTV/payback: 88,30;
- throughput: 88,00.

Eles podem existir na biblioteca e no produto, mas precisam:

- mostrar premissa;
- indicar tier;
- impedir interpretação indevida;
- não ser apresentados como previsão causal.

---

## 14. Gate aprovado

Critérios definidos:

- testes automatizados: 100% PASS;
- stress identity error < 1e-10;
- Core A ≥95;
- Production Core A+B ≥94.

Resultado:

- 36/36 PASS;
- erro máximo = 5,615e-16;
- Core A = 98,18;
- A+B = 95,96.

**PRODUCTION GATE: PASS.**

---

## 15. Limitação que permanece

O framework está validado para:

- decompor resultados;
- detectar inconsistência;
- calcular identidades;
- calcular metas condicionais;
- avaliar economia unitária simples;
- orientar diagnóstico do ICP.

Ele **não está validado como modelo causal universal**.

Se uma empresa pergunta:

> “aumentar CTR em 10% causará +10% de receita?”

o framework só pode responder:

> “na identidade atual, mantendo as demais variáveis constantes, +10% de CTR implica +10% no componente multiplicativo correspondente.”

Para afirmar causalidade, é necessário experimento ou evidência empírica apropriada.

Essa limitação é intencional e faz parte da confiabilidade do framework, não uma deficiência a ser escondida.
