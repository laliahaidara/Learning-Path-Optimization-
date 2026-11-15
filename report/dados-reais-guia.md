# Dados reais do GuIA no trabalho de knapsack — documento de leitura

**Para o grupo ler antes de levar ao Overleaf.** Tudo o que está aqui já foi
implementado e roda na branch `real-data-guia`: dados em `real_data/`, código em
`real_instances.py` e `experiment_real.py`, resultados em `results/real_*.csv`.

---

## 0. Leitura rápida — o que o algoritmo decide (e o que ele NÃO decide)

Antes de qualquer número, o essencial:

**O problema do trabalho é de escolha, não de ordem.** O aluno tem X horas pra
estudar e o catálogo tem mais conteúdo do que cabe nesse tempo. O algoritmo responde
uma única pergunta: **quais módulos entram na trilha?** É como fazer uma mala:
decidir o que levar dentro do limite de peso — a ordem em que as peças entram na
mala não importa.

- **A posição/ordem dos módulos NÃO é otimizada.** Em que sequência estudar é outro
  problema (os pré-requisitos: "faça Lógica antes de Python"). O artigo original
  (RUTICO) trata disso com um grafo; nosso trabalho deliberadamente deixou os
  pré-requisitos de fora pra isolar o problema da escolha (a "relaxação" da Seção
  IV-D do paper). Colocar a ordem de volta é o item nº 1 do trabalho futuro.
- Cada módulo tem um **tempo** (quanto custa estudar) e um **score** (quanto vale).
  O algoritmo maximiza a soma dos scores sem estourar o tempo do aluno. Esse é o
  "problema da mochila" (knapsack) do título.
- Os seis algoritmos do paper são seis jeitos de fazer essa mesma escolha — do mais
  burro e garantido (testar todas as combinações) ao mais rápido e arriscado (pegar
  os de melhor custo-benefício até encher). O que comparamos é: quem acha a melhor
  trilha, a que custo, e quem erra quanto.

**O que esta etapa acrescentou:** o paper comparava os algoritmos só com dados
inventados (sintéticos). Nós extraímos números reais do GuIA — quanto tempo os
alunos de verdade levam em cada módulo, quanto concluem, que nota tiram — e rodamos
a mesma comparação neles. Três perguntas guiaram tudo:

1. Dados reais se parecem com qual tipo de dado inventado? (Seção 4.1)
2. O algoritmo rápido-e-arriscado (greedy) erra quanto em dados reais? (Seção 4.3)
3. O algoritmo recomendado pelo paper (DP) continua barato em dados reais? (Seção 4.4)

Respostas curtas: (1) depende de como se define o score — e um dos casos reais não se
parece com **nenhuma** família sintética, o que é um achado; (2) erra até 18,8%,
justamente pro aluno com pouco tempo; (3) continua, e com um bônus a favor dele.

---

## 1. De onde vieram os dados (e a anonimização)

- Banco de produção do GuIA, acessado por um job temporário de **somente leitura**,
  com consultas 100% agregadas (médias e contagens). O job foi apagado após o uso.
- **Nenhum dado pessoal ou texto saiu do banco.** Cursos e módulos viraram índices
  (`C2M1` = curso 2, módulo 1), sem títulos, sem IDs, sem nada de aluno. Os CSVs do
  repo só têm números.
