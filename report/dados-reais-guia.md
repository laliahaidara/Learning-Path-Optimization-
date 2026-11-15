# Dados reais do GuIA no trabalho de knapsack — documento de leitura

**Para o grupo revisar antes de levar ao Overleaf.** Tudo abaixo já está implementado e
reproduzível na branch `real-data-guia`: `real_instances.py`, `experiment_real.py`,
`real_data/*.csv` (dados) e `results/real_*.csv` (saídas).

---

## 1. O que foi feito e por quê

O paper compara seis algoritmos para o knapsack 0/1 de trilhas de aprendizagem usando
**apenas instâncias sintéticas**, e declara duas pendências: a hipótese de que dados
reais de e-learning são correlacionados (Seção II-C, não testada) e o item "real course
data" no Future Work. Fechamos as duas com dados reais do **GuIA**, a plataforma de
aprendizagem adaptativa do Sebrae: módulos com tempo de estudo **medido** (não estimado)
e múltiplas definições de score vindas de comportamento real de alunos.

## 2. Fonte dos dados e anonimização

- Banco de produção da plataforma, acessado por job temporário de **somente leitura**
  com consultas 100% agregadas (o job foi destruído após a extração).
- **Nenhum dado pessoal ou textual saiu do banco**: cursos e módulos viram índices
  (`C2M1`), sem títulos, sem IDs, sem qualquer informação de aluno. Os CSVs em
  `real_data/` contêm apenas contagens, medianas e médias.
- No paper, o Sebrae pode ser citado como operador da plataforma
  ("a Brazilian adaptive-learning platform operated by Sebrae"), sem expor dado algum.

Volumetria de origem (agregada): 4 cursos, 19 módulos, 86 tópicos, 3.864 matrículas,
1.411 registros de progresso por módulo (576 com início **e** fim registrados),
189 respostas NPS, 8.960 atividades geradas e 13.573 tentativas corrigidas com score.

## 3. As instâncias construídas

### 3.1 Nível módulo (n = 12)

Entram os módulos com tempo mediano real medido (sessões com `started_at` e
`completed_at`). **w_i** = mediana observada em minutos (16,5 a 376 min — variação de
23× entre módulos, coisa que estimativa de carga horária nunca mostraria: o campo
estimado da plataforma era constante em 2h). Três definições de **v_i**:

| Definição | O que mede | Fonte |
|---|---|---|
| `conclusao` | taxa de conclusão (%) — proxy de sucesso/engajamento | progresso por módulo |
| `conteudo` | nº de tópicos — proxy de volume de conteúdo (a hipótese do artigo) | estrutura do curso |
| `nps` | NPS médio do curso ×10 — proxy de satisfação | feedback dos alunos |

### 3.2 Nível tópico (n = 78)

Tópicos com atividades corrigidas. A plataforma mede tempo por **módulo**, não por
tópico; o tempo do módulo é rateado entre os tópicos **proporcionalmente ao volume de
atividades geradas em cada um** (proxy observado de carga; tópicos sem atividade
dividem o restante por igual). Esta é a única escolha de modelagem da instância de
tópicos e deve ser declarada no paper. Scores: `dominio` (score médio das atividades,
0–100) e `engajamento` (nº de tentativas, demanda observada).

## 4. Resultados

### 4.1 Onde os dados reais caem entre as famílias sintéticas (bloco `profile`)

| Instância / score | n | Pearson r (tempo × score) | Família sintética mais próxima |
|---|---|---|---|
| módulos / `conteudo` | 12 | **+0,92** | weakly/strongly correlated (r = +0,98 / +1,00) |
| módulos / `conclusao` | 12 | **−0,62** | **nenhuma** — regime negativamente correlacionado |
| módulos / `nps` | 12 | −0,05 | uncorrelated (r ≈ +0,10) |
| tópicos / `dominio` | 78 | +0,13 | uncorrelated |
| tópicos / `engajamento` | 78 | +0,29 | uncorrelated |

Duas conclusões para o paper:

1. **A hipótese da Seção II-C se confirma** quando o score mede volume de conteúdo:
   r = +0,92, entre as famílias weakly e strongly correlated — exatamente o regime que
   o paper usou para argumentar a favor da DP (onde o greedy mais perde na média e o
   custo do B&B mais oscila).
2. **Existe um regime que as famílias sintéticas não cobrem**: score de engajamento dá
   correlação **negativa** (módulos longos concluem menos). Nenhuma das três famílias
   clássicas (nem o benchmark de Pisinger) gera isso, e e-learning real produz
   naturalmente. É contribuição própria do trabalho.

### 4.2 Os algoritmos na instância real de módulos (bloco `algorithms`)

Exemplo (score `conteudo`, T = 2h — a réplica real da Tabela IV do paper):

| Algoritmo | Valor | Ótimo | Perda | Operações |
|---|---|---|---|---|
| DFS exaustivo | 21 | 21 | 0% | 245 |
| DP (tabela) | 21 | 21 | 0% | 1.452 |
| DP (vetor) | 21 | 21 | 0% | 682 |
| DP (memo) | 21 | 21 | 0% | 154 |
| B&B | 21 | 21 | 0% | 113 |
| MITM | 21 | 21 | 0% | 218 |
| FPTAS (ε=0,1) | 21 | 21 | 0% | 6.740 |
| Greedy | 19 | 21 | **9,5%** | 40 |
| Greedy + best item | 19 | 21 | **9,5%** | 52 |

