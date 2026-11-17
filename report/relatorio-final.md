# Otimização de trilhas de aprendizagem como problema da mochila 0/1

**Relatório final — Projeto e Complexidade de Algoritmos (UnB)**
Lalia Sadio, Adriana Souza, Leandro Bergmann, Dalila Rezende
Prof. Marcelo Antonio Marotta — novembro de 2026

---

## 1. Apresentação

Este relatório reúne, em formato de leitura corrida, todo o trabalho desenvolvido no
projeto final da disciplina: o problema estudado, os sete algoritmos implementados e
comparados, a análise teórica, os experimentos com dados sintéticos, a validação com
dados reais de uma plataforma de aprendizagem adaptativa em produção (o GuIA, operado
pelo Sebrae) e o experimento bônus com a metaheurística GRASP, adaptada da arquitetura
MAS-Cloud+. A versão em formato de artigo (IEEE, em inglês), com as provas formais,
acompanha este relatório; aqui o objetivo é que qualquer leitor — inclusive de fora da
disciplina — entenda o que foi feito, por que, e o que se concluiu.

Todo o código é Python 3 puro (sem bibliotecas de algoritmos), organizado em um módulo
por algoritmo, e cada algoritmo devolve um **contador de operações elementares** — uma
medida de custo que não depende da máquina. Os contadores medem operações de natureza diferente em cada algoritmo (uma célula da DP, um nó do DFS ou do B&B), então as comparações diretas entre algoritmos indicam ordem de grandeza, e não custo exato. Todos os experimentos são reprodutíveis
por linha de comando e suas saídas estão versionadas em `results/`.

## 2. O problema: escolher o que estudar quando o tempo não dá pra tudo

Plataformas de ensino têm mais conteúdo do que um aluno consegue estudar. Um aluno
com, digamos, 5 horas por semana precisa decidir **quais módulos cursar**. Cada módulo
custa um tempo e rende um valor (um score — o quanto aquele módulo contribui para o
objetivo do aluno). O problema é: **maximizar a soma dos scores sem estourar o tempo
disponível**.

Dois esclarecimentos que evitam confusão:

- **É um problema de escolha, não de ordem.** Decidimos *quais* módulos entram na
  trilha, como quem decide o que cabe numa mala. Em que sequência estudar
  (pré-requisitos) é outro problema, deliberadamente deixado de fora para isolar o
  núcleo combinatório — essa "relaxação" está declarada no artigo e voltará nos
  trabalhos futuros.
- Esse é exatamente o clássico **problema da mochila 0/1 (knapsack)**: cada item
  (módulo) é levado inteiro ou não é levado. O problema é NP-difícil (a versão de decisão é NP-completa), mas da
  variedade "fraca": admite algoritmo exato cujo custo depende do *valor numérico* do
  orçamento T, não só da quantidade de itens — e essa distinção é o fio condutor de
  todo o trabalho.

O ponto de partida foi o artigo **RUTICO** (Nabizadeh et al., 2017), que recomenda
trilhas sob restrição de tempo enumerando todos os caminhos viáveis de um grafo de
curso com uma busca em profundidade (DFS) e devolvendo o de maior score. Funciona, mas
enumerar tudo custa caro — e a pergunta do projeto é: **dá pra fazer melhor, e qual
técnica de projeto de algoritmos é a mais adequada a esse domínio?**

## 3. Os algoritmos comparados

Sete algoritmos, cobrindo as principais técnicas de projeto:

1. **DFS exaustivo (a técnica dos autores do RUTICO)** — backtracking: percorre a
   árvore de decisão "levo / não levo" módulo a módulo, podando ramos que estouram o
   tempo. Exato por força bruta. Visita entre n+1 e 2^(n+1)−1 nós — o pior caso dobra
   a cada módulo novo.