- No paper, citamos o Sebrae como operador da plataforma ("a Brazilian
  adaptive-learning platform operated by Sebrae") sem expor dado algum.

Volume de origem (agregado): 4 cursos, 19 módulos, 86 tópicos, 3.864 matrículas,
1.411 registros de progresso (576 com início e fim marcados — é daí que vem o tempo
real), 189 notas NPS e 13.573 exercícios corrigidos com nota.

## 2. As duas instâncias que montamos

"Instância" = um conjunto concreto de itens (tempo + score de cada um) pra dar de
comida aos algoritmos.

### 2.1 Módulos (12 itens)

Entram os módulos em que dá pra medir o tempo real: a **mediana** do que os alunos
levaram entre começar e concluir. Resultado: de 16,5 min a 376 min — uma variação de
23×. Detalhe que justifica a extração: o campo de carga horária *estimada* da
plataforma era constante (2h pra tudo), ou seja, estimativa não contaria essa
história.

O "score" (valor do módulo) não existe pronto no banco — testamos **três definições**,
porque cada uma conta uma história diferente:

| Score | O que mede | Em palavras |
|---|---|---|
| `conclusao` | % de alunos que concluem o módulo | "módulo que as pessoas terminam" |
| `conteudo` | nº de tópicos do módulo | "módulo com mais conteúdo" |
| `nps` | satisfação média do curso (NPS) | "módulo de curso bem avaliado" |

### 2.2 Tópicos (78 itens)

Visão mais fina: cada tópico vira um item. Como a plataforma só mede tempo por
módulo, repartimos o tempo do módulo entre seus tópicos **proporcionalmente ao volume
de exercícios de cada um** (tópico com mais exercícios consome mais tempo — um proxy
observado, não um chute uniforme). Essa repartição é a única escolha de modelagem
nossa e está declarada nas limitações. Scores: `dominio` (nota média dos exercícios)
e `engajamento` (nº de tentativas — demanda real).

## 3. Resultados — um por um, com a conclusão primeiro

### 3.1 Dados reais se parecem com qual família sintética?

**Conclusão: depende do score — e uma das combinações não se parece com nada que a
literatura testa.**

O paper usa três famílias de dados inventados que vão de "tempo e score não têm nada
a ver" (uncorrelated) até "quanto mais longo o módulo, mais vale" (strongly
correlated). A régua pra comparar é a correlação de **Pearson (r)**: +1 significa
"andam juntos", 0 "sem relação", −1 "andam ao contrário".

| Instância / score | n | r (tempo × score) | Lê-se assim |
|---|---|---|---|
| módulos / `conteudo` | 12 | **+0,92** | módulo mais longo tem mais conteúdo — como o paper apostou |
| módulos / `conclusao` | 12 | **−0,62** | módulo mais longo conclui MENOS — ao contrário de tudo que se testa |
| módulos / `nps` | 12 | −0,05 | sem relação |
| tópicos / `dominio` | 78 | +0,13 | quase sem relação |
| tópicos / `engajamento` | 78 | +0,29 | relação fraca |

Dois pontos pro paper:

1. **A hipótese da Seção II-C se confirmou**: com score de conteúdo, r = +0,92 — os
   dados reais caem entre as famílias weakly e strongly correlated, exatamente o
   regime que o paper usou pra defender a DP.
2. **Achado original**: com score de engajamento a correlação é **negativa**
   (módulos longos espantam conclusão). Nenhuma das famílias clássicas da literatura
   gera esse regime — e e-learning real gera naturalmente.

### 3.2 Os algoritmos concordam em dados reais?

**Conclusão: todos os exatos acham a mesma trilha ótima em todas as combinações; o
greedy erra.** Exemplo com score `conteudo` e aluno com 2h (versão real da Tabela IV
do paper). "Operações" é o custo: quantos passos elementares cada um gastou.

| Algoritmo | Score da trilha | Ótimo | Perdeu | Operações |
|---|---|---|---|---|
| DFS exaustivo | 21 | 21 | 0% | 245 |
| DP (tabela) | 21 | 21 | 0% | 1.452 |
| DP (vetor) | 21 | 21 | 0% | 682 |
| DP (memoizada) | 21 | 21 | 0% | 154 |
| B&B | 21 | 21 | 0% | 113 |
| MITM | 21 | 21 | 0% | 218 |
| FPTAS (ε=0,1) | 21 | 21 | 0% | 6.740 |
| Greedy | 19 | 21 | **9,5%** | 40 |
| Greedy + melhor item | 19 | 21 | **9,5%** | 52 |

Na instância de tópicos (78 itens), DFS e MITM ficam de fora **por projeto**: seriam
2⁷⁹ combinações — é o regime que o próprio paper classifica como inviável. DP, B&B e
heurísticas rodam numa boa.

