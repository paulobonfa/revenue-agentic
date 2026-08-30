# Revenue Mechanics 2.0 — Especificação Matemática de Produção

## 1. Finalidade

Revenue Mechanics é uma álgebra operacional para responder duas classes de pergunta:

1. **decomposição:** quais variáveis produziram o resultado observado?;
2. **planejamento reverso:** que valor uma ou mais variáveis precisam assumir para atingir uma meta, mantendo explícitas as premissas?

O framework não trata todas as relações como igualmente confiáveis. Cada cálculo pertence a uma classe:

- **Identidade:** verdade por definição;
- **Derivação:** consequência algébrica de identidades;
- **Estimativa:** parâmetro futuro assumido a partir de histórico/benchmark;
- **Cenário:** cálculo `ceteris paribus`;
- **Empírico/causal:** relação que precisa ser observada/testada e não nasce da álgebra.

A confiabilidade cai nessa mesma direção.

---

## 2. Variáveis primitivas

Sempre que possível, o modelo parte de contagens e valores observáveis:

- `Spend` / Budget;
- Impressions;
- Clicks;
- Sessions;
- Leads;
- MQL/SQL/Opportunities;
- Customers/Orders;
- Revenue;
- Units;
- Active Customers;
- New/Expansion/Contraction/Churn MRR.

Taxas e custos unitários são derivados dessas primitivas.

Regra de projeto: **não tratar uma métrica derivada como informação independente da própria base que a define**.

Exemplo:

\[
Leads=\frac{Budget}{CPL},\qquad CPL=\frac{Budget}{Leads}
\]

Substituir uma na outra retorna `Leads`; não cria explicação nova.

---

## 3. Mecânica universal de fluxo

Para uma etapa sequencial:

\[
\boxed{N_{i+1}=N_i p_i}
\]

onde `p_i` é uma taxa de passagem definida sobre exatamente a mesma população.

Para uma cadeia:

\[
\boxed{N_n=N_0\prod_{i=0}^{n-1}p_i}
\]

Conversão total:

\[
\boxed{p_{0,n}=\prod_i p_i}
\]

Input necessário para uma meta:

\[
\boxed{N_0^*=\frac{N_n^*}{\prod_i p_i}}
\]

Conversão necessária em uma etapa `k`:

\[
\boxed{p_k^*=\frac{p_{0,n}^*}{\prod_{i\neq k}p_i}}
\]

Condição de possibilidade:

\[
0\le p_k^*\le1
\]

Se o solver exigir mais de 100%, a meta é matematicamente impossível com as demais premissas constantes.

Drop-off:

\[
\boxed{Drop_i=N_i(1-p_i)}
\]

**Uso:** CRO, vendas, CRM, ecommerce, onboarding e qualquer pipeline sequencial.

---

## 4. Mecânica de mídia paga

### 4.1 CPM

\[
\boxed{CPM=\frac{Spend}{Impressions}\times1000}
\]

\[
\boxed{Impressions=\frac{1000\,Spend}{CPM}}
\]

### 4.2 CTR

\[
\boxed{CTR=\frac{Clicks}{Impressions}}
\]

\[
\boxed{Clicks=Impressions\times CTR}
\]

### 4.3 CPC

\[
\boxed{CPC=\frac{Spend}{Clicks}}
\]

Substituindo CPM e CTR:

\[
\boxed{CPC=\frac{CPM}{1000\,CTR}}
\]

Inversões:

\[
\boxed{CPM=1000\,CPC\,CTR}
\]

\[
\boxed{CTR=\frac{CPM}{1000\,CPC}}
\]

Essas relações são identidades, não previsões. O Google Ads também define CPC médio como custo dividido por cliques e CTR como cliques dividido por impressões.

### 4.4 Session Realization Rate

Plataforma de mídia e analytics nem sempre contam o mesmo evento. Definimos:

\[
\boxed{SRR=\frac{Sessions}{AdClicks}}
\]

Não é necessariamente uma probabilidade; pode exceder 1 por diferenças de escopo/medição.

\[
\boxed{Sessions=AdClicks\times SRR}
\]

Custo por sessão:

\[
\boxed{CPS=\frac{CPC}{SRR}}
\]

---

## 5. Leads e aquisição

Se:

\[
CVR_{S,L}=\frac{Leads}{Sessions}
\]

então:

\[
\boxed{Leads=Sessions\times CVR_{S,L}}
\]