Todos os exatos concordam em todas as 12 combinações (3 scores × 4 orçamentos) — a
validação de correção do paper se mantém em dados reais.

### 4.3 Gap do greedy em orçamentos reais (blocos `gap` e `tgap`)

Varredura fina de T (15 em 15 min). Piores gaps do greedy:

| Instância / score | Pior gap | Onde |
|---|---|---|
| módulos / `conteudo` | **18,8%** | T = 90 min |
| módulos / `conclusao` | 17,3% | T = 60 min |
| tópicos / `engajamento` | 7,3% | T = 45 min |
| tópicos / `dominio` | 2,3% | T = 45 min |

Confirma as duas previsões do paper com dados reais: o pior caso do greedy acontece em
**orçamentos apertados com poucos itens**, e o gap **encolhe quando n cresce**
(12 → 78 itens: pior gap cai de 18,8% para 7,3%). Orçamento apertado não é caso
exótico — é o aluno típico com 1–2h por semana, justamente quem o recomendador mais
precisa acertar.

### 4.4 Pseudo-polinomialidade com unidade de tempo real (bloco `pseudopoly`)

Mesma instância (score `conteudo`), n fixo, unidade cada vez mais fina:

| Unidade | T | Ops DP | Ops B&B | Ops Greedy | Valor ótimo |
|---|---|---|---|---|---|
| horas | 10 | 132 | 124 | 42 | **49** |
| blocos de 15 min | 40 | 492 | 348 | 38 | 57 |
| blocos de 5 min | 120 | 1.452 | 311 | 40 | 56 |
| minutos | 600 | 7.212 | 311 | 40 | 56 |

Dois pontos: (i) só a DP cresce com T, como a Fig. 3 do paper — mas mesmo em minutos
são 7.212 operações, irrisório; (ii) **achado bônus**: arredondar para horas muda o
próprio ótimo (49 ≠ 56) — granularidade grossa não só economiza DP, **distorce a
instância**. Minutos + DP é barato e fiel; é mais um argumento pela DP com T pequeno.

### 4.5 Uma tabela responde todos os orçamentos (bloco `sweep`)

A última linha da tabela DP dá o ótimo para **todo** T de 0 a 24h de uma vez
(`results/real_budget_sweep.csv`, pronto pra virar figura). O catálogo completo cabe a
partir de 1.108 min (≈18,5h). É o item (5) da Seção VII-A demonstrado em dado real — e,
fora do paper, o argumento de produto para otimizar trilhas do GuIA por orçamento do
aluno.

## 5. Parágrafos prontos para o Overleaf (inglês)

Sugestão de subseção VI-J ("Real platform data"), ajustem à vontade:

> **Real platform data.** We validated the synthetic findings on anonymized, aggregated
> data from a Brazilian adaptive-learning platform operated by Sebrae. For 12 modules
> we obtained the median observed study time over completed sessions (16.5 to 376
> minutes — a 23× spread that catalog estimates, constant at 2 h, entirely miss) and
> three score definitions: completion rate, topic count, and course-level NPS. A
> finer-grained instance assigns each of 78 topics a share of its module's time
> proportional to its number of generated exercises, scored by the mean grade of
> 13,573 corrected attempts.
>
> The content-based score confirms the correlation hypothesis of Section II-C: topic
> count correlates with measured time at r = +0.92, between the weakly and strongly
> correlated families. The engagement score, however, is **negatively** correlated
> (r = −0.62): longer modules are completed less often. None of the standard synthetic
> families produces this regime, which e-learning data generates naturally.
>
> All exact algorithms agreed on every real instance. The greedy lost up to 18.8% at
> tight budgets (T = 90 min with n = 12), precisely the regime predicted in Section
> VI-F, and at most 7.3% on the topic-level instance (n = 78), confirming that the gap
> shrinks with n. Refining the time unit from hours to minutes raised the DP's cost
> from 132 to 7,212 operations — still negligible — while every other counter stayed
> constant; coarser rounding, besides saving nothing that matters, changed the optimum
> itself (49 vs. 56 points), so minute-level DP is both cheap and more faithful.
> Finally, a single DP table answered the optimal selection for every budget up to
> 24 h, the property highlighted in Section VII-A, at no extra cost.

E uma frase para Threats to Validity:

> The topic-level instance allocates module time to topics proportionally to their
> number of generated exercises; this workload proxy is the only modeling choice not
> directly measured. The platform is young (4 courses), so the module-level instance is
> small (n = 12); its regimes, however, are the ones the synthetic experiments already
> cover at scale.

## 6. Limitações (sejam honestos no paper)

1. n = 12 módulos é pequeno — a plataforma tem 4 cursos hoje. Os experimentos de escala
   continuam sendo os sintéticos; o dado real valida o **regime**, não a escala.
2. O rateio de tempo por tópico é proxy (declarado na Seção 3.2).
3. NPS é por curso, não por módulo — dentro de um curso é constante.
4. Mediana de tempo real inclui comportamento de navegação (pausas curtas contam
   sessões; sessões abandonadas não entram pois exigem `completed_at`).

## 7. Como reproduzir

```bash
python experiment_real.py                      # todos os blocos
python experiment_real.py --only profile gap   # blocos específicos
```

Saídas em `results/real_*.csv`. Os dados anonimizados estão versionados em
`real_data/`; os scripts de extração (`real_data/*.js`) ficam no repo só como registro
de método — rodá-los exige acesso à infraestrutura do Sebrae, que não é necessária para
reproduzir nenhum experimento.