2. **Programação dinâmica (DP, a proposta do trabalho)** — a observação central do
   projeto: a árvore do DFS tem 2^n folhas, mas muitos ramos levam ao **mesmo estado**
   (mesmos módulos decididos, mesmo tempo restante). A DP é o mesmo percurso com cada
   estado calculado **uma única vez**: uma tabela de n×(T+1) células. Em outras
   palavras, **a DP é o DFS dos autores com memória**, no problema relaxado sem pré-requisitos: conserva a exatidão e descarta a redundância. Três variantes: tabela completa (reconstrói a trilha), vetor (só o
   valor, memória mínima) e memoizada (calcula só os estados alcançáveis).
3. **Greedy por razão score/tempo** — ordena por "custo-benefício" e vai levando o que
   cabe. Rápido (Θ(n log n), com merge sort escrito à mão) e sem nenhuma garantia: um
   módulo curto de razão ótima pode ocupar o espaço da combinação ideal. A variante
   **greedy + melhor item** devolve o melhor entre o greedy e o melhor módulo sozinho,
   o que garante pelo menos metade do ótimo.
4. **Branch and Bound (B&B)** — o DFS com uma poda mais inteligente: descarta um ramo
   quando um limite otimista (o bound fracionário de Dantzig) mostra que ele não pode
   superar a melhor solução já encontrada. Exato; custo varia com os dados.
5. **Meet-in-the-Middle (MITM)** — divide os módulos em duas metades, enumera os
   subconjuntos viáveis de cada uma e combina. Exato, custo O(2^(n/2)): não depende de
   T, mas explode com n.
6. **FPTAS** — aproximação com precisão controlada: reescala os scores e resolve com
   DP sobre o lucro. Garante pelo menos (1−ε) do ótimo em tempo polinomial em n e 1/ε.
7. **GRASP (bônus, adaptado do MAS-Cloud+)** — metaheurística: construção gulosa
   **randomizada** (sorteia entre os melhores candidatos em vez de pegar sempre o
   primeiro) seguida de busca local (adiciona e troca módulos até não melhorar),
   repetida 20 vezes com semente fixa. Sem garantia teórica, mas com média excelente.

### Resumo da análise teórica

Para cada algoritmo o trabalho prova correção e deriva melhor e pior caso (as provas
estão no artigo; aqui vai o mapa):

| Algoritmo | Exato? | Melhor caso | Pior caso | Custo depende de |
|---|---|---|---|---|
| DFS exaustivo | sim | Θ(n) | Θ(2^n) | n e folga do orçamento |
| DP (tabela) | sim | Θ(nT) | Θ(nT) — sempre | n e magnitude de T |
| DP (vetor) | sim (só valor) | Θ(n) | Θ(nT) | n e magnitude de T |
| DP (memoizada) | sim | Θ(n) | O(nT) | estados alcançáveis |
| Greedy | não (perda ilimitada) | Θ(n log n) | Θ(n log n) | n |
| Greedy + melhor item | ≥ ótimo/2 | Θ(n log n) | Θ(n log n) | n |
| Branch and Bound | sim | Θ(n log n) | O(n·2^n) | n e correlação dos dados |
| Meet-in-the-Middle | sim | Θ(n) | Θ(2^(n/2)) | n e folga do orçamento |
| FPTAS | ≥ (1−ε)·ótimo | — | O(n³/ε) | n e 1/ε |
| GRASP (bônus) | não (sem garantia) | Θ(n log n) | pseudo-polinomial* | n, iterações, dados |

\* cada movimento aceito da busca local aumenta o score total, que é limitado pela
soma dos scores — isso prova que a busca termina. O limite pseudo-polinomial vale para scores inteiros; com scores reais a terminação se mantém, mas o limite de pior caso passa a ser exponencial.

O detalhe teórico mais importante: a DP é **pseudo-polinomial** — Θ(nT) parece
polinomial, mas T escrito em binário tem log T bits, então o custo é exponencial *no
tamanho da entrada*. Isso não contradiz a NP-dificuldade; significa que a DP é a escolha adequada
**quando T é pequeno em valor absoluto** — e orçamento de estudo em minutos é
exatamente isso.