CPL:

\[
\boxed{CPL=\frac{Spend}{Leads}}
\]

Derivações equivalentes:

\[
\boxed{CPL=\frac{CPS}{CVR_{S,L}}}
\]

\[
\boxed{CPL=\frac{CPC}{SRR\,CVR_{S,L}}}
\]

\[
\boxed{CPL=\frac{CPM}{1000\,CTR\,SRR\,CVR_{S,L}}}
\]

Se `CVR_{L,C}=Customers/Leads`:

\[
\boxed{CAC_{media}=\frac{CPL}{CVR_{L,C}}}
\]

Logo:

\[
\boxed{CAC_{media}=\frac{CPM}{1000\,CTR\,SRR\,CVR_{S,L}\,CVR_{L,C}}}
\]

Para múltiplas etapas comerciais, basta continuar multiplicando as taxas.

---

## 6. Lei geral de custos entre etapas

Defina custo por evento:

\[
c_i=\frac{Spend}{N_i}
\]

Como:

\[
N_{i+1}=N_i p_i
\]

então:

\[
\boxed{c_{i+1}=\frac{c_i}{p_i}}
\]

E a inversa:

\[
\boxed{p_i=\frac{c_i}{c_{i+1}}}
\]

Exemplos:

\[
CVR_{S,L}=\frac{CPS}{CPL}
\]

\[
CVR_{L,C}=\frac{CPL}{CAC_{media}}
\]

A relação só é válida se ambos os custos utilizarem **o mesmo Spend e populações aninhadas**.

---

## 7. CAC: escopo obrigatório

### Media CAC

\[
\boxed{CAC_{media}=\frac{MediaSpend}{NewCustomers}}
\]

### Fully Loaded CAC

\[
\boxed{CAC_{full}=\frac{Media+MarketingAcquisition+SalesAcquisition}{NewCustomers}}
\]

Os buckets precisam ser mutuamente exclusivos para evitar dupla contagem.

Produção nunca deve mostrar apenas “CAC” sem informar o escopo.

---

## 8. Mecânica do valor econômico esperado

Se o evento final possui valor econômico esperado `V_n`, uma etapa anterior vale:

\[
\boxed{V_i=p_iV_{i+1}}
\]

Em cadeia:

\[
\boxed{V_i=V_n\prod_{j=i}^{n-1}p_j}
\]

Isso é o espelho da cadeia de custos:

- custo cresce dividindo por conversão;
- valor esperado retrocede multiplicando por conversão.

Assim, em break-even:

\[
\boxed{CostPerEvent_i\le ExpectedEconomicValue_i}
\]

Aplicação: converter CAC máximo em CPL máximo, CPC máximo ou CPM máximo de forma economicamente coerente.

Essa família é `CORE_B`, não `CORE_A`, porque o valor final normalmente é estimado e não observado instantaneamente.

---

## 9. Receita transacional e ecommerce

### Receita básica

\[
\boxed{Revenue=Customers\times AOV}
\]

Em funil:

\[
\boxed{Revenue=Traffic\left(\prod_i p_i\right)AOV}
\]

Em mídia paga:

\[
\boxed{Revenue=\frac{1000\,Spend}{CPM}\,CTR\,SRR\left(\prod_i p_i\right)AOV}
\]

### ROAS

\[
\boxed{ROAS=\frac{Revenue}{Spend}}
\]

Se CAC e AOV usam a mesma população/atribuição:

\[
\boxed{ROAS=\frac{AOV}{CAC_{media}}}
\]

### Revenue per Session

\[
\boxed{RPS=CVR\times AOV}
\]

### AOV

Se `UnitsPerOrder=Units/Orders` e `ASP=Revenue/Units`:

\[
\boxed{AOV=UnitsPerOrder\times ASP}
\]

Logo:

\[
\boxed{Revenue=Sessions\times CVR\times UnitsPerOrder\times ASP}
\]

---

## 10. CRO Solver

Para uma relação multiplicativa:

\[
Y=K\prod_i x_i^{a_i}
\]

entre dois estados:

\[
\boxed{\frac{Y_1}{Y_0}=\prod_i\left(\frac{x_{i,1}}{x_{i,0}}\right)^{a_i}}
\]

### Uma alavanca

Se apenas `x_j` muda e a meta é `g=Y_1/Y_0`:

\[
\boxed{x_j^*=x_{j,0}g^{1/a_j}}
\]