### 3.3 Quanto o greedy erra, e com quem?

**Conclusão: erra mais justamente pro aluno com pouco tempo — e erra menos quando o
catálogo cresce.** ("Gap" = quanto a trilha do greedy ficou abaixo da ótima, em %.)

| Instância / score | Pior gap | Acontece com |
|---|---|---|
| módulos / `conteudo` | **18,8%** | aluno com 1h30 |
| módulos / `conclusao` | 17,3% | aluno com 1h |
| tópicos / `engajamento` | 7,3% | aluno com 45 min |
| tópicos / `dominio` | 2,3% | aluno com 45 min |

Duas previsões do paper confirmadas em dado real: o pior caso do greedy é **orçamento
apertado** (e aluno com 1–2h/semana é o caso típico, não o exótico), e o gap encolhe
quando n cresce (12 → 78 itens: pior gap cai de 18,8% pra 7,3%).

### 3.4 A conta da DP continua barata com tempo real?

**Conclusão: continua — e descobrimos um motivo extra pra usar minutos.** A DP é o
único algoritmo cujo custo cresce com a precisão do relógio (isso é o
"pseudo-polinomial" do paper: o custo depende do tamanho do número T, não só da
quantidade de itens). Pegamos a mesma instância e fomos refinando a unidade:

| Unidade de tempo | T (orçamento 10h) | Custo DP | Custo B&B | Custo Greedy | Ótimo |
|---|---|---|---|---|---|
| horas | 10 | 132 | 124 | 42 | **49** |
| blocos de 15 min | 40 | 492 | 348 | 38 | 57 |
| blocos de 5 min | 120 | 1.452 | 311 | 40 | 56 |
| minutos | 600 | 7.212 | 311 | 40 | 56 |

- Só a DP encarece (132 → 7.212 operações), como o paper previu — mas 7.212 operações
  é nada (milissegundos).
- **Bônus**: arredondar pra horas **mudou a resposta certa** (ótimo 49 ≠ 56). Unidade
  grossa não só não economiza nada relevante — ela **distorce o problema**. Minutos +
  DP é barato e mais fiel.

### 3.5 Uma rodada da DP responde todos os orçamentos

A tabela que a DP preenche já contém, de graça, a trilha ótima pra **qualquer** tempo
de 0 a 24h (última linha da tabela — Seção VII-A, item 5 do paper). Demonstramos com
os dados reais (`results/real_budget_sweep.csv`, pronto pra virar figura). Fora do
paper, é o argumento de produto: o GuIA poderia responder "sua melhor trilha com 2h,
5h ou 10h por semana" com uma única conta.

## 4. Parágrafos prontos para o Overleaf (inglês)

Sugestão de subseção VI-J ("Real platform data") — ajustem à vontade:

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

## 5. Limitações (pra sermos honestos no paper)

1. **A ordem dos módulos ficou de fora** — o trabalho otimiza a escolha, não a
   sequência. Pré-requisitos são o trabalho futuro nº 1 (vira o
   "precedence-constrained knapsack").
2. n = 12 módulos é pouco — a plataforma tem 4 cursos hoje. O dado real valida o
   **tipo** de instância; a escala continua com os sintéticos.
3. A repartição de tempo por tópico é um proxy (declarada na Seção 2.2).
4. NPS é por curso, não por módulo — dentro de um curso é constante.
5. A mediana de tempo real só usa sessões concluídas (abandonos não têm fim marcado).

## 6. Como reproduzir

```bash
python experiment_real.py                      # todos os blocos
python experiment_real.py --only profile gap   # blocos específicos
```

Saídas em `results/real_*.csv`. Os dados anonimizados estão versionados em
`real_data/`; os scripts de extração (`real_data/*.js`) ficam no repo como registro de
método — rodá-los exige acesso à infraestrutura do Sebrae, que **não** é necessária
pra reproduzir nenhum experimento.