## 4. Experimentos com dados sintéticos

**Metodologia.** Instâncias geradas em três famílias, conforme a correlação entre
tempo e score de cada módulo: *uncorrelated* (sem relação), *weakly correlated* (score
≈ tempo ± ruído) e *strongly correlated* (score = tempo + constante — a família
reconhecidamente difícil para B&B e, por hipótese, a plausível em e-learning). Orçamento
T como fração ρ do tempo total. Sementes fixas; conclusões pelos contadores de
operações (idênticos em qualquer máquina).

**Correção.** Cinco casos de borda e 1.200 instâncias aleatórias: todos os algoritmos
exatos devolveram sempre o mesmo valor; toda seleção reportada era viável; as
garantias do greedy+item (≥ ótimo/2) e do FPTAS (≥ 0,9·ótimo com ε=0,1) valeram em
100% dos casos. **Zero falhas.**

**O DFS explode como previsto.** No pior caso visitou exatamente 2^(n+1)−1 nós para
todo n testado (8.388.607 nós em n=22, 1,24 s); no caso médio, ~57% disso, crescendo
1,99× por módulo — médio também é exponencial. Extrapolando: ~5 minutos em n=30,
~4 dias em n=40. Enquanto isso, em n=22 a DP computa 2.310 células: **cerca de 3.600 vezes menos que o pior caso do DFS (e 2.000 vezes menos que o caso médio)**, e a diferença só cresce.

**A DP escala.** Custo exatamente n(T+1) em toda instância (como provado): 600 módulos
com T=3.060 custam 1.836.600 operações — 0,37 s em Python puro. O greedy fica abaixo
de 2 ms em qualquer tamanho.

**Pseudo-polinomialidade na prática.** Mantendo 18 módulos e refinando a unidade de
tempo (T de 100 a 102.400), só a DP cresce (1.818 → 1.843.218 operações); DFS, B&B,
MITM e greedy não mudam: dependem de n e da estrutura da instância, não da magnitude de T.

**Qualidade do greedy.** Gap médio pequeno e decrescente com n (abaixo de 3% para
n≥30), mas pior caso severo com poucos módulos: 25,9% (n=8, ρ=0,3), 54,5% (ρ=0,1) e
99,8% na instância adversarial — dois módulos em que a razão engana completamente.
A variante com melhor item conserta apenas os casos em que um módulo sozinho quase
enche a mochila; o valor dela é a garantia de metade, não a média.

**B&B é sensível aos dados; DP e MITM não.** Com R=1000 e n=40, instâncias fortemente
correlacionadas custam ao B&B, em média, 11 a 15× mais que as não correlacionadas (17.162 contra 1.377 operações em n=40); a pior execução chegou a 44.475 operações contra 2.087, cerca de 21× — em linha com a literatura. DP e MITM custam
idêntico nas duas famílias. O B&B foi o exato mais barato em tudo que medimos (n≤40),
mas é o único cujo custo oscila com os dados e sem garantia polinomial.

**FPTAS não compensa aqui.** Com T pequeno, aproximar custou 7,8× a 78× o preço de
resolver exato com a DP (ε de 0,5 a 0,05) — encontrou o ótimo em todos os casos, mas
pagando caro por uma garantia mais fraca.

**A enumeração do RUTICO.** A DFS sobre o grafo de pré-requisitos completo gera
exatamente 2^(n−1) caminhos (32.768 em n=16): no pior caso, a abordagem do artigo original é exponencial no tamanho do grafo do curso. Grafos de curso reais são mais esparsos, então esse número é um limite superior, e não o caso típico.

## 5. Validação com dados reais (plataforma GuIA / Sebrae)

### 5.1 Extração e anonimização