Para taxa com expoente 1:

\[
x_j^*=g\,x_{j,0}
\]

### Várias alavancas iguais

\[
\boxed{m=g^{1/n}}
\]

### Gap residual

\[
\boxed{g_{residual}=\frac{g_{target}}{g_{planned}}}
\]

### Limite de uma probabilidade

Se `p` é uma taxa e só pode chegar a 100%:

\[
\boxed{g_{max}=\frac{1}{p}}
\]

O solver deve sempre rotular o resultado como **cenário ceteris paribus**, não previsão causal.

---

## 11. Decomposição exata de variação

Para:

\[
Y=K\prod_i x_i^{a_i}
\]

logaritmando:

\[
\boxed{\ln\frac{Y_1}{Y_0}=\sum_i a_i\ln\frac{x_{i,1}}{x_{i,0}}}
\]

Isso permite atribuir mecanicamente a variação a cada componente sem somar percentuais de forma incorreta.

Não significa causalidade. Significa apenas decomposição algébrica do resultado.

---

## 12. Marginal e escala

### mCAC observado

\[
\boxed{mCAC=\frac{\Delta Spend}{\Delta Customers}}
\]

### mROAS observado

\[
\boxed{mROAS=\frac{\Delta Revenue}{\Delta Spend}}
\]

Essas grandezas só recebem interpretação de escala se os dois pontos pertencem ao **mesmo regime operacional**. Mudança simultânea de campanha, criativo, oferta, pricing ou CRO torna o slope uma comparação de intervenção, não custo marginal da escala.

### Elasticidade-arco

Para dados semanais/mensais:

\[
\boxed{\varepsilon_{arc}=\frac{\Delta Outcome/\overline{Outcome}}{\Delta Input/\overline{Input}}}
\]

Essa versão substitui o uso incorreto de elasticidade diferencial em intervalos grandes.

No midpoint:

\[
\boxed{mCost=\frac{AverageCost_{mid}}{\varepsilon_{arc}}}
\]

A elasticidade permanece módulo `CONDITIONAL`: descreve o intervalo observado, não garante a mesma resposta futura.

---

## 13. B2B / vendas

### Bookings esperado

\[
\boxed{Bookings=Opportunities\times WinRate\times AverageDealValue}
\]

### Oportunidades necessárias

\[
\boxed{Opportunities^*=\frac{Bookings^*}{WinRate\times AverageDealValue}}
\]

### Pipeline nominal necessário

\[
\boxed{Pipeline^*=\frac{Bookings^*}{WinRate}}
\]

O cálculo precisa ser segmentado quando win rate e ticket variam muito por canal, produto, segmento ou coorte.

### Revenue Throughput Rate

\[
\boxed{Throughput=\frac{Opportunities\times WinRate\times AverageDealValue}{SalesCycle}}
\]

É um índice de velocidade/throughput, **não forecast de receita reconhecida**.

---

## 14. Recorrência: estado da base

Forma universal:

\[
\boxed{Stock_t=Stock_{t-1}+Inflows_t-Outflows_t}
\]

Para clientes ativos com churn `h_t`:

\[
\boxed{A_t=A_{t-1}(1-h_t)+New_t}
\]

Se churn e novos clientes são constantes:

\[
\boxed{A_t=A_0(1-h)^t+N\frac{1-(1-h)^t}{h}}
\]

Para `h=0`:

\[
A_t=A_0+Nt
\]

### MRR

Para base homogênea:

\[
\boxed{MRR_t=A_t\times ARPA_t}
\]

### ARR

\[
\boxed{ARR_t=12\,MRR_t}
\]

ARR aqui significa run-rate anualizado, não receita acumulada das cohorts.

---

## 15. MRR Bridge, GRR e NRR

\[
\boxed{MRR_{end}=MRR_{start}+New+Expansion+Reactivation-Contraction-Churn}
\]

GRR:

\[
\boxed{GRR=\frac{MRR_0-Churn-Contraction}{MRR_0}}
\]

NRR:

\[
\boxed{NRR=\frac{MRR_0+Expansion-Churn-Contraction}{MRR_0}}
\]

O motor falha se inputs implicarem MRR negativo da cohort, em vez de mascarar inconsistência.

---

## 16. LTV simplificado — módulo condicional

Com churn constante por ciclo:

\[
S(k)=(1-h)^k
\]

Ciclos esperados até horizonte `H`:

\[
\boxed{RC_H=\frac{1-(1-h)^H}{h}}
\]

Para churn zero e horizonte finito:

\[
RC_H=H
\]

Horizonte infinito, `0<h\le1`:

\[
\boxed{RC=\frac{1}{h}}
\]

Revenue LTV simplificado:

\[
\boxed{SimpleRevenueLTV=ARPA\times RC}
\]

Contribution LTV simplificado:

\[
\boxed{SimpleContributionLTV=ARPA\times ContributionMargin\times RC}
\]

Essas fórmulas são válidas como aproximação apenas quando churn/ARPA/margem são aproximadamente estacionários e a cohort é razoavelmente homogênea. Para operação com comportamento forte por cohort, usar cohort real.

---

## 17. Payback

Aproximação simples:

\[
\boxed{Payback\approx\frac{CAC}{ARPA\times ContributionMargin}}
\]

Versão ajustada por churn constante:

\[
\boxed{t\ge\frac{\ln\left(1-\frac{CAC\,h}{ARPA\,m}\right)}{\ln(1-h)}}
\]

quando:

\[
CAC<\frac{ARPA\,m}{h}
\]

Se o CAC for maior ou igual ao Contribution LTV simplificado, o payback esperado é infinito dentro do modelo.

---

## 18. Break-even ROAS

Com `m` como contribution margin antes da mídia:

\[
Revenue\,m=Spend
\]

Logo:

\[
\boxed{ROAS_{BE}=\frac{1}{m}}
\]

Se queremos preservar margem pós-mídia `\mu`:

\[
\boxed{ROAS_{min}=\frac{1}{m-\mu}}
\]

condicionado a `\mu<m`.

Contribution ROAS:

\[
\boxed{ContributionROAS=ROAS\times m}
\]

Break-even ocorre em `ContributionROAS=1`.

---

## 19. Agregação correta

Taxas agregadas devem ser reconstruídas a partir de numeradores/denominadores, não pela média simples de taxas.

\[
\boxed{CTR_{total}=\frac{\sum Clicks_i}{\sum Impressions_i}}
\]

\[
\boxed{CVR_{total}=\frac{\sum Conversions_i}{\sum Inputs_i}}
\]

\[
\boxed{CPL_{total}=\frac{\sum Spend_i}{\sum Leads_i}}
\]

Quando a heterogeneidade importa, calcular por segmento e somar o outcome:

\[
\boxed{Revenue_{total}=\sum_i Traffic_i\,CVR_i\,AOV_i}
\]

---

## 20. Consistency Score

Para qualquer identidade com valor observado `Y_o` e reconstruído `Y_d`:

\[
\boxed{Error=\frac{|Y_o-Y_d|}{|Y_o|}}
\]

Tiers operacionais:

- A: erro <1%;
- B: 1–3%;
- C: 3–10%;
- D: ≥10%.

`D` bloqueia uso automático em planejamento reverso até investigação de definição, atribuição ou tracking.

---

## 21. Production tiers

### CORE_A — ≥95
Identidades e diagnósticos que podem ir para produção diretamente:

- mídia básica;
- funil/cadeia de custos;
- receita transacional/ecommerce;
- base ativa/MRR;
- MRR Bridge/retention;
- agregação/consistência;
- break-even ROAS.

### CORE_B — 90–94,99
Uso em produção com premissas visíveis:

- CRO reverse planning;
- B2B reverse funnel;
- expected-value chain;
- marginal scale metrics.

### CONDITIONAL — 80–89,99
Não aparece como “verdade geral” no core:

- elasticidade-arco;
- Simple Constant-Churn LTV;
- Contribution LTV / payback;
- Revenue Throughput Rate.

---

## 22. O que foi removido

A versão 2 não usa como leis gerais:

\[
CPA(x)=a\ln(1+bx)
\]

\[
MRR=c\,tm(1-h)
\]

\[
ARR=c\,tm\,78(1-h)
\]

\[
RC=T(1-h)
\]

nem LTV triangular.

A razão é simples: ou a matemática representava outra grandeza, ou a forma funcional precisava de calibração sofisticada demais para o ganho operacional oferecido ao ICP.

---

## 23. Regra final de parcimônia

Se uma divisão, produto, estoque/fluxo ou diferença marginal resolve a decisão com informação suficiente, não adicionar modelo mais sofisticado.

Complexidade adicional só entra quando demonstra redução material no erro da decisão.