Dados extraídos do banco de produção da plataforma por consultas **somente de
leitura e 100% agregadas** (job temporário, destruído após o uso). **Nenhum dado
pessoal ou texto saiu do banco**: cursos e módulos viraram índices, e os arquivos
versionados contêm apenas contagens, medianas e médias. Origem (agregada): 4 cursos,
19 módulos, 86 tópicos, 3.864 matrículas, 576 sessões de módulo com início e fim
registrados, 189 notas NPS e 13.573 exercícios corrigidos.

Duas instâncias:

- **Módulos (n=12)** — tempo = mediana real observada por módulo (16,5 a 376 min, uma
  variação de 23× que a carga horária estimada da plataforma, constante em 2h, não
  captura). Três definições de score: taxa de conclusão (`conclusao`), nº de tópicos
  (`conteudo`) e NPS do curso (`nps`). Entram os 12 dos 19 módulos que têm tempo medido; os tempos são arredondados para o minuto inteiro mais próximo (mínimo de 1), porque a DP exige tempos inteiros.
- **Tópicos (n=78)** — tempo do módulo repartido entre os tópicos proporcionalmente ao
  volume de exercícios de cada um (proxy observado; é uma escolha de modelagem declarada, assim como as definições de score). Scores: nota média dos exercícios (`dominio`) e nº de tentativas
  (`engajamento`). Entram os 78 dos 86 tópicos que têm tempo de módulo e nota média registrados, com o mesmo arredondamento.

### 5.2 O que os dados reais mostraram

**Onde o dado real cai entre as famílias sintéticas.** Medimos a correlação de
Pearson entre tempo e score (r = +1 andam juntos, 0 sem relação, −1 contrários):

| Instância / score | n | r | Leitura |
|---|---|---|---|
| módulos / conteúdo | 12 | **+0,92** | confirma a hipótese: módulo longo vale mais |
| módulos / conclusão | 12 | **−0,62** | módulo longo conclui MENOS — regime que nenhuma família sintética cobre |
| módulos / NPS | 12 | −0,05 | sem relação |
| tópicos / domínio | 78 | +0,13 | quase sem relação |
| tópicos / engajamento | 78 | +0,29 | relação fraca |

Dois resultados: (i) a hipótese do artigo — "dados de e-learning são correlacionados"
— **se confirmou** na definição de score por conteúdo, r=+0,92, próximo da família weakly correlated (r=0,98 em uma instância sintética de mesmo n) e abaixo da strongly correlated (r=1,00); (ii) **observação**: o score de conclusão produz correlação *negativa*, um regime que as três famílias sintéticas deste trabalho não cobrem. Com n=12, essa estimativa deve ser lida com cautela.

**Todos os exatos concordam; o greedy erra com orçamento apertado.** Nas 12 combinações (3 scores ×
4 orçamentos), todos os algoritmos exatos acharam a mesma trilha ótima. O greedy
perdeu até **21% com orçamento apertado**: 21,0% com 30 min e 17,3% com 1h (score de conclusão), e 18,8% com 1h30 (score de conteúdo). Com 20h a perda foi zero nos três scores. No nível tópico (n=78) o pior gap
cai para 7,3% — confirmando em dado real a previsão de que o gap encolhe com n.

**Granularidade: custo e fidelidade.** Repetindo o teste de pseudo-polinomialidade com
a instância real (orçamento de 10h): em horas, a DP custa 132 operações; em minutos,
7.212; os demais variam pouco e sem tendência (o B&B fica entre 124 e 348 operações), porque a mudança de unidade altera os tempos arredondados, mas não o tamanho do problema. E 7.212 operações seguem sendo milissegundos.
O bônus do teste: **arredondar os tempos para horas mudou a própria resposta ótima**
(49 pontos em horas contra 56 em minutos, no score de conteúdo). Em horas, a trilha escolhida ocupa só 502 dos 600 minutos reais; em blocos de 15 min, o valor sobe para 57, mas a trilha soma 606 minutos e estoura o orçamento. Unidade grossa não só não economiza nada relevante — distorce o
problema. Minutos + DP é barato e mais fiel.

**Uma rodada, todos os orçamentos.** A última linha da tabela da DP entrega o ótimo
para *qualquer* orçamento de 0 a 24h de uma só vez — demonstrado com os dados reais.
Em produto, é a diferença entre responder "sua melhor trilha com 2h, 5h ou 10h por
semana" com uma única conta ou três.

## 6. Bônus: a metaheurística GRASP (ponte com o MAS-Cloud+)

O MAS-Cloud+ (Mendes et al., 2022 — grupo do Prof. Marotta) provisiona máquinas
virtuais na nuvem com três camadas de raciocínio: regras rápidas, **metaheurística
(GRASP)** e otimização formal. Nosso comparativo cobria todas as técnicas **menos** a
metaheurística — o bônus fecha essa lacuna adaptando o GRASP do MAS-Cloud+ ao domínio
de trilhas, com semente fixa (reprodutível) e contador de operações como os demais.

**Validação:** em 1.800 instâncias aleatórias geradas pelo protocolo de correção (três famílias, 40 sementes, cinco valores de ρ e n ∈ {8, 12, 16}), o GRASP achou o
ótimo em **98,1%** dos casos (gap médio 0,044%, pior 9,4%). Os gaps do greedy na tabela abaixo vêm das 30 instâncias por célula deste experimento (ρ=0,3), com sementes diferentes das da Seção 4; por isso o pior caso em weakly correlated com n=8 aparece aqui como 25,0%, e lá como 25,9%.

**Resultados principais:**

| Cenário | Greedy | GRASP |
|---|---|---|
| weakly corr., n=8 (pior gap) | 25,0% | **0,0%** |
| real, módulos/conclusão (pior gap) | 21,0% | **0,0%** |
| real, módulos/conteúdo (pior gap) | 18,8% | 1,5% |
| instância adversarial | 2 (ótimo: 1000) | **1000** |
| custo relativo ao greedy | 1× | 50× a 260× |

**Comparação com a DP exata:** na instância real de tópicos (n=78), o GRASP
custou **4,5× mais que a DP exata** (211.950 contra 46.878 operações) e ainda assim
perdeu até 3,2%, mais que o próprio greedy nesse score (2,3%). No nível de módulos (n=12), o GRASP custou cerca de metade das operações da DP (3.580 contra 7.212), com gap de 0% a 1,5%. Nos dois níveis, só a DP garante o ótimo. Esse resultado vai na mesma direção do que o MAS-Cloud+ relata no domínio dele, onde a otimização formal
superou a metaheurística em 19,3% de desempenho com 6,5% menos custo. **Nos dois
domínios, quando a instância cabe no método exato, o exato vence; a metaheurística é o
plano B para quando não cabe, e com o T pequeno das trilhas de estudo esse caso não apareceu em nenhuma instância testada.**

## 7. Discussão: qual algoritmo, quando

| Situação | Escolha |
|---|---|
| T inteiro pequeno (minutos de estudo), n até milhares, precisa de garantia | **Programação dinâmica** |
| Resposta instantânea, muitos módulos pequenos, perda de 1–3% aceitável | Greedy + melhor item |
| T gigante (unidade finíssima), n ≲ 40 | Meet-in-the-Middle |
| n grande demais para os exatos, sem garantia exigida | GRASP (bônus) |
| Instâncias fáceis, n moderado, velocidade média importa mais | Branch and Bound |
| n e T gigantes, erro ε tolerável | FPTAS |
| Pré-requisitos (ordem) | enumeração como no RUTICO, ILP ou DP em árvore |

A recomendação do trabalho é a **DP**, por cinco razões que os experimentos — agora
também os reais — sustentam: (1) é exata, e o greedy demonstrou perder até 21% com o aluno de pouco tempo; (2) o parâmetro que a encarece (T) é pequeno neste
domínio, e em minutos a conta é de milissegundos; (3) o custo é **previsível** —
exatamente n(T+1) operações antes de rodar, enquanto o B&B oscilou 11–15× entre
famílias e o GRASP não oferece garantia; (4) o custo da DP não muda com a correlação dos dados, que nas instâncias reais variou de r=−0,62 a r=+0,92, enquanto o B&B se mostrou sensível a ela nos experimentos sintéticos; (5) uma tabela
responde todos os orçamentos de uma vez.

## 8. Conclusão

Modelamos a seleção de módulos sob orçamento de tempo como o problema da mochila 0/1 e
mostramos que, no problema relaxado sem pré-requisitos, a programação dinâmica é a enumeração exaustiva do RUTICO **com
memória**: as 2^n folhas da árvore de decisão colapsam em n(T+1) estados. Provamos a
correção e os limites de custo de todos os algoritmos, validamos tudo com contadores
de operações independentes de máquina, e levamos a comparação a dados reais de uma
plataforma em produção — que confirmaram a hipótese de correlação, mostraram um regime negativamente correlacionado que as famílias sintéticas testadas não cobrem e mostraram o greedy
falhando no perfil de aluno com pouco tempo. O bônus GRASP fechou a última
técnica que faltava e, ao ficar mais caro e menos preciso que a DP na instância de tópicos, chegou em e-learning a uma conclusão alinhada à do MAS-Cloud+ na nuvem: **quando o problema cabe no método
exato, o exato vence.**

**Trabalhos futuros.** Reintroduzir os pré-requisitos (mochila com precedência —
NP-difícil em DAGs gerais, mas com DP viável em árvores); restrições múltiplas (tempo
+ custo computacional de LLM, uma mochila multidimensional — com aplicação direta na
plataforma real: rotear interações do aluno para modelos de linguagem de capacidades e
custos diferentes conforme a necessidade, nos moldes do próprio MAS-Cloud+); e
instâncias maiores em linguagem compilada.

## 9. Reprodução

```bash
python experiment.py              # experimentos sintéticos do artigo
python experiment_real.py         # instâncias reais (módulos e tópicos)
python experiment_grasp.py        # bônus GRASP
```

Saídas em `results/*.csv`. Os dados reais anonimizados estão em `real_data/`;
reproduzir os experimentos **não** exige nenhum acesso à infraestrutura do Sebrae. Os scripts de dados reais e do GRASP estão no branch `real-data-guia` do repositório; o branch `main` contém apenas os experimentos sintéticos.

## Anexo: divisão de atividades

Cada frente teve um responsável, identificado também na docstring de cada arquivo
de código (`Responsável: ...`):

| Integrante | Atividades | Arquivos principais |
|---|---|---|
| **Lalia Sadio** | Estudo do artigo (RUTICO) e implementação de referência: DFS exaustivo e DFS sobre o grafo do curso | `algorithms/dfs.py`, `algorithms/graph_dfs.py` |
| **Adriana Souza** | Programação dinâmica (3 variantes), análise de complexidade e prova do custo n(T+1) | `algorithms/dp.py` |
| **Leandro Bergmann** | Algoritmos de comparação: greedy (com merge sort próprio), branch and bound, meet-in-the-middle, FPTAS e GRASP | `algorithms/greedy.py`, `algorithms/sorting.py`, `algorithms/branch_and_bound.py`, `algorithms/meet_in_the_middle.py`, `algorithms/fptas.py`, `algorithms/grasp.py` |
| **Dalila Rezende** | Instâncias sintéticas e reais (extração agregada e anonimizada do GuIA), rotinas de experimento, métricas de tempo, gráficos e redação do relatório | `instances.py`, `real_instances.py`, `experiment*.py`, `real_data/`, `results/` |

O modelo comum (`algorithms/model.py`) foi definido em conjunto. Todos os membros
revisaram o código e o texto integralmente e respondem por qualquer parte do
trabalho.
