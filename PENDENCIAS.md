# Pendências abertas do projeto

Itens que aguardam decisão e **não** estão cobertos pelas pendências técnicas
da fase 2, registradas na Seção 8 de `resultados_fase2/RELATORIO_EXECUCAO.md`
(brms/Stan, SFA degenerado, segunda etapa do DEA). Cada item aqui traz a data
de abertura, a evidência que o motivou e de quem é a decisão.

---

## 0-bis. Varredura de `resultados_fase2/tabelas/` (27/07/2026) — achados abertos

**Aberta em:** 27/07/2026
**Decisão de:** João, com Priscilla onde indicado
**Situação:** **FECHADA em 29/07/2026 — os quatro achados tratados.** Todos
os números foram relidos das fontes antes de virar texto (regra 7).

### Como cada um foi fechado

**(A) Equação de ineficiência da SFA — INCORPORADA.** A Seção 15 ganhou a
Tabela~`tab:equacaoinef` com os sete coeficientes `Z_` citáveis e três
leituras. O achado que o documento nunca mostrava está agora explícito: **o
Público Municipal sai significativamente menos ineficiente que a Direta**
($-5{,}454$, EP 1,020, $p = 9{,}0\times10^{-8}$), sustentando por dentro do
modelo paramétrico a ordem das redes que a Seção afirmava só pelas médias de
eficiência técnica. Junto entraram o Filantrópico indistinguível da Direta
($p = 0{,}134$, coerente com o empate 0,788 × 0,784 já impresso), o Privado
($+2{,}474$), a complexidade ($-2{,}159$), o Grande Porte ($+2{,}470$), o
Especial ($+7{,}401$) e a ausência de tendência ($p = 0{,}668$).

*Correção ao próprio inventário:* este item listava **quatro** coeficientes
fortemente significativos. São **cinco** — `Z_cplx_z` ($-2{,}159$,
$p = 3{,}2\times10^{-11}$) tinha sido omitido da contagem.

**(B) Monotonicidade do insumo de UTI — REPORTADA.** Entrou na mesma
passagem da Seção 15, como a terceira das "honestidades a registrar":
violação em **94,9%** das observações (97,8% entre as com UTI ativa), contra
99,7% de respeito para leitos e 99,6% para valor. O inventário arredondava
para "95%"; vale o 94,9% do `RELATORIO_EXECUCAO.md`.

**(C) "Todas as amostras" — CORRIGIDA, em duas seções.** A frase agora
decompõe o "regime operacional": produção e intensidade de UTI excluem o
zero nas quatro amostras; a ocupação de internação cruza o zero em duas
(principal $-0{,}041$ a $+0{,}277$; sem pandemia $-0{,}077$ a $+0{,}260$).
A **Seção 16 trazia a mesma afirmação** e não constava deste inventário —
foi corrigida junto, senão a correção da 15 abriria classe 4 contra a 16.

**(D) Cobertura de `tabS_sensibilidade` e `tabR_frente3` — TRATADA, e a
leitura deste item fica REFUTADA.**

> **Formulação refutada, preservada.** Este item dizia que na variante sem
> pandemia o coeficiente sai "com erro padrão 400,0 ($p = 8{,}3\times
> 10^{-7}$), **ou seja, precisamente estimado**", e concluía que "a
> afirmação de que o coeficiente 'perde identificação' vale para a
> principal, não para todas as variantes".
>
> **Não é precisão.** Sob separação a verossimilhança fica praticamente
> plana numa região distante de zero, e o intervalo de Wald calculado ali
> não tem interpretação — um $p$ pequeno sobre um parâmetro degenerado mede
> o formato da aproximação, não o dado. A evidência de que o problema é o
> mesmo nas quatro amostras está na **instabilidade do ponto**: $-772$,
> $-902$, $-1.298$, $-1.971$, com erro-padrão de 400 a 1.896. Um parâmetro
> identificado não varia por fator de 2,6 entre subamostras da mesma base.
> A não-identificação vale para **todas** as variantes, e é isso que o
> texto novo declara, com a faixa impressa e o $p$ pequeno explicado em
> nota de rodapé para que ninguém o releia como precisão.

Nenhuma célula das duas tabelas virou número citável no corpo, o que
continua **coerente** com a decisão travada de não citar o contraste OSS da
SFA. O que mudou é que a razão agora está escrita.

---

*Diagnóstico original de 27/07/2026, preservado:*

Primeira checagem de completude fonte × texto sobre
`resultados_fase2/tabelas/` (22 CSVs) e os relatórios em markdown, pastas
que as auditorias anteriores nunca indexavam. Confirmações positivas:
`gamma` vale 0,954821 e o texto imprime 95,5% (o erro de 94% está de fato
corrigido); o LR da Translog (567,0) e a correlação Spearman DEA×SFA
(0,617 e 0,629, impressos como 0,62 e 0,63) conferem com a fonte. Quatro
achados ficaram abertos.

**(A) Classe 3 — a equação de ineficiência da SFA não aparece no
documento.** `tabS_fronteira_bc95.csv` traz seis coeficientes `Z_d_*` e
o documento não cita nenhum. Quatro são fortemente significativos:
Público Municipal −5,454 (p = 9,0×10⁻⁸), Privado +2,474 (p = 4,2×10⁻¹⁰),
Grande Porte +2,470 (p = 1,3×10⁻¹³) e Especial +7,401 (p = 7,0×10⁻¹⁶).
O único coeficiente dessa equação que o texto menciona é o da OSS, e só
para explicar que perde identificação. O resultado de que o Público
Municipal sai significativamente menos ineficiente na mesma equação nunca
é mostrado, embora o documento discuta a ordem das redes na SFA.

**(B) Classe 3 — violação de monotonicidade do insumo de UTI, não
reportada.** O `RELATORIO_EXECUCAO.md` (linha 117) registra que o insumo
de UTI é "mal comportado no Translog (monotonicidade violada em 95% das
observações no painel de 289)" e que "qualquer leitura fina de UTI em
eficiência pede desenho próprio". O documento não menciona isso em lugar
nenhum, embora use a fronteira Translog para sustentar a ordem das redes
e reporte um coeficiente de intensidade de UTI.

**(C) Classe 2 + 4 — "todas as amostras" contradiz a própria Seção 15.**
A Seção 15 afirma que "o regime operacional mais intenso e a eficiência
produtiva maior das OSS são traços robustos da rede, visíveis em todos os
métodos e em todas as amostras". Por `tabR_frente1_variantes.csv`, a
ocupação tem intervalo que cruza o zero em duas das quatro amostras
(principal: −0,041 a 0,277; sem pandemia: −0,077 a 0,260). A própria
Seção 15 já diz isso duas vezes, mais acima. Produção e intensidade de
UTI são robustas nas quatro; ocupação não. A frase precisa dizer qual
componente do "regime operacional" é robusto, ou trazer o número.

**(D) Classe 5 — `tabS_sensibilidade.csv` e `tabR_frente3_variantes.csv`
não têm nenhuma célula no texto.** Isso é *coerente* com a decisão
travada de não citar a SFA das OSS, e o documento explica a degeneração.
Fica o registro de um detalhe: em `tabR_frente3`, a variante sem pandemia
estima o coeficiente em −1.971,5 com erro padrão 400,0 (p = 8,3×10⁻⁷),
ou seja, precisamente estimado, enquanto a especificação principal tem
erro padrão 905,6 (p = 0,152). A afirmação de que o coeficiente "perde
identificação" vale para a principal, não para todas as variantes. Vale
conferir se a redação atual cobre isso.

---

## 0. As cinco classes de erro e as duas regras de triagem

**Consolidado em:** 27/07/2026

A triagem padrão de consistência do documento deve testar **cinco**
classes. As três primeiras eram conhecidas; a quarta e a quinta foram
descobertas nas auditorias de 26 e 27/07/2026 e nenhuma das anteriores
as capturava.

| # | Classe | O que o teste compara | Como se detecta |
|---|---|---|---|
| 1 | Texto discorda da própria tabela-fonte | valor impresso × CSV | pertinência do token contra o CSV |
| 2 | Texto discorda da figura da mesma página | valor impresso × PNG | leitura do PNG, não só do CSV |
| 3 | Contagens inteiras não verificáveis em CSV | N citado × `COUNT` no painel | contagem própria no painel |
| **4** | **Texto discorda de OUTRA SEÇÃO** | seção × seção | **consistência cruzada** |
| **5** | **Fonte tem mais linhas do que o texto reporta** | nº de linhas × nº de resultados citados | **completude fonte × texto** |

**Classe 4 — texto discorda de outra seção.** Descoberta em 26/07/2026.
Nenhum dos dois lados discorda da sua própria fonte; eles discordam
entre si, em geral porque uma correção foi aplicada num lugar e não
propagada, ou porque duas seções leem colunas diferentes da mesma base.
Casos encontrados: a Seção 10 citava a faixa de variação *within* de
"2% a 35%" quando a Seção 8 já trazia 4,5% a 38,2% (resíduo do commit
`9872eb8`); a Seção 7 e a Seção 16 imprimiam o faturamento dos mesmos
conversores em bases diferentes, com inversão de sinal em Sorocaba.
**Instrumento de defesa:** `analises/NUMEROS_CANONICOS.md`, que lista
todo valor que aparece em mais de uma seção.

**Classe 5 — reporte parcial da tabela-fonte.** Descoberta em
27/07/2026. A tabela-fonte contém mais resultados do que o texto
apresenta, e as linhas omitidas apontam sistematicamente na mesma
direção — em geral a que enfraquece o argumento. Casos encontrados:
`tab_est_sintetico.csv` tinha 6 linhas e o texto reportava 3, sendo as 3
omitidas todas nulas e uma delas do TMP, o achado central;
`tab_est_wild_bootstrap.csv` tinha 2 p-valores e nenhum era impresso,
substituídos pelos adjetivos "aponta na mesma direção" e "resistente".
**Instrumento de defesa:** a coluna "linhas na fonte / linhas citadas"
do `NUMEROS_CANONICOS.md`.

### Regra A — completude fonte × texto

Para toda tabela que produza **resultados** (não descritivos), conferir
o número de linhas contra o número de resultados citados. Reporte
parcial é permitido, mas exige: (i) nota de rodapé remetendo à tabela
completa, e (ii) declaração explícita da direção das linhas não
reportadas. Subconjuntos assim declarados hoje: `tab_est_cs_evento`
(20/8) e `tabB_sensibilidade_mortalidade` (3/1).

### Regra B — nenhum adjetivo de resultado sem número

"Resistente", "robusto", "estável", "confirma", "aponta na mesma
direção", "sobrevive intacto", "sabidamente conservador", "replica com
exatidão" — todos exigem o p-valor, o intervalo ou o coeficiente
impresso **na mesma frase**. Onde o número não couber no corpo, vai em
nota de rodapé; nunca some.

Exceção única: remissão a número já impresso antes, no mesmo trecho de
leitura, com o ponteiro explícito. Não vale para resumos de fim de seção
que enunciam conclusões novas.

A varredura de 27/07/2026 encontrou nove casos e resolveu **todos**. O
último — a Seção 15 dizendo que a Translog é "preferida ao Cobb Douglas
por larga margem" — foi dado como sem solução numa primeira análise,
por engano: a varredura tinha procurado apenas em `analises/tabelas/` e
nos CSVs da fase 2. O número está em
`resultados_fase2/RELATORIO_EXECUCAO.md`, linha 74 (LR de 567,0 com 6
graus de liberdade, p da ordem de 1e−119).

**Lição de método incorporada à triagem:** a busca por número de apoio
deve cobrir também os **relatórios em markdown** da fase 2, não só as
tabelas CSV. Um resultado documentado em prosa continua sendo um
resultado documentado.

**Erro de classe 1 encontrado no mesmo passo.** A mesma frase da Seção
15 afirmava que "94% da variância composta" é atribuída à ineficiência,
enquanto `tabS_fronteira_bc95.csv` traz `gamma = 0,9548` e o
`RELATORIO_EXECUCAO.md` registra "gamma = 0,955 (EP 0,006)" — ou seja,
**95,5%**. Corrigido. Este é o primeiro erro de classe 1 encontrado
depois das Camadas 1 e 2 da triagem automatizada, e ele escapou por um
motivo instrutivo: a triagem indexava `analises/tabelas/`, e este número
vive em `resultados_fase2/tabelas/`. Indexar as tabelas da fase 2 é
pré-requisito para fechar o item 1.

---

## 1. Varredura de consistência texto ↔ figura ↔ tabela-fonte nas 18 seções

**Aberta em:** 26/07/2026
**Decisão de:** João
**Situação:** Camada 1 executada e Camada 2 concluída em 26/07/2026;
Camada 3 e item 3 pendentes

Auditar as 18 seções de `analises/latex/secoes/` conferindo cada número do
texto contra a tabela-fonte em `analises/tabelas/` **e** contra a figura
correspondente em `analises/figuras_*/`.

**Motivação.** Durante a auditoria de `estimacao.md` e
`analise_exploratoria.md` (26/07/2026), descobriu-se que
`sec08_correlacao_variancia.tex` trazia um parágrafo e uma tabela cujos
números contradiziam as duas figuras impressas na mesma página: afirmava 2%
de variação *within* no TMP sob um gráfico estampando 13%, e Spearman de 0,63
no par mais forte contra 0,77 na figura. Corrigido no commit `9872eb8`.

**Por que isso indica risco sistêmico.** A rodada de reconciliação de
julho/2026 (314 → 289 CNES) foi desenhada em torno dos números que já se
*sabia* estarem desatualizados pela exclusão dos hospitais estruturalmente
incomparáveis. Um erro que nunca dependeu da
mudança de painel — como o do sec08 — passaria batido por construção. O sec08
é evidência de que outras seções podem ter escapado pelo mesmo motivo.

**Método sugerido.** Tarefa própria, com piloto e validação, no modelo da
Etapa 6 (piloto pequeno → validação → resto). O que tornou o diagnóstico do
sec08 inequívoco foi **ler a figura PNG**, não apenas o CSV: `fig_ae_10` e
`fig_ae_14` imprimem os valores e concordam com as tabelas-fonte, isolando o
texto como a única parte divergente.

**Resultado das Camadas 1 e 2 (26/07/2026).** A triagem automatizada testou
520 dos 1.209 tokens numéricos das 18 seções e devolveu 32 candidatos (6,2%):
20 falsos positivos e 12 indeterminados. A Camada 2 resolveu os 12 — 5 do
`sec15` (medianas DEA e médias SFA), 2 do `sec07` (trajetória de Sorocaba),
2 do `sec09` (mortalidade agregada do funil) e 3 do `sec16` (constantes de TE
da SFA e variação de Taipas). **Todos benignos; nenhuma correção necessária.**
Nenhuma seção apresentou a assinatura do `sec08`, que na versão defeituosa
acusava 69% de divergência contra 0 a 16% no restante do documento. Isso é
evidência de que o defeito do `sec08` foi isolado **dentro da classe que esta
triagem enxerga** — texto que discorda da própria tabela-fonte.

**Causa raiz dos falsos positivos.** A triagem indexava apenas
`analises/tabelas/`. Os 12 indeterminados e boa parte dos 20 falsos positivos
vinham de estatísticas calculadas direto de `analises/painel_definitivo.csv` e
dos escores por observação em `resultados_fase2/dea/` e `resultados_fase2/sfa/`
— fontes ausentes do índice, que nenhuma tabela agregada poderia reproduzir.
Indexar essas três fontes derrubaria a taxa de falso positivo de 62,5% para
perto de zero, e é pré-requisito comum ao item 3 abaixo.

> **Previsão REFUTADA em 29/07/2026, preservada e atribuída.** A frase acima
> — "derrubaria a taxa de falso positivo de 62,5% para perto de zero" — foi
> escrita neste arquivo em 26/07/2026 e **está errada na interpretação**,
> ainda que acerte o número. O índice foi construído
> (`indexar_fontes_triagem.py`) e os candidatos caem de **13 para zero**.
> Mas a **calibração nula** que o script agora roda mostra o que essa queda
> significa:
>
> | casas decimais | tokens reais que casam | valores SORTEADOS que casam |
> |---|---|---|
> | 0 | 100% | 22,1% |
> | 1 | 100% | **100,0%** |
> | 2 | 100% | 25,8% |
> | 3 | 100% | 65,5% |
> | 4 | 100% | **94,2%** |
>
> Com o índice completo, um número **inventado** de quatro casas decimais no
> intervalo dos escores tem 94% de chance de "pertencer". A queda de
> candidatos não é o documento ficando limpo: é o índice ficando **denso
> demais para discriminar**. Os escores do DEA cobrem [0,1] com 21.723
> valores; depois de indexá-los, pertinência de quatro casas ali não é
> teste. **Zero candidatos não é um documento limpo; é um teste que parou de
> testar.**
>
> **A lição, que é a de R1 v2 outra vez, e agora sobre o nosso próprio
> instrumento:** concordância só é evidência se a checagem tivesse alguma
> chance de discordar. Ninguém tinha perguntado com o que a pertinência
> *não* concordaria. O placebo era barato e estava disponível desde o
> início.
>
> **Consequência para o método.** Pertinência não sustenta a Camada 1
> sozinha. Os quatro erros de 29/07/2026 saíram de **recontagem própria** e
> de **leitura de figura**; **nenhum** saiu de pertinência — e os três de
> resíduo da Etapa 1 eram invisíveis a ela por construção, porque 21,9%,
> 86,1% e 0,54 existiram como valores legítimos na base anterior e
> pertinência não tem noção de tempo. O índice continua útil para
> **localizar a fonte** de um número e para dar crédito por fonte. Não é
> teste de correção.

**Camada 3 — EXECUTADA em 29/07/2026. Quatro erros encontrados, todos
corrigidos, e três deles da mesma origem.**

O inventário dizia 48 PNGs em 8 seções. São **44 PNGs em 7 seções**: o
`sec01` não referencia nenhuma figura. A varredura leu os PNGs e comparou
com o texto da mesma página.

| # | seção | classe | o que o texto dizia | o que a figura e a fonte dizem |
|---|---|---|---|---|
| 1 | `sec02` | 2 | ocupação de UTI com **"21,9% de zeros"** | **21,6% não-aplicáveis** (688 obs) e **0,3% de zeros** (7 obs) entre as 2.491 válidas |
| 2 | `sec06` | 2 | UTI atinge **"86,1% em 2021"** | **100,8%** — a figura imprime 101 |
| 3 | `sec08` | 1 e 2 | as duas ocupações correlacionam **"0,54"** | **0,305** na fonte, **0,30** na figura |
| 4 | `sec05` | 3 | **"33 dos 43"** hospitais da faixa 2 não operam UTI | **34** sem UTI SUS pela mediana; **32** sem nenhuma diária. Nenhuma definição do projeto devolve 33 |

**Os três primeiros são o mesmo erro, e a proveniência foi reproduzida
exatamente.** Os valores 21,9%, 86,1% e 0,54 são os que se obtêm com a
**definição antiga** da ocupação de UTI, em que as 688 observações sem UTI
SUS entravam como **zero estrutural** em vez de não-aplicável:

- 21,9% = **695** zeros sobre 3.179, e 695 = 688 estruturais + 7 verdadeiros;
- 86,1% = mediana de 2021 com os zeros dentro, contra 100,8% sem eles;
- 0,54 é a correlação inflada pelos mesmos zeros, contra 0,305.

Cada um foi recalculado nas duas definições antes de ser corrigido, e o
valor antigo bateu na casa decimal em todos. **Não é coincidência de
arredondamento: é resíduo da Etapa 1.**

**O que isto diz sobre o Bloco A.** O §11 registra que o escopo real da
propagação era `sec02`, `sec04` e `sec08` — medido, não presumido. As três
seções foram tocadas, e ainda assim **duas delas guardavam um número
antigo cada**, e o `sec06`, que não estava na lista, guardava um terceiro.
A medição de escopo estava certa quanto a *quais seções*, e incompleta
quanto a *quais números dentro delas*. O `sec08` é o caso mais instrutivo:
o parágrafo corrigido explica, três linhas abaixo do erro, que aquele par
"foi recalculado sobre o domínio corrigido da ocupação de UTI".

**Por que nenhuma camada anterior os pegaria.** A Camada 1 testa
pertinência do token contra os CSVs de `analises/tabelas/`, e 21,9%, 86,1%
e 0,54 **existiram** como valores legítimos — só que na base anterior.
Pertinência não tem noção de tempo. Só a comparação contra a figura
regerada, que é o que a Camada 3 faz, separa o valor certo do valor
vencido.

**As demais conferências passaram.** Foram lidos e batidos contra o texto:
os seis mapas de composição do `sec04` (20 dos 26 da Direta, 29 dos 33 das
OSS, 32 dos 43 da faixa 2, os zeros de faixa 5 e 6), a escada completa do
`sec05` (R\$ 631 → R\$ 3.780; TMP 3,16 → 6,30; alta complexidade 0 →
22,5%; mortalidade 3,20% → 6,52% com recuo a 5,43%), os zeros por
categoria e por faixa do `sec03` (37,5% e 10,7%; 80,1% e 0,0%), a
mortalidade anual do `sec06` (5,31% → 6,28%) e a ocupação de internação de
2020 (64,5%), e as anotações dos histogramas do `sec02` (massa em zero de
0,9% na mortalidade e 31,3% na alta complexidade, máximo de 875%).

---

## 2. Escopo editorial de `analises/estimacao.md`

**Aberta em:** 26/07/2026
**Decisão de:** João, possivelmente com Priscilla
**Situação:** aguardando decisão; documento **não** foi expandido

`estimacao.md` documenta apenas as seções 1 a 3 de `estimacao.py` (preparo da
base, modelos principais por indicador, estudo de eventos dos 5 conversores).
Ficam sem prosa correspondente: teste de permutação, bootstrap selvagem por
cluster, estimador de Callaway e Sant'Anna, controle sintético, robustez sem
o biênio pandêmico e resíduos quantílicos. Todos existem como `tab_est_*.csv`
e estão cobertos no LaTeX (Seções 13 e 14).

**Por que não foi resolvido junto com a auditoria.** É uma questão de escopo
editorial — o que deve existir em prosa acessível *versus* o que basta estar
em tabela e no LaTeX técnico —, não de reconciliação numérica. Envolve
provavelmente Priscilla, que é leitora da versão em prosa e não do LaTeX.

---

## 3. Contagens inteiras não cobertas pela triagem automatizada

**Aberta em:** 26/07/2026
**Decisão de:** João
**Situação:** **EXECUTADA em 29/07/2026.** Mecanismo próprio construído
(`verificar_contagens_inteiras.py`); **um** achado, corrigido.

### Resultado (29/07/2026)

O script reconta do painel, a cada execução, toda contagem inteira que o
documento afirma — nenhum número é copiado de prosa (regra 7). Ele varre as
20 seções, isola os inteiros que o texto apresenta **como contagem** e testa
cada um contra o conjunto recontado.

**209 afirmações de contagem; 90 casam com uma contagem do painel.** As 119
restantes foram inspecionadas e nenhuma é erro: são contagens do **funil
anterior ao painel** (830 estabelecimentos da base bruta, os 25 excluídos por
incomparabilidade), valores monetários, rótulos de percentil (p90) e
subconjuntos declarados. As contagens de cabeça conferem todas:

| afirmação | seção | recontagem |
|---|---|---|
| 289 CNES, 3.179 observações, 11 anos | sec01 | **confere** |
| 171 Filantrópicos, 56 Municipais, 37 OSS, 27 Direta, 3 Privados | sec04 | **confere** pela regra "alguma vez", que a própria seção declara |
| 26 Direta e 33 OSS | sec04 | **confere** pela regra "categoria dominante", também declarada ali |
| 159 médios, 120 grandes, 10 especiais | sec01 | **confere** (soma 289) |
| 35 de baixo óbito estrutural, 254 demais | sec03 | **confere** (soma 289) |
| 5 conversores | várias | **confere** |
| 67 / 97 / 125 CNES em E1 / E2 / E3 | sec13b | **confere** |

### O achado: a Seção 13b misturava as duas regras de contagem

O projeto usa **duas regras legítimas** e a diferença entre elas é exatamente
o número de conversores, porque um hospital que trocou de gestão pertenceu de
fato às duas categorias:

- **categoria dominante** — cada CNES conta uma vez, onde passou a maior
  parte do período. Soma **289**.
- **alguma vez na categoria** — o conversor conta nas duas. Soma **294**.

A Seção 4 usa as duas e **declara ambas**, com a conta de reconciliação
escrita ("por isso a soma das categorias excede em cinco o total de 289").
A tabela do funil de estratos da Seção 13b usava **células pela segunda
regra e totais pela primeira**, com legenda dizendo "Distribuição dos 289
hospitais" e "cada célula traz hospitais distintos" — de modo que nenhuma
coluna fechava:

| estrato | CNES distintos | conversores | soma das células |
|---|---|---|---|
| E1 | 67 | 0 | 67 |
| E2 | 97 | 1 | **98** |
| E3 | 125 | 4 | **129** |
| TOTAL | 289 | 5 | **294** |

**Nenhum número da tabela está errado, e nenhum foi alterado.** As células
são a contagem certa para o que a estimação faz — `tabSEG_10` reporta
`n_cnes` 125 e `n_cnes_oss` 28 em E3, e as duas estão corretas ao mesmo
tempo, porque 3 dos 125 hospitais aparecem nas duas categorias. O que
faltava era a **declaração da regra**, que a Seção 4 já trazia e a 13b não.
Corrigido na legenda.

**Classe do erro: 4.** Duas seções usando a mesma convenção, uma declarando
e a outra não — e a que não declarava afirmava na legenda algo incompatível
com as próprias células. Nenhuma camada da triagem o pegaria: cada número,
isolado, está certo.

---

*Diagnóstico original de 26/07/2026, preservado:*

A Camada 1 da varredura (item 1) testou 520 dos 1.209 tokens numéricos das 18
seções. Ficaram **sem qualquer verificação** 412 inteiros, 188 anos e 89
códigos CNES — e entre os inteiros estão as afirmações de contagem: 289 CNES,
3.179 observações, os N por categoria (171 Filantrópicos, 56 Municipais, 37
OSS, 27 Direta, 3 Privados), os 25 excluídos por incomparabilidade
estrutural, os 5 conversores.

**Por que escaparam.** A triagem testa pertinência contra os CSVs de
`analises/tabelas/`, e contagens não existem ali como valores: são contagens
de linhas, não células. `sec01_painel` é o caso extremo — 27 tokens, todos
inteiros, zero testados.

**Por que isso importa.** É a **mesma classe de erro que a reconciliação de
julho/2026 combateu** (314 → 289 CNES). A Camada 1 cobre a classe do `sec08`
(texto discorda da própria tabela) e é cega para esta.

**O que a verificação exigiria.** Para cada N citado no texto — CNES
distintos, total de observações, linhas por `modelo_gestao_proxy` —, rodar uma
contagem própria (COUNT/GROUP BY) direto em `analises/painel_definitivo.csv` e
comparar com o valor impresso na seção. Não é pertinência contra CSVs de
tabela, é mecanismo próprio. Começar por `sec01_painel`. Convém executar no
mesmo passo em que `painel_definitivo.csv`, `dea/` e `sfa/` forem indexados
para o item 1, que precisa das mesmas fontes.

---

## 4. Itens bloqueados por ausência de interpretador Python

**Aberta em:** 27/07/2026
**Decisão de:** João
**Situação:** **RESOLVIDA em 27/07/2026**

O bloqueio era de ambiente: `python`, `python3` e `py` resolviam apenas
para os *stubs* da Microsoft Store em `WindowsApps`. Foi criado um venv
com `uv` (`.venv`, CPython 3.12.13) com pandas, numpy, matplotlib,
seaborn, openpyxl, scipy, statsmodels, patsy e pyarrow. Rodar sempre com
`.venv\Scripts\python.exe`, nunca com o `python` do PATH.

Os três itens que dependiam disso foram fechados:

**(a) Figuras dos conversores em valores reais.** Fechado no commit
`08f8648`. As cinco `fig_ae_09_conversor_*_custo_real.png` foram geradas
e a Seção 7 passou a exibi-las, com a variação em valores reais de volta
à prosa (Sorocaba −12,2%, Pérola Byington −28,4%).

**(b) Seções 2 e 9 em valores reais.** Fechado no mesmo commit.
`tab_ae_univariada.csv` e `tab_ae_outliers.csv` passaram a ser calculadas
sobre `custo_real`, e os rótulos "(valores correntes)" saíram. Não há
mais valor monetário em base nominal no documento, exceto na Seção 6,
cujo assunto é a comparação entre as duas bases.

**(c) Item 10 — geografia da seleção.** Aplicado; ver item 5, que segue
aberto por depender de ratificação, não de ambiente.

---

## 5. Classificação geográfica em `selecao_entrevistas.py`

**Aberta em:** 27/07/2026
**Decisão de:** Priscilla e Alberto (não é correção editorial)
**Situação:** **APLICADA em 27/07/2026 — pendente de ratificação**

> **Estado em 27/07/2026.** A reclassificação foi implementada (commit
> `307ef29`) por decisão do João, com três estratos por código IBGE:
> Capital (52 hospitais), Outras regiões metropolitanas (49, reunindo os
> 38 demais municípios da RMSP e os 9 da Baixada Santista) e Interior
> (188). A Baixada Santista sozinha tem 10 hospitais, abaixo do piso de
> 15 fixado para um estrato, e por isso entrou junto com a RMSP.
>
> **Efeito na seleção, que é o que precisa de ratificação:** um único
> swap, no bloco c (desviante negativo Filantrópico). Saiu o CNES 2080354
> (Hospital Santo Antônio, Santos) e entrou o CNES 2078465 (Real
> Sociedade Portuguesa de Beneficência, Campinas). Nenhum outro hospital
> entrou, saiu ou mudou de bloco; os seis blocos mantêm o mesmo tamanho e
> o total segue em 24 hospitais únicos. A Seção 16 e o Apêndice B já
> foram reconciliados.
>
> **O que falta:** Priscilla e Alberto ratificarem essa troca. Se
> preferirem manter o Hospital Santo Antônio, basta reverter o commit
> `307ef29` ou fixar o desempate como puramente descritivo. A figura
> `fig_sel_c_2080354.png` foi deixada no repositório de propósito, para
> servir de referência nessa conversa.

O diagnóstico original, mantido para registro: a Seção 16 rotulava três
hospitais como "interior" incorretamente: Santos
(2 hospitais) é Baixada Santista, e Cotia e Guarulhos são Região
Metropolitana de São Paulo. A origem era `selecao_entrevistas.py:90-91`:

```python
def _capital(municipio: str) -> str:
    return "capital" if municipio == "Sao Paulo" else "interior"
```

**Por que não foi corrigido.** A variável `geografia` **entra no
algoritmo de seleção**, não é apenas descritiva. Em
`selecao_entrevistas.py:310-318`, dentro de `bloco_bc()`, ela é critério
de desempate entre candidatos quase empatados:

```python
falta = ("interior" if geografias.count("capital")
         >= geografias.count("interior") else "capital")
```

Trocar o binário capital/interior por quatro categorias (Capital, RMSP,
Baixada Santista, Interior) quebra essa contagem e **pode selecionar
hospitais diferentes nos blocos b e c**. Há ainda um segundo uso na
linha 421: o pareamento do bloco d penaliza pares de municípios
distintos. Mudar a composição dos blocos de entrevista é decisão da
pesquisadora principal e do responsável pelo banco, não ajuste de
rótulo.

**O que fazer quando for ratificado:** reescrever `_capital()` para
classificar por código IBGE, decidir se o desempate passa a operar sobre
quatro categorias ou continua binário com a nova classificação apenas
descritiva, regerar `tab_selecao_entrevistas.csv` e as figuras de
seleção, e reconciliar a Seção 16 e o Apêndice B.

---

## 6. Data exata e OSS do Hospital Estadual de Presidente Prudente

**Aberta em:** 27/07/2026
**Decisão de:** João (pesquisa documental)
**Situação:** aberta — reduzida em 27/07/2026

O **ano** de conversão deixou de ser lacuna: é **2025**, derivado do
próprio painel (a classificação assistencial do SIH para o CNES 2750511
é Direta em todos os anos até 2024 e OSS em 2025). A Subseção 7.1 agora
registra esse ano e declara explicitamente que ele vem do painel, não de
fonte documental. O que permanece em aberto é a **data exata da assunção
e a OSS contratada**.

A Subseção 7.1 documenta as datas de assunção das cinco conversões. Duas
estão confirmadas e duas são aproximadas:

| CNES | Hospital | OSS | Assunção | Confiança |
|---|---|---|---|---|
| 2081695 | Conjunto Hospitalar de Sorocaba | Seconci-SP | 1º/11/2018 | confirmada |
| 2078287 | CRSM / Pérola Byington | Seconci-SP | set/2022 | confirmada |
| 2082225 | H. Geral de Taipas | IRSSL / Sírio-Libanês | ~set/2024 | **aproximada** |
| 2091755 | H. Geral de Vila Penteado | IRSSL / Sírio-Libanês | ~set/2024 | **aproximada** |
| 2750511 | H. Est. de Presidente Prudente | **não identificada** | ano 2025 (do painel); mês **não identificado** | ano do painel |

As datas aproximadas foram inferidas de reportagem de 08/10/2024 que
noticiava os "primeiros trinta dias de contrato". Para Presidente
Prudente, o ano vem da mudança de classificação do SIH entre 2024 e
2025; o mês e a OSS responsável seguem não identificados.

**Por que importa.** A data de assunção determina quantos meses de cada
ano pertencem a cada regime, e a Subseção 7.1 argumenta que os anos
parciais **atenuam** o contraste medido. Sem o mês de Presidente
Prudente, não se sabe quantos meses de 2025 correram sob cada regime,
de modo que esse argumento continua quantificável para quatro dos cinco
conversores.

**Nota sobre as fontes.** As datas, os nomes das organizações sociais e
as circunstâncias das conversões descritas na Subseção 7.1 vêm de
pesquisa documental em imprensa e material institucional, conduzida pelo
responsável pelo estudo. **Não foram verificadas de forma independente
durante a redação**, e as notas de rodapé da Subseção 7.1 atribuem cada
afirmação à sua fonte. Convém uma checagem antes de qualquer publicação
externa.

---

## 7. Eixo "Densidade" nos histogramas — ajuste de código

**Aberta em:** 27/07/2026
**Decisão de:** João
**Situação:** **FECHADA em 29/07/2026 — o trabalho já estava feito e o
registro é que não acompanhou.** Verificada por reprodução, não por leitura.

### O fechamento (29/07/2026), e a afirmação que ele refuta

> **Formulação refutada, preservada e atribuída.** A instrução de trabalho
> que abriu o Bloco 6, escrita por **João**, dizia: *"regeneração dos eixos
> de densidade — essa segue aberta e é o item 1 do bloco"*, e mandava
> substituir o eixo "por quantidade de observações nas figuras
> remanescentes". **Não há figura remanescente.** Fica atribuída pelo mesmo
> motivo que a formulação larga do item 1.2 e as versões refutadas de R1:
> este registro preserva erro rotulado, e rótulo sem autoria transfere o
> erro para quem o encontrou.

Quatro medições, todas reproduzidas em 29/07/2026 antes de este parágrafo
ser escrito:

| verificação | resultado |
|---|---|
| `density=True` em `analise_exploratoria.py` | **nenhuma ocorrência** |
| `analise_exploratoria.py` reexecutado sobre a árvore limpa | **zero alteração** em PNG ou tabela — o disco já é a saída do código atual |
| eixo Y dos PNGs, aberto e lido | `fig_ae_01_hist_mort_all`, `fig_ae_03_hist_log_custo_real` e `fig_ae_12_mistura_mort_all` imprimem **"Hospitais-ano"** |
| `densidade` como palavra isolada em `analises/latex/` | **nenhuma ocorrência** (as buscas anteriores casavam com *intensidade*) |

**As duas listas abaixo foram resolvidas de modos diferentes, e nenhuma como
o inventário previa.** A Lista 1 foi pela opção 1 — a curva KDE saiu, e o
comentário em `analise_exploratoria.py:293-296` registra o motivo. A Lista 2,
que o inventário dava como **não conversível**, foi convertida pela opção 2:
`_escala_contagem()` (linha 167) multiplica a densidade ajustada por *n* e
pela largura do *bin*, de modo que as curvas Beta e a mistura continuam
sobre um histograma de contagem. Ou seja, as duas opções que o inventário
punha como alternativas excludentes foram ambas usadas, cada uma onde cabia.

**A única ocorrência sobrevivente em todo o projeto** é
`resultados_fase2/fase2_hierarquico.R:87` (`ylab = "Densidade"`), que gera as
`figB01_checagem_preditiva_*`. Elas **não estão no documento** — verificado:
`figB01`, `checagem_preditiva` e `ppcheck` não aparecem em nenhum `.tex`.
Continua não havendo o que migrar, exatamente como este item já dizia.

**Lição de método, que é a do próprio §13.** Este item descrevia com
precisão um defeito que já tinha sido corrigido, e sobreviveu três dias
descrevendo um estado inexistente. Nenhuma camada da triagem o pegaria:
todas comparam texto contra dado, e aqui o texto errado era o do *registro*,
não o do documento. O que o pegou foi rodar o script.

### Revisão de 30/07/2026 — o eixo sai da contagem e vai para percentual

**Decisão de João.** A tabela acima passa a descrever um estado anterior: o
eixo Y dos histogramas **não imprime mais "Hospitais-ano"**, e sim
**"% do total de hospitais-ano"**. O motivo é de leitura e não de
estatística — "400 hospitais-ano" só significa algo para quem carrega o
denominador na cabeça, e o denominador não é o mesmo em todas as figuras
(3.179 no painel, 2.491 na ocupação de UTI, 3.150 no interior da
mortalidade, 2.174 no interior da alta complexidade, 3.178 no TMP). Em
percentual as alturas ficam comparáveis entre figuras e o número se lê
sozinho. A forma das barras é idêntica: a conversão é uma divisão pelo *n*
da amostra.

Alcance, todas as onze figuras regeradas em 30/07/2026: os seis
`fig_ae_01_hist_*`, os dois `fig_ae_03_hist_log_*`,
`fig_ae_02_beta_pct_alta_complex`, `fig_ae_12_mistura_mort_all` e
`fig_ae_12_decomposicao_mort_all`. Em código, `ROT_CONTAGEM` virou
`ROT_PERCENTUAL`, `_escala_contagem()` virou `_escala_percentual()` — que
não precisa mais do *n*, porque ele cancela entre a contagem esperada e o
denominador da conversão — e entrou `_pesos_pct()`, que passa
`weights=100/n` a cada `ax.hist`. `_eixo_pct()` escreve o sinal de % nos
rótulos, para a leitura não depender do rótulo do eixo.

Dois efeitos colaterais tratados, e não só o rótulo:

- em `fig_ae_02_beta_pct_alta_complex` o eixo é log e a curva Beta diverge
  perto de zero (o expoente *a* é 0,33): em percentual ela subiria acima de
  100% do total, número sem sentido de leitura. O eixo foi cortado em 100%
  e a curva sai pelo alto, com o `\comofeito` dizendo que isso é
  propriedade do molde e não leitura dos dados;
- o `\comofeito` da Figura da mistura afirmava "a contagem das 3.179
  observações", e o histograma sempre foi o **interior de (0,1)**, que tem
  **3.150**. O erro é anterior a esta revisão e foi corrigido junto, com o
  número conferido em `tab_ae_mistura_mortalidade.csv`.

Texto ajustado nos dois lados do documento — `sec02_univariada.tex` (três
legendas, três `\comofeito` e um `\comoler`) e
`apendiceA_diagnosticos.tex` (três legendas e três `\comofeito`) —, e as
legendas das ocupações passam a nomear o denominador de cada painel, que é
exatamente o que a escala percentual torna comparável. Regra 7 cumprida: os
onze PNGs foram regerados e três deles abertos e lidos antes deste
parágrafo.

O diagnóstico original segue abaixo, preservado.

---

Uma leitora não-estatística lê o eixo "Densidade" como percentual, e ele
não é. O inventário de 27/07/2026 separou as figuras em duas listas.

### Lista 1 — conversíveis para contagem (8 figuras)

`fig_ae_01_hist_*` (mortalidade, TMP, faturamento, alta complexidade,
ocupação de internação, ocupação de UTI — Seção 2) e
`fig_ae_03_hist_log_*` (faturamento e TMP — hoje no Apêndice A).

**O ajuste não é só trocar o rótulo.** `analise_exploratoria.py:238` usa
`density=True` **porque sobrepõe uma curva KDE** (linhas 241–243). Passar
para contagem exige uma de duas decisões:

1. remover a curva KDE e usar `density=False` com o eixo em
   "hospitais-ano"; ou
2. manter a curva e reescalá-la pela largura do *bin* e pelo N, para que
   ela continue acompanhando um histograma de contagem.

A opção 1 é mais simples e mais legível para o público-alvo; a opção 2
preserva a leitura de forma da distribuição. **Decidir antes de
executar.**

### Lista 2 — não conversíveis (permanecem em densidade)

`fig_ae_12_mistura_mort_all` e `fig_ae_12_decomposicao_mort_all`
(curvas Beta sobrepostas), `fig_ae_02_beta_pct_alta_complex` (idem), os
seis `fig_ae_04_violino_*`, e `figE01_violino_te_categoria` e
`figS01_te_categoria`. São densidade por definição. As três primeiras
migraram para o Apêndice A no item C de 27/07/2026; os violinos ficaram
no corpo, com a legenda explicando que a largura mostra concentração e
não percentual.

As `figB01_checagem_preditiva_*` **não estão no documento** — existem em
`resultados_fase2/figuras/` e nunca foram referenciadas. Não há o que
migrar.

### Erro de classe 2 que motivou a revisão

O commit `073b07e` ("Substitui 'densidade' por quantidade de observações
nos eixos dos histogramas") alterou **apenas a prosa do `.tex`**. O eixo
Y dos PNGs continua escrito "Densidade" — conferido abrindo
`fig_ae_01_hist_mort_all.png`. Ou seja, a correção criou a contradição
texto ↔ figura que pretendia remover, e ela ficou no documento de 25/07
a 27/07/2026. Enquanto o código não for ajustado, o texto e as legendas
passam a dizer "densidade", que é o que a figura de fato mostra.

> *Estado deste parágrafo em 29/07/2026:* **já não descreve o repositório.**
> O código foi ajustado e os PNGs regerados — `fig_ae_01_hist_mort_all.png`
> imprime "Hospitais-ano". A contradição texto ↔ figura que ele registra
> existiu de 25/07 a 27/07/2026 e está desfeita nos dois lados. Preservado
> porque a lição abaixo continua valendo, e porque foi ele que a produziu.

**Lição para a triagem:** correção de eixo de figura exige alterar o
script e regerar o PNG. Alterar só o `.tex` cria erro de classe 2.

---

## 8. Restrições de LaTeX: registro corrigido

**Corrigido em:** 27/07/2026
**Situação:** resolvido; fica como registro para não se repetir

Circulou no projeto uma lista de restrições de compilação que na verdade
pertencia ao cabeçalho do `roteiro_entrevistas.tex`, não ao
`principal.tex`. Três das seis não valiam para o documento principal:

| Restrição | `roteiro` (aposentado) | `principal.tex` |
|---|---|---|
| sem babel português | correta | **falsa** — carrega `[brazilian]{babel}` na linha 12 |
| `\sloppy` + `\emergencystretch=3em` | correta | **falsa** — não existe nenhum dos dois |
| microtype sem expansão/protrusão | correta | **falsa** — microtype não é carregado |
| sem lmodern | correta | correta |
| xcolor antes de hyperref | correta | correta |
| pdfLaTeX / TeX Live 2023 | correta | correta |

**Consequência prática.** A hifenização portuguesa **funciona** no
`principal.tex`; conferido com `\showhyphens`, que devolve
`hos-pi-ta-lar mor-ta-li-dade com-ple-xi-dade fi-lan-tró-pico`. Os
zeros de overfull e underfull no log são resultado real, não supressão
por `\sloppy`. Uma tarefa de repaginação chegou a ser aberta sobre a
premissa errada e foi interrompida.

**Estado da repaginação em 29/07/2026 — atualizado.** A tarefa foi
retomada e concluída: o commit `bbe3a57` traz **19 quebras de página em 11
seções**, levando o documento de 113 a 116 páginas com o compile limpo, e
foi mesclado em `master` pelo merge `dfb0f7e`. `bbe3a57` é hoje **ancestral
de `master`**, verificável por `git merge-base --is-ancestor`. A branch
`repaginacao-jul2026` foi apagada em 29/07/2026 junto com as outras três
residuais (item 12.A.8), com o SHA registrado lá. O documento está hoje em
**132 páginas**, depois da auditoria editorial (§14); ver a nota de
contagem no §12, que reconcilia os números que este arquivo já afirmou.

> *Formulação anterior, de 27/07/2026, preservada e rotulada:* «a branch
> `repaginacao-jul2026` existe, está vazia e atrás de `master`.» Era
> **verdadeira quando escrita** — `bbe3a57` ainda não existia — e ficou
> desatualizada com o merge de 29/07. Não é erro na origem; é registro que
> o tempo passou por cima.
>
> **Por que a correção não é cosmética.** Este arquivo e o
> `RESTRICOES_SEGMENTACAO.md` afirmavam coisas opostas sobre o mesmo
> objeto: a nota de método de 29/07 daquele documento registra `bbe3a57` e
> as 116 páginas, enquanto este continuava declarando a branch vazia.
> É a **classe 4** da triagem do item 0 — texto que discorda de outra
> fonte, sem que nenhum dos dois lados discorde da sua própria evidência —
> e ela é **pior entre documentos de controle do que entre seções**, porque
> são estes dois que arbitram o resto. Uma seção errada engana o leitor; um
> documento de controle errado engana quem for corrigir a seção.

**O problema tipográfico real** é a mancha: `left=1cm, right=1cm` produz
cerca de 100 caracteres por linha a 12pt, contra os 65 a 72
recomendados para leitura contínua. O comentário na linha 13 do
`principal.tex` explica a escolha (margens mínimas para as figuras
ocuparem a página). Reduzir a mancha exige revisar as larguras de
`\subfig` e `\includegraphics` no mesmo passo, senão as figuras encolhem
proporcionalmente.

Registrado também no README, seção "Preâmbulo do `principal.tex`".

---

## 9. Ocupação de internação — natureza do excesso acima de 100%

**Aberta em:** 27/07/2026
**RESOLVIDA em:** 28/07/2026, em mecanismo
**Situação:** **FECHADA quanto à natureza do excesso.** O indicador VOLTA para
dentro da estimação na Etapa 4, em modelo de duas partes. Duas asserções de
apoio permanecem verificáveis e não verificadas (itens 3 e 4 abaixo), mas
nenhuma delas decide a questão.

### Resolução (28/07/2026)

O excesso **não é erro de nenhum dos dois sistemas**. O **CNES** registra
estritamente capacidade instalada e **habilitada**, excluindo por definição
leito extra efetivamente operado. O **SIH** fatura diária e gera AIH primária
para maca e leito de observação quando a permanência ultrapassa 24 horas — a
"regra das 24 horas" —, o que configura leito extra por superlotação.

Ocupação acima de 100% é a **assinatura aritmética da superlotação**: o
numerador conta permanência em leito extra, o denominador a exclui. Os dois
campos estão corretos segundo as próprias definições.

O leito pactuado nos contratos SES-SP com as OSS é sistematicamente maior que
o do CNES e seria melhor denominador de capacidade *operacional* — o que não
torna o CNES errado. Contrato estipula capacidade operacional, CNES registra
capacidade habilitada: conceitos distintos, não medidas discordantes.

**O critério de decisão pré-especificado falhou.** Ele dizia que se o
contratualizado estivesse sistematicamente acima de `leitos_sus`, o
sub-registro ganharia. O contratualizado está acima e a conclusão correta é a
oposta: o critério montava dicotomia falsa entre "cadastro errado" e
"sobrecarga real", quando o cadastro está certo *e por isso* o excesso mede
sobrecarga. Preservado sem correção retroativa, em
`RESTRICOES_SEGMENTACAO.md` (R1).

O diagnóstico abaixo é a **versão v3, preservada**. A evidência de linhagem
que ele levanta continua válida; a conclusão de indeterminação, não.

---

`ocupacao_internacao = 100 × diarias_internacao / (leitos_sus × 365)`,
identidade conferida com aderência exata nos onze anos. **15,5% das
observações do painel definitivo ficam acima de 100%**, o que é impossível
frente à capacidade cadastrada, com incidência fortemente diferencial por
categoria de gestão: OSS 29,3%, Público Municipal 26,0%, Filantrópico 11,3%,
Direta 3,9%, Privado 3,0%. Dentro do estrato E3 o desequilíbrio é maior —
OSS 35,5% contra Direta 2,9%.

**A hipótese de sub-registro de leito não foi refutada: ficou não testada.**
Ela chegou a ser dada por refutada contra a contagem de leitos do arquivo de
classificação Barcelona (`20260303 - Classificação Hospitais.xlsx`), que
concorda com `leitos_sus` (razão 1,00) e sob a qual o excesso sobrevive (OSS
24,4% contra Direta 1,8%). **Mas essa contagem não é fonte independente.** No
Privado, `leitos_sus` é 6,7% de `total_leitos`, e a coluna Barcelona dá razão
1,000 contra `leitos_sus` — uma contagem independente de leito hospitalar
daria ~15. Nas 3.040 observações em que SUS e total divergem, a diferença
absoluta mediana contra `leitos_sus` é de 6 leitos, contra `total_leitos`, 38.
A coluna `UTI` do mesmo arquivo repete a assinatura, e a concordância cresce
monotonicamente de 9,3% em 2015 a 69,6% em 2025 — perfil de retrato do campo
CNES tomado no fim do período.

**Todos os campos de leito disponíveis — `leitos_sus`, `leitos_internacao`,
`total_leitos`, contagem Barcelona — são de linhagem CNES.** A concordância
entre eles não constitui validação externa: um CNES que sub-registra leito
SUS sub-registra em todos ao mesmo tempo. Não se sabe se o excesso é
sobrecarga real ou sub-registro, e estes dados não conseguem distinguir.

**A única evidência que não depende do CNES é o padrão episódico.** 123 dos
289 CNES têm ao menos um ano acima de 100%, mas apenas 3 estão acima nos onze
anos e 57 em apenas um ou dois; a mediana entre os afetados é de 3 anos.
Sub-registro cadastral estável produziria excesso persistente, de modo que o
padrão favorece a leitura de pico de demanda — **sem estabelecê-la**: um
hospital pode sub-registrar leito justamente nos anos em que expande, e o
padrão episódico apareceria igual.

Se o denominador estiver certo, o excesso está no numerador
(`diarias_internacao`) ou é real, no sentido de hospital operando acima da
capacidade nominal cadastrada — leito extra, maca em corredor, leito de
observação contabilizado como diária. Isso é a hipótese alternativa, não a
conclusão.

**Perguntas para o Alberto — situação em 28/07/2026:**

1. **RESPONDIDA (sim).** As diárias do SIH incluem permanência em leito extra
   ou de observação não cadastrado, pela regra das 24 horas.
2. **RESPONDIDA (sim).** O cadastro CNES de leitos SUS exclui leito extra
   operado: registra capacidade habilitada.
3. **ABERTA, como asserção não medida.** O leito contratualizado no portal
   **CGCSS/SES-SP** está acima de `leitos_sus` segundo o Alberto. O portal não
   está no painel, e isto **não** decide entre sobrecarga e sub-registro,
   porque contrato e CNES medem conceitos distintos de capacidade.
4. **ABERTA, como asserção não verificada.** A coluna `Leitos` do arquivo
   Barcelona derivar do `ST_LEITO` é verificável contra o histórico DataSUS.
   A linhagem CNES do arquivo já está estabelecida por evidência própria
   (teste do Privado, coluna `UTI`, deriva 9,3% → 69,6%), independentemente
   desta asserção.

As duas linhas de apoio ficam registradas com estatutos distintos de propósito:
uma se sustenta sozinha, a outra não.

**Ocupação acima de 100% mede sobrecarga assistencial e é citável como
achado**, não como bug — e separa OSS e Público Municipal de Direta e
Filantrópico numa dimensão de pressão que o projeto ainda não explorou.

O indicador entra na Etapa 4 em **modelo de duas partes** (R6): binário de
superlotação e contínua condicional a ≤ 100. Nunca como contínua winsorizada,
que apagaria o sinal. Os modelos de ocupação já rodados na Fase 2 têm três
defeitos independentes e serão refeitos na **Etapa 5** — ver R8.
Detalhamento, testes de linhagem, variantes e o registro das duas versões
anteriores deste diagnóstico ficam em `RESTRICOES_SEGMENTACAO.md`, restrição
R1; evidência em
`analises/tabelas/tabSEG_05b_ocupacao_internacao_acima_100.csv` e
`tabSEG_05c_variantes_ocupacao_internacao.csv`.

**Hipótese derivada, com trava (R5 em `RESTRICOES_SEGMENTACAO.md`):** se o
excesso for sobrecarga real, pressão assistencial vira mecanismo candidato
entre gestão e desfecho — mas é **variável pós-tratamento**, e incluí-la como
covariável em modelos de mortalidade ou TMP bloquearia o canal causal que se
quer medir. Mesmo erro de *bad control* que descartou `pct_alta_complex` como
estrato. Só em análise de mediação formal, com desenho próprio.

---

## 10. O rótulo "Bayesiana hierárquica" da Fase 2 não descreve o que foi estimado

**Aberta em:** 29/07/2026
**Decisão de:** João
**Situação:** **RESOLVIDA em 29/07/2026 — renomeado o projeto inteiro.**
Uma exceção declarada, no fim do item.

### O achado

A Etapa 4 tinha um script chamado `etapa4_bayes_segmentado.R` que não é
bayesiano. Ele foi renomeado para `etapa4_hierarquico_segmentado.R`, e a
tabela `tabSEG_12` junto, no fechamento de 29/07/2026.

Ao levantar o alcance dessa renomeação, descobriu-se que **o mesmo defeito
existe na Fase 2, e lá é maior**. O `RELATORIO_EXECUCAO.md`, seção 3,
documenta com precisão que a Frente 1 desceu a escada brms → rstan → glmmTMB
porque o ambiente não tem toolchain de compilação, e lista as cinco
degradações resultantes: intervalos de Wald no lugar de credibilidade,
checagem por simulação no lugar de `pp_check` de posteriori, AIC no lugar de
LOO, sensibilidade de especificação no lugar de sensibilidade de priors — que
"não existem aqui" —, e encolhimento por *partial pooling* clássico.

**A documentação é impecável. O rótulo é que não acompanhou.** O pacote
continua se intitulando "Bayesiana hierárquica" no título do relatório, no
README de `resultados_fase2/`, e no nome de `fase2_hierarquico.R`, `fase2_hierarquico_boot.R`
e do diretório `bayes/`.

### Por que isto importa mais do que parece

**Não há modelagem bayesiana em lugar nenhum do projeto.** A premissa de que a
Etapa 4 precisava ser renomeada *para não se confundir com a Fase 2 bayesiana*
é falsa: as duas rodam o mesmo estimador, glmmTMB por máxima verossimilhança,
pelo mesmo motivo, com a mesma degradação documentada.

Duas consequências práticas:

1. **Para o texto.** Não se pode escrever no `principal.tex` que a Etapa 4 e a
   Fase 2 são famílias inferenciais distintas, nem que a proximidade dos
   pontos é convergência entre paradigmas. Não há dois paradigmas. Escrever
   isso introduziria erro novo em vez de corrigir o existente.
2. **Para a Seção 15 e o Apêndice.** Qualquer trecho que descreva a Frente 1
   como bayesiana precisa ser conferido contra a seção 3 do
   `RELATORIO_EXECUCAO.md`. Não foi conferido nesta sessão.

### Por que não foi corrigido junto

Renomear a Fase 2 é operação de natureza diferente da da Etapa 4:

- o pacote `resultados_fase2/` foi montado **autocontido para revisão
  externa** e pode já ter circulado sob esses nomes;
- os resultados foram **publicados** sob o rótulo, inclusive no
  `principal.tex`;
- envolve nomes de arquivo, de diretório (`bayes/`), de tabela
  (`tabB_comparacao_cre_hierarquico.csv`) e o título do relatório;
- e há uma pendência já registrada de **migrar para brms/Stan** num ambiente
  com toolchain (Seção 8 do `RELATORIO_EXECUCAO.md`). Se essa migração for
  feita, o rótulo passa a estar certo, e a renomeação teria sido trabalho
  jogado fora.

**As três saídas possíveis**, em ordem de custo crescente:

1. **Manter os nomes e corrigir só a prosa**, deixando explícito em cada
   ocorrência que a estimação é por máxima verossimilhança e que "bayesiano"
   sobreviveu como nome do plano, não do que rodou. Custo baixo, resolve o
   risco de leitura, deixa nomes de arquivo enganosos.
2. **Renomear tudo**, como foi feito na Etapa 4. Custo médio, e refaz o pacote
   de revisão externa.
3. **Executar a migração para brms/Stan** e tornar o rótulo verdadeiro. Custo
   alto, exige Rtools e reestimação, mas é a única que fecha a pendência da
   Seção 8 no mesmo movimento.

### A decisão: opção 2, renomear tudo — João, 29/07/2026

**Não é escolha entre três saídas.** Manter a Etapa 4 renomeada e a Fase 2 não
renomeada produziria **contradição interna entre seções**, que é a classe 4 da
triagem deste projeto (item 0). Trocaríamos um erro por outro da mesma
família. E o argumento do pacote autocontido pesa na direção **contrária** à
que este item supunha: é pior mandar para revisão externa com o rótulo errado
do que refazer os nomes antes de mandar.

**Registro de responsabilidade.** A decisão é de João, que a assume. Priscilla
precisa saber, e entra na comunicação a ela como item — mas **não é dela
ratificar**: é fato estatístico, não escolha metodológica. Intervalo de Wald
de máxima verossimilhança não é intervalo de credibilidade, e isso não depende
de preferência de ninguém.

**O que foi renomeado:**

| antes | depois |
|---|---|
| `fase2_bayes.R` | `fase2_hierarquico.R` |
| `fase2_bayes_boot.R` | `fase2_hierarquico_boot.R` |
| `bayes/` (13 objetos `.rds`) | `hierarquico/` |
| `tabB_comparacao_freq_bayes.csv` | `tabB_comparacao_cre_hierarquico.csv` |
| `figB01_ppcheck_*.png` (6 figuras) | `figB01_checagem_preditiva_*.png` |
| título do `RELATORIO_EXECUCAO.md` | "hierárquica por máxima verossimilhança" |
| `etapa4_bayes_segmentado.R` | `etapa4_hierarquico_segmentado.R` (feito antes) |
| `tabSEG_12_bayes_por_estrato.csv` | `tabSEG_12_hierarquico_por_estrato.csv` (idem) |

**No documento, uma única frase era falsa.** `sec17_conclusao.tex` anunciava
"validação por modelos **bayesianos** hierárquicos". Em todos os outros pontos
o texto já dizia apenas "hierárquico", que está **correto** — o modelo é
hierárquico, só não é bayesiano. A varredura por `posterior`, `credibilidade`
e `priori` no `.tex` devolveu 29 ocorrências e **todas as demais eram falsos
positivos**: "janela posterior", "anos posteriores" e "melhora posterior" são
temporais, "prioritários" casa com `priori`, e "teste de credibilidade" na
Seção 12 é o teste de tendências pré-conversão, no sentido corrente da
palavra.

**Nenhum número mudou.** Nenhum coeficiente, nenhum intervalo, nenhuma
conclusão substantiva. Os `.rds` de modelo são os mesmos arquivos noutro
diretório.

**O motivo de usar hierárquico continua inteiro.** Encolhimento e *pooling*
parcial são propriedades do modelo de efeitos aleatórios, não do paradigma, e
existem em máxima verossimilhança. Nada do que justificava a camada cai.

**A migração para brms/Stan continua pendência legítima** (seção 8 do
`RELATORIO_EXECUCAO.md`) e agora fica honesta: é trabalho futuro, não
descrição do presente.

### A exceção declarada: `preparo_fase2.R`

A linha 2 desse arquivo diz `# Preparo comum da fase 2 (Bayesiana
hierárquica, DEA e SFA).` e **não foi corrigida**, porque `preparo_fase2.R`
está na lista de arquivos que o protocolo de trabalho proíbe editar, ao lado
de `painel_definitivo.csv`, `construir_painel_definitivo.py` e
`analise_sih.py`.

A edição seria de **comentário apenas**, sem efeito sobre execução. Mesmo
assim ela não foi feita: a proteção existe justamente para que ninguém decida
caso a caso que a sua edição é inócua. Fica registrada como a única ocorrência
remanescente do rótulo antigo em código, aguardando dispensa explícita da
regra 4.

---

## 11. Duas fórmulas de decomposição de variância convivendo no projeto

**Aberta em:** 29/07/2026
**Decisão de:** João
**Situação:** aberta — a escolha desta rodada está registrada; a
convivência das duas, não resolvida

Ao propagar a correção do domínio da ocupação de UTI (Bloco A), a parcela de
variação *within* desse indicador foi recalculada por **duas fórmulas
diferentes, que devolveram valores diferentes**:

| fórmula | valor | onde vive |
|---|---|---|
| decomposição de `analise_exploratoria.py` | **66,3%** | pipeline publicado, gera `tab_ae_variancia_within_between.csv` |
| soma de quadrados dentro/total, cálculo próprio | 66,9% | `analises/verificar_alcance_correcao_uti.py` |

**Foi usado o 66,3%,** e o motivo é de método, não de preferência: é a mesma
fórmula que produziu o **38,2%** publicado. Trocar de fórmula no mesmo passo
em que se troca o domínio misturaria dois efeitos, e ninguém saberia depois
qual dos dois moveu o número. A comparação 38,2% → 66,3% isola a correção do
domínio, que é o que se queria medir.

**O que fica pendente** é a convivência em si. Duas fórmulas de decomposição
no mesmo repositório, sem registro de qual é a canônica, é exatamente o
mecanismo pelo qual `ocupacao_uti_valida` acabou morando em duas bases com
domínios diferentes — o defeito que o Bloco A corrigiu. Convém decidir qual é
a definição do projeto e deixar a outra explicitamente rotulada como
diagnóstico auxiliar, ou eliminá-la.

### O prompt do fechamento nomeava a Seção 11 como afetada. A medição refutou.

**Registrado para que ninguém "corrija" a Seção 11 daqui a três meses e
introduza o erro que não existia.**

A instrução de trabalho do Bloco A listava `sec11_resultados_indicadores.tex`
entre as seções a propagar. **Ela não é afetada pelo defeito da Etapa 1**, e o
motivo é verificável em `estimacao.py`:

- A parte positiva do modelo de UTI condiciona em `ocupacao_uti > 0`
  (`estimacao.py:622`). Como as 688 observações sem UTI SUS entravam no painel
  com ocupação **zero**, esse filtro **já as removia todas** — a amostra
  publicada tem 2.484 observações, contra 2.491 do domínio correto.
- A diferença de **7 observações** não é o defeito da Etapa 1: são hospitais
  com UTI habilitada e nenhuma diária no ano, isto é, o **defeito 2 de R8**,
  que é condicionar no desfecho em vez da capacidade. Problema distinto, já
  registrado, e cuja correção pela mudança mínima devolve o valor publicado
  (R10).

Logo: **o +19,3% da Seção 11 nunca esteve contaminado pelos zeros
estruturais.** O que a correção do domínio de fato afeta na estimação é a
**primeira** parte do modelo (`uti_ativa`, `estimacao.py:618`), que conflaciona
"hospital sem UTI" com "hospital com UTI e sem uso" — e essa parte não é
citada na Seção 11.

O escopo real do Bloco A, medido e não presumido, é **sec02, sec04 e sec08**.

---

## 12. Estado ao fim do fechamento de 29/07/2026

**Consolidado em:** 29/07/2026

O fechamento mesclou as Etapas 4 e 5 e a repaginação em `master`, renomeou
o rótulo bayesiano em todo o projeto, propagou a correção do domínio da
ocupação de UTI ao documento e escreveu a seção da reestimação segmentada.
O documento vai de 113 a **127 páginas** no fechamento, e a **129** ao fim do
Bloco 6 (29/07/2026), com compile limpo em três passes nos dois estados.

> *Atualização de 29/07/2026, ao fim da auditoria editorial (§14).* A
> passagem tipográfica e os cortes A1 a A6 devolveram o documento a **127
> páginas**, e a auditoria editorial, que acrescentou o sumário executivo e
> as tarjas, o levou a **132**. Compile limpo em três passes (0/0/0/0) em
> todos esses estados. Esta linha existe porque o §8 e este §12 chegaram a
> afirmar contagens diferentes ao mesmo tempo, que é a classe 4 do §13
> dentro de um único documento de controle.

O que segue aberto está separado em **duas listas**, porque são coisas
diferentes e misturá-las esconde qual delas depende de alguém decidir.

### A. Pendente por DECISÃO HUMANA ou INSUMO EXTERNO — não destravável por trabalho nosso

Nenhum destes é destravado por mais análise. *Rótulo ampliado em 29/07/2026:*
a lista dizia apenas "DECISÃO HUMANA", e os itens 9 e 10 abaixo não são
decisão de ninguém — são dados que não estão em disco. O critério que une a
lista é o correto e é mais largo do que o nome antigo: **nada aqui avança
porque alguém se esforce mais.**

1. **Leitura humana do PDF por João.** Nenhuma auditoria numérica substitui.
   As 138 conferências automáticas testam texto contra fonte; não testam se
   o texto está bem escrito nem se a argumentação se sustenta.

   *Reduzida, não fechada, em 29/07/2026.* A auditoria editorial do §14
   cobriu a camada que faltava: prosa, argumento e coerência entre seções,
   nas cinco frentes, com doze achados corrigidos. **Continua aberta** por
   dois motivos: uma leitura de máquina não substitui julgamento sobre
   ênfase, ordem de exposição e o que interessa a Priscilla e Alberto; e o
   §14 deixou uma decisão explicitamente para o João, a densidade de
   negrito da `sec13b`.
2. **Reclassificação geográfica** (item 5, e a verificação em `0d2f1f8`). A
   composição oficial foi conferida contra as duas leis complementares e o
   código já está correto. O que resta é escolher entre três estratos
   (Baixada junto com a RMSP, respeitando o piso de 15) e quatro (Baixada
   isolada, com 10 hospitais, abaixo do piso). **Aguarda Priscilla e
   Alberto.**
3. **Seção 16 e Apêndice B**, que dependem da decisão anterior. O item 4.4
   do fechamento pedia que a Seção 16 refletisse a seleção regenerada; ela
   **não foi regenerada**, porque isso pressupõe a decisão de estratificação.
   Escrever a seção sobre uma seleção que não existe seria inventar
   resultado.
4. **Comunicação à Priscilla**, com quatro conteúdos: o achado confirmado e
   mais forte (intensidade de UTI, +30,4%, estável em cinco famílias); o
   achado decomposto em dois (ocupação de internação); os erros editoriais
   corrigidos; e a inversão do ordenamento da Etapa 1.
5. **A renomeação da Fase 2 já foi feita** (item 10), mas a **migração para
   `brms`/Stan** continua sendo a única saída que torna o rótulo original
   verdadeiro. É decisão de escopo, não de trabalho pendente.
6. **Qual fórmula de decomposição de variância é a canônica** (item 11).
7. **Forma funcional de `complexidade_pond_mort`** — aguarda Priscilla.
8. **As quatro branches locais residuais — APAGADAS em 29/07/2026**, por
   decisão de João, com os SHAs de topo registrados abaixo.

   *Correção de subcontagem, 29/07/2026.* Este item nomeava **uma** branch
   (`reconciliacao-etapaF-jul2026`) quando **quatro** estavam no mesmo
   estado. A formulação anterior, preservada: *"Branch
   `reconciliacao-etapaF-jul2026`, resíduo já mesclado, deixada para depois
   do fechamento por decisão de João."* Subcontagem numa lista de pendências
   é a mesma classe de defeito que a lista existe para evitar, e por isso a
   correção fica rotulada em vez de sobrescrever.

   As quatro estavam a **zero commits à frente de `master`** — conteúdo já
   mesclado, ponteiro é ruído:

   | branch | SHA de topo | commit |
   |---|---|---|
   | `feat/etapa4-reestimacao-segmentada` | `f60f69b` | R9 — resultados da Etapa 4 |
   | `feat/etapa5-ocupacao-fase2` | `0e93604` | formulação larga do item 1.2 atribuída |
   | `reconciliacao-etapaF-jul2026` | `da333a4` | p-valores do teste de tendências paralelas |
   | `repaginacao-jul2026` | `bbe3a57` | 19 quebras de página, 113 → 116 |

   **A operação é reversível:** `git branch <nome> <sha>` recria qualquer
   uma. E é reversível *em definitivo*, não por uma janela de reflog: as
   quatro pontas são **ancestrais de `master`**, de modo que os objetos
   seguem alcançáveis e nunca serão coletados. Foi por isso que os SHAs
   entraram aqui antes de a operação ser executada, e não depois.

9. **Verificação da coluna `Leitos` do arquivo Barcelona contra o histórico
   `ST_LEITO` do DataSUS.** *Reclassificada da lista B para cá em
   29/07/2026.* Asserção registrada em R1, nunca medida — e **não mensurável
   com o que está em disco**: o histórico do DataSUS não está no
   repositório, e o README registra que as fontes brutas não são versionadas.

   **O motivo pelo qual isto não é trabalho pendente é de método, não de
   logística.** O único arquivo Barcelona presente é o
   `20260303 - Classificação Hospitais.xlsx` — que é *exatamente o objeto sob
   suspeita de linhagem*. Conferi-lo contra si mesmo não é verificação. A
   linhagem CNES do arquivo já está estabelecida por evidência própria (teste
   do Privado, coluna `UTI`, deriva 9,3% → 69,6%); o que falta é uma fonte
   externa, e ela não está aqui. Sem o `ST_LEITO`, qualquer coisa que se
   rodasse produziria concordância por construção — que é precisamente o erro
   de R1 v2, registrado como a lição central deste projeto.
10. **Comparação do leito contratualizado CGCSS/SES-SP com `leitos_sus`.**
    *Reclassificada da lista B para cá em 29/07/2026.* Asserção do Alberto,
    nunca medida. O portal **não está no painel** e não há dado do CGCSS em
    lugar nenhum do repositório — R1 já registrava isso, e a reclassificação
    apenas põe o item na lista coerente com o próprio registro. Depende de
    acesso externo, não de execução.
11. **Refazer a seleção do bloco c só sobre o DEA.** *Aberta em 29/07/2026,
    pela auditoria editorial (§14).* Reproduzido em
    `analises/auditar_selecao_sem_sfa.py`: **dois dos três** hospitais do
    bloco c mudam quando o critério é reexecutado sem a fronteira
    estocástica, cujos valores R11 tornou não citáveis. Na Direta o CNES
    2028840 dá lugar ao 2083094; no Filantrópico o 2078465 dá lugar ao
    2077655. O bloco b **não muda em nenhuma das quatro categorias**, e por
    isso se resolveu por redação.

    **Está aqui, e não na lista B, pelo mesmo motivo do item 5:** trocar
    entrevistado é decisão da pesquisadora principal, não ajuste editorial.
    O documento declara a lista do bloco c como **provisória** em vez de
    substituí-la por conta própria. Se Priscilla e Alberto preferirem manter
    os hospitais atuais, basta declarar o critério antigo como
    exploratório; se preferirem a lista só-DEA, o script já a produz.
12. **Em que defeito o veredito de não-citabilidade da SFA se apoia.**
    *Aberta em 30/07/2026, pela auditoria da §16.* A `sec15` funda a
    proibição em dois defeitos, e **só um deles sobrevive ao teste**: a
    degeneração das OSS é real e irreparável, mas a violação de
    monotonicidade em 94,9% é propriedade do **insumo aninhado**, não da
    forma Translog. Retirado o insumo de UTI, a violação desaparece e nada
    substantivo se move (Spearman 0,986). Como é a monotonicidade que
    estende a proibição das OSS às outras quatro categorias, o **escopo** do
    veredito depende de qual defeito se declara. Detalhado em §16.

### B. Pendente por TRABALHO NÃO FEITO — ninguém precisa decidir nada

Estes só dependem de alguém executá-los. *Lista reduzida de nove para sete em
29/07/2026*, com os dois primeiros itens antigos reclassificados para A9 e
A10: não eram trabalho, eram insumo ausente.

1. **Datas exatas de contrato e OSS responsável** dos cinco conversores
   (item 6). O mês de Presidente Prudente e a OSS contratada seguem não
   identificados.
2. **`estimacao.md` cobre só as seções 1 a 3 de `estimacao.py`** (item 2).
   *Este item tem uma metade em cada lista:* ampliar ou não é decisão
   editorial; ampliar, se decidido, é trabalho.

*Itens retirados em 29/07/2026, todos por execução ou medição:*

- **Eixo "Densidade" dos histogramas** (item 7): o código já estava
  convertido, os PNGs já estavam regerados e o `.tex` já não trazia a
  palavra. Ver §7, com a verificação e a formulação refutada atribuída.
- **Contagens inteiras** (item 3): mecanismo próprio construído e executado
  (`verificar_contagens_inteiras.py`), 209 afirmações de contagem testadas,
  90 casadas contra o painel e as demais inspecionadas. Um achado — a regra
  de contagem não declarada na tabela da Seção 13b —, corrigido. Ver §3.
- **Camada 3 da varredura** (item 1): 44 PNGs em 7 seções, lidos e
  comparados com o texto da mesma página. **Quatro erros, todos
  corrigidos**, e três deles resíduos da Etapa 1 com proveniência
  reproduzida. Ver §1.
- **Os quatro achados de `resultados_fase2/tabelas/`** (item 0-bis): a
  equação de ineficiência da SFA entrou na Seção 15 como tabela própria, a
  violação de monotonicidade foi reportada, o "todas as amostras" foi
  decomposto em duas seções e a leitura de (D) sobre "precisamente
  estimado" ficou refutada e preservada. Ver §0-bis.
- **Indexar as três fontes na triagem**: feito
  (`indexar_fontes_triagem.py`), com as cinco famílias de fonte e os
  relatórios em markdown. **A previsão que motivava o item foi refutada
  pela calibração nula do próprio script** — ver o bloco em §1. O índice
  fica como ferramenta de localização de fonte, não como teste de correção.

---

## 13. As inconsistências deste projeto se concentram num par de arquivos

**Registrado em:** 29/07/2026
**Situação:** achado de método — muda o procedimento de auditoria

Três erros de **classe 4** foram encontrados em 29/07/2026, e os três estão
no mesmo par: **`PENDENCIAS.md` × `RESTRICOES_SEGMENTACAO.md`**. Não é
coincidência de amostra pequena; é consequência de como os dois arquivos são
escritos — cada etapa acrescenta ao registro que tem à mão, e ninguém relê o
outro para conferir se ele ainda diz a mesma coisa.

**Os três casos, e as duas direções:**

| # | onde | direção | estado |
|---|---|---|---|
| 1 | `PENDENCIAS.md` §8 dizia a branch `repaginacao-jul2026` "vazia e atrás de `master`" | pendência **fechada** que constava como **aberta** | corrigido |
| 2 | §12.A.8 nomeava uma branch residual quando eram quatro | **subcontagem** de item | corrigido |
| 3 | lista final do `RESTRICOES_SEGMENTACAO.md` trazia `fig_ae_09` e a conversão monetária como pendentes | pendência **fechada** que constava como **aberta** | corrigido |

**As duas direções importam e são erros diferentes.** Pendência fechada que
consta como aberta faz alguém refazer trabalho pronto — custo em horas.
Pendência aberta que consta como fechada faz alguém **não fazer** trabalho
necessário e declarar o estado bom — custo em credibilidade do registro. A
segunda é a pior, e é a que a auditoria tende a não procurar, porque ninguém
audita o que acredita estar resolvido.

**Por que este par pesa mais do que qualquer seção.** Uma seção errada engana
o leitor do documento. Um documento de controle errado engana **quem for
corrigir a seção** — e os dois arquivos aqui são justamente os que arbitram o
resto: `PENDENCIAS.md` decide o que está aberto e de quem é a decisão,
`RESTRICOES_SEGMENTACAO.md` decide o que pode e o que não pode ser escrito.
Contradição entre eles não é erro de conteúdo, é erro de árbitro.

**Procedimento incorporado, a partir de 29/07/2026:** toda auditoria de
consistência deste projeto confere os **dois documentos de controle um contra
o outro**, nas duas direções, antes de olhar as 18 seções. O teste é barato —
os dois arquivos cabem numa leitura — e nenhuma das camadas 1, 2 ou 3 da
triagem o faz, porque todas elas comparam *texto contra fonte de dados*, e
aqui os dois lados são texto.

**Ampliação do achado, ao fim do Bloco 6 (29/07/2026).** A doença não fica
entre os dois arquivos: ela aparece **dentro de cada um**. No mesmo dia, o
§7 deste arquivo descrevia com precisão um defeito de eixo de figura que já
estava corrigido havia dois dias, e o §1 afirmava uma previsão sobre a
triagem que a calibração nula do próprio instrumento refutou. Nenhum dos
dois é contradição com outro documento: é registro que envelheceu sem que
ninguém o reexecutasse.

O que separa os casos pegos dos casos que teriam passado é sempre o mesmo:
**alguém rodou.** O §7 caiu quando o `analise_exploratoria.py` foi
reexecutado; o §1 caiu quando o índice foi calibrado contra placebo; os três
resíduos da Etapa 1 caíram quando os PNGs foram abertos. Ler o registro
nunca teria derrubado nenhum deles — o registro estava internamente
coerente em todos os casos.

**Regra de leitura, para toda auditoria futura deste projeto:** um item de
pendência que descreve um defeito **não é evidência de que o defeito existe
hoje**. Antes de trabalhar sobre um item, reproduza o defeito. Se ele não
reproduzir, o trabalho é fechar o item, não consertar o que já está
consertado.

---

## 15. Mortalidade ajustada nas figuras, e a descritiva ampliada por estrato (29/07/2026)

**Executadas em:** 29/07/2026
**Situação:** **FECHADAS**, com uma não-ação deliberada registrada abaixo.

### A. A mortalidade ajustada saiu das figuras

O commit `1b42a89` tirou a métrica de todo o **texto** em 29/07/2026. Não
tocou nos **PNGs**, que é exatamente o modo de falha que o §7 deste arquivo
documenta: alterar só o `.tex` cria erro de classe 2.

**Uma única figura tinha a métrica como componente:**
`fig_ae_14_variancia_within.png`, na Seção 8. Trazia **sete barras**, com
"Mortalidade ajustada" em 16%, sob um texto que diz "em **cinco dos seis**
indicadores". Agora traz seis, com os demais valores idênticos (66, 17, 16,
13, 8, 5).

**A correção foi feita na origem.** `analise_sih.py` define a lista de
indicadores e está na lista de protegidos da regra 4: ficou intacto, e o
filtro entrou em `analise_exploratoria.py`, com o motivo no comentário.

**Prova de que nada além da métrica mudou.** As onze tabelas afetadas foram
comparadas contra `HEAD` removendo do lado antigo apenas as linhas e colunas
da ajustada. As onze deram **idêntico**. Mais 12 PNGs órfãos apagados.

**Achado colateral, da mesma classe.** Regerar as figuras mostrou que
`fig_ae_10_correlacao_spearman.png` imprimia **"Complexidade estrutural"** no
eixo, enquanto a legenda da mesma página diz "complexidade Barcelona". O
commit `6d1598c` (A2) renomeou no script e nos `.tex` e **não regerou o
PNG**. Latente desde então; corrigido junto.

### A não-ação deliberada: `estimacao.py`

`estimacao.py` roda a mortalidade ajustada como checagem e produz
`fig_est_04_qq_mort_ajustada_zib.png`, que **não está no documento** desde
`1b42a89`. A remoção foi tentada, medida e **revertida**:

- o gerador aleatório dos resíduos quantílicos é **único e sequencial**
  (`default_rng(20260704)`), de modo que retirar um modelo desloca os
  sorteios de todos os seguintes;
- isso moveu a quarta casa de dois outros modelos e levou o r do QQ da fração
  de alta complexidade de **0,9906 para 0,9905** — e o Apêndice cita "0,991",
  que passaria a ficar sobre a fronteira de arredondamento;
- e reescreveu 34 tabelas e 19 figuras, 22 delas numericamente idênticas.

**Mover um valor publicado para apagar um gráfico que ninguém vê é mau
negócio.** Fica registrada a dependência de ordem no RNG como defeito de
desenho a corrigir num passo próprio, com decisão do João, porque a correção
honesta (um gerador por modelo) muda os três r de QQ que o Apêndice imprime.

### B. Descritiva ampliada por estrato: `descritivas_estratos_ampliada.py`

O `descritivas_segmentadas.py` cobria seis indicadores. O script novo cruza
os três estratos com **as 27 variáveis do painel que admitem leitura
descritiva**, mais nove derivadas, e entra no documento como a
Subseção 14.5. Saídas: `tabSEG_20` a `tabSEG_25` e `figSEG_10` a `figSEG_13`.

**A decisão de método que estrutura o script.** O estrato é fixo por CNES.
Para *descrever* os estratos o hospital-ano serve; para *comparar* não serve,
porque trata onze medidas do mesmo hospital como independentes e infla
qualquer teste por um fator próximo de onze. O script reporta as duas coisas
sem misturá-las: descritiva em hospital-ano, teste e tamanho de efeito em
CNES (*n* igual a 289).

**A salvaguarda contra circularidade.** Sete das 27 variáveis são
**definicionais** — o corte é construído com a mediana de `uti_sus` e a faixa
Barcelona. Um $\eta^2$ de 0,71 na faixa Barcelona não é achado, é a definição
reaparecendo. Ficam hachuradas na figura e marcadas na tabela, e fora de toda
leitura substantiva. Sem essa marca o ranking inteiro seria circular no topo.

**O achado.** O estrato explica de **23% a 43%** da variância entre hospitais
em escala, volume, faturamento e ocupação, e **6%** na mortalidade — onde
sequer ordena (E2 0,059 contra E3 0,058, *p* de 0,391). A escada de
complexidade organiza fortemente a estrutura e quase não organiza o desfecho.
Três padrões menores: a produtividade por leito **satura em E2** (43,8 → 61,9
→ 59,0, *p* de 0,736 entre os dois últimos); a proporção de leitos SUS **não
segue a escada** (80,5% → 63,7% → 81,2%); e a pandemia entrou **pela ponta de
baixo** (9,8% → 8,7% → 5,2% de saídas por COVID), o único ordenamento
invertido do levantamento.

**Erro de classe 5 corrigido no caminho.** A Subseção do gradiente afirmava
que a ocupação de UTI "não tem valor em E1 por construção". Não é isso:
`tabSEG_04` já reportava mediana de 66,2% para **18 CNES e 71 hospitais-ano**
de E1. E1 é definido pela *mediana* de `uti_sus` igual a zero, não por
ausência de UTI em todos os anos, e esses 18 são o piscar cadastral de R7. A
fonte trazia mais do que o texto reportava, e a justificativa dada estava
errada. Corrigido nos três lugares em que aparecia, incluindo um `\comofeito`
escrito nesta mesma sessão, que tinha propagado a imprecisão.

**Segunda vez que a regra 7 pegou a própria auditoria.** A primeira redação
da leitura temporal afirmava que o E2 ultrapassa o E3 nas saídas por leito
"a partir de 2022". A tabela por ano refuta: em 2022 o E3 ainda está à frente
(61,1 contra 59,7). O correto é seis dos onze anos, inclusive os três
últimos. A frase foi escrita a partir da leitura do gráfico e corrigida pela
tabela.

**As seis tabelas entraram no documento (30/07/2026).** A Subseção 14.5
terminava com um parágrafo que apenas *dizia onde as tabelas estavam*, e o
leitor do PDF ficava sem elas. As seis foram **reproduzidas por extenso**, em
onze tabelas LaTeX: o dicionário abre em duas (27 incluídas por família, 8
grupos excluídos com motivo), a descritiva sai nas duas unidades lado a lado,
o teste sai completo com os três contrastes de Holm, a abertura por ano sai em
duas tabelas de três métricas, e o cruzamento com categoria sai em uma, com as
oito células de $n<10$ e a marca R2 impressas. A `figSEG_10`, que o script
gerava desde 29/07 e **nenhuma seção incluía**, entrou com "Como ler" e "Como
foi feito". Medido nos dois PDFs: a Seção 14 passou de **11 para 22 páginas**
(63--73 contra 63--84) e o documento, de **136 para 147**.

**Quatro achados que só apareceram ao reproduzir as fontes**, nenhum deles no
texto anterior: (i) o preço unitário real caiu **26,7%** em E1 e **11,0%** em
E2 nos onze anos, e **não caiu** em E3 (+1,3%) — a erosão da tabela de
pagamento foi proporcionalmente maior no degrau de baixo; (ii) a superlotação
é **traço de hospital em E3 e evento de ano em E2**: em E3, 28,1% dos
hospitais-ano contra 26,4% dos hospitais na maioria dos seus anos (quase
coincidem); em E2, 9,3% contra 2,1% (não coincidem); (iii) **três hospitais de
E3** têm mediana de ocupação acima de 100% nos onze anos, que é por que a
linha da ocupação condicional tem 122 CNES e não 125; (iv) dos **81**
contrastes par a par, **73 rejeitam**, e os 8 que não rejeitam são o mapa de
onde a escada para de funcionar — três deles são a ocupação de UTI inteira, a
única variável das 27 que o teste global não distingue ($p$ de 0,158).

**Regra 7 cumprida na direção inversa, e vale registrar.** Nenhum número novo
foi escrito: todos saíram de `tabSEG_20` a `tabSEG_25` lidas do disco. As duas
afirmações da leitura temporal que já estavam no texto — seis cruzamentos na
mortalidade, E2 acima em seis dos onze anos nas saídas por leito — foram
**reconferidas contra `tabSEG_24` ano a ano** antes de a tabela entrar, e
confirmaram.

---

## 14. Auditoria editorial das cinco frentes (29/07/2026)

**Executada em:** 29/07/2026
**Situação:** **FECHADA** quanto aos doze achados; deixa **uma pendência
nova**, registrada em 12.A.11.

A primeira auditoria do projeto a olhar **prosa, argumento e coerência entre
seções** em vez de número contra fonte. As 138 conferências do Bloco 5, as 209
recontagens do Bloco 6 e os 44 PNGs da Camada 3 não são refeitos aqui: o objeto
é o que nenhuma verificação automática testa.

### O que a auditoria confirmou funcionando

Registrado porque ausência de achado, quando a checagem tinha chance de
discordar, é resultado. A **Regra B** (nenhum adjetivo de resultado sem número)
está sendo cumprida: 25 candidatos varridos, todos falsos positivos exceto um.
Ordenamento sem estatística nomeada: 38 candidatos, dois substantivos. A
`sec07` resolve sozinha a exigência de honestidade sobre os cinco conversores,
com fonte atribuída em nota e a direção do viés declarada. O Bloco C é a melhor
escrita nova do documento: declara o critério antes do resultado e explica por
que a ordem inversa converteria princípio em seleção pelo resultado.

### Os achados, por classe

**Classe 1 (texto contra a própria tabela).** A `sec15` afirmava que a equação
de ineficiência tem "outros seis" termos e "quatro" fortemente significativos.
São **sete** e **cinco**, e a tabela que os mostra está oito linhas abaixo. O
"cinco" já estava corrigido no §0-bis deste arquivo desde o mesmo dia e **nunca
foi propagado ao `.tex`**; o "seis" nunca fora corrigido em lugar nenhum.

**Classe 2 (texto contra a figura da mesma página).** O `\comoler` da figura de
eficiência mandava o leitor ver OSS e Município acima de Direta e Filantrópico
"nos dois painéis". No painel do DEA isso é falso: o Município marca 0,632 e a
Direta 0,634, e a própria Seção admite o empate 35 linhas antes.

**Classe 3 e 5 (omissão com viés direcional).** O nível SFA do Público
Municipal (0,912, contra 0,787 da Direta) não existia em nenhum `.tex`. O
documento citava da SFA só o par que empata e depois usava o coeficiente de
−5,454 como corroboração de uma ordem que ele contraria. Detalhado em R11,
emenda de 29/07/2026.

**Classe 4 (seção contra seção).** Quatro casos:

1. A `sec13b` afirmava que "as cinco conversões foram para o mesmo tipo de
   operador". A `sec07` documenta que a OSS de Presidente Prudente **não foi
   identificada**, e que Taipas e Vila Penteado foram para uma organização
   diferente da de Sorocaba e do Pérola. A `sec07` e a `sec17` fazem a
   afirmação correta e restrita (os **dois** com janela utilizável, ambos
   Seconci-SP); a `sec13b` era a única das três a exagerar, e chegava à
   conclusão certa pela evidência errada.
2. A `sec17` listava "a mortalidade menor no logito, excluindo o zero" entre os
   achados que se mantêm em E3, enquanto a mesma seção diz três vezes que o
   achado de mortalidade não se sustenta e que nada autoriza afirmar que a
   gestão por OSS a reduz. A `sec13b` é cuidadosa no ponto (citável só com o
   controle de complexidade explicitado, diferença bruta não citável); a
   conclusão citava o resultado e largava a qualificação.
3. A `sec17` dava duas magnitudes para a intensidade de uso da UTI, 19,3% e
   30,4%, ambas chamadas do achado mais forte, a 110 linhas uma da outra, sem
   dizer que são estimadores diferentes sobre amostras diferentes. **Os dois
   números estão certos na fonte**; faltava a frase que os reconcilia.
4. A `sec17` chamava a maior eficiência das OSS de "concordante entre DEA e
   SFA", apoiando-se num escore que a `sec15` declara não citável.

**Termo não definido.** A `sec15` imprimia "97,8% entre as que têm UTI ativa"
sem definir o termo. Reproduz sob capacidade instalada (`uti_total > 0` ou
`uti_sus > 0`); sob a leitura natural, ter registrado diária, dá **96,9%**.

**Ponteiro que não resolve.** A `sec13b` mandava conferir "as tabelas de
origem" tarjadas, sem `\ref`, e essas tabelas não estão no documento.

### Os dois achados de forma, mensuráveis

A `sec13b` traía a origem em marcas objetivas, e as duas foram corrigidas:

| marca | medida | estado |
|---|---|---|
| figura sem `\comofeito` | **única seção do documento** com figura (2) e nenhum `\comofeito`; as outras treze têm | dois `\comofeito` escritos |
| travessão `---` | a passagem tipográfica de `b4b888a` removeu o travessão do documento inteiro e **deixou-o só nas duas seções novas** (3 em `sec15`, o do `sec13b` é célula de tabela) | convertidos |

Fica também registrado, **sem correção**, que a densidade de negrito da
`sec13b` é de **17,0 por 100 linhas** (65 em 382), a maior entre as seções
analíticas e 57% acima da `sec14`, que é vizinha e do mesmo gênero. É escolha
de estilo, não erro, e a decisão de aparar ou não é do João.

### O erro estrutural: não havia sumário executivo

O documento ia da capa ao índice e direto à Seção 1, cuja primeira frase
anuncia "esta parte do documento apresenta a Análise Exploratória", que são as
seções 1 a 9 de 18. Em 127 páginas, o leitor só descobria o que o trabalho
conclui na página 94.

Foi escrito um **sumário executivo** (`secoes/sec00_resumo.tex`), deliberadamente
**não numerado** (`\section*` com `\addcontentsline` à mão), para que a
numeração de todas as seções seguintes permaneça a que o projeto usa: a
`sec13b` continua saindo como Seção 14 e nenhuma referência cruzada se move.
Ele não introduz nenhuma afirmação nova: é síntese do que a `sec17` já conclui,
com as cinco limitações em lista, e todos os seus números foram reproduzidos.

O documento vai de 127 a **132 páginas**, com compile limpo em três passes.

### A lição desta auditoria

Os quatro erros de classe 4 e a omissão do 0,912 têm a mesma assinatura, e não
é a das auditorias anteriores. **Nenhum deles é um número errado.** Cada valor
citado confere com a sua fonte; o que não fecha é a relação entre eles, ou
entre o número e a frase que o apresenta. A triagem de pertinência não os vê
por construção, a recontagem de inteiros não os vê, e a leitura de PNG não os
vê. O que os pegou foi **ler o argumento de ponta a ponta perguntando se ele se
sustenta** — e, no caso do bloco c, **rodar o contrafactual** em vez de aceitar
a frase que a própria auditoria tinha rascunhado.

Esse último ponto merece registro próprio, porque é a lição de R1 v2 outra vez:
a primeira redação da correção do `sec16` afirmava que a lista de entrevistados
não mudava sem a SFA. **A afirmação foi escrita antes de ser testada, e o teste
a refutou** em dois dos três hospitais do bloco c. Ela não chegou ao documento
porque a regra 7 exigiu rodar. Sem a regra, teria entrado como fato.

**Candidato não corrigido, deixado para conferência humana.** A mesma lista
final do `RESTRICOES_SEGMENTACAO.md` traz *"Propagação da correção da ocupação
de UTI (Etapa 1) para as seções já escritas do `principal.tex` — depende de
leitura da Priscilla"*. O Bloco A **aplicou** essa propagação (commits
`7e3ee35` e `834cade`, escopo real sec02, sec04 e sec08, medido em §11), e o
§12 registra o fechamento. Mas a leitura da Priscilla, que a linha também
menciona, **continua pendente** — de modo que a linha está meio certa e meio
desatualizada, e desfazer o nó exige decidir o que ela quis dizer. Fica aqui
nomeado em vez de corrigido por conta própria.

---

## 17. A SFA sai da análise (31/07/2026)

**Decisão de:** João, 31/07/2026
**Regra que ele deu:** *"se o SFA for bom e correto podemos usá-lo, caso
contrário podemos usar apenas o DEA."*

**O veredito sob essa regra: só DEA.** Dos três defeitos que a §16 examinou,
**um sobrevive** — a degeneração das OSS, constante até a 5ª casa em todas as
especificações testadas (principal, sem UTI, Mundlak, só leitos). E ele cai
**exatamente sobre a categoria que a pesquisa existe para comparar**. Uma
fronteira cujos escores travam nas OSS não serve como medida, por mais
correta que seja no resto.

### O que saiu do documento

- **`sec15`**: o painel (b) dos violinos, a tabela da equação de ineficiência
  (`tab:equacaoinef`), a figura de dispersão SFA×DEA (`fig:convergencia`) e
  toda a passagem técnica da contraparte paramétrica. Nenhuma das três
  âncoras era referenciada em lugar nenhum — a remoção não quebrou
  referência.
- **`sec16` e `apendiceB`**: a coluna SFA das seis tabelas de seleção (18
  linhas), os escores citados nas fichas e as ressalvas que os
  acompanhavam.
- **`sec17`, `sec00`**: as passagens de conclusão e a limitação do sumário.
- **`NUMEROS_CANONICOS.md`**: as duas linhas de valores da SFA.

### O que entrou no lugar

Uma subseção nova em `sec15`, **"O segundo método que foi tentado, e por que
ele ficou de fora"** (`\label{sub:sfa}`), escrita **sem estatística** e
dirigida a administradores hospitalares: explica a diferença entre os dois
métodos, e os dois defeitos por analogia — a nota igual para todos os
hospitais de um grupo, que é o modelo travando; e o leito de UTI contado
duas vezes, "como perguntar quanto custa um carro e depois, na mesma conta,
quanto custa o motor dele". Todas as demais seções remetem a ela.

### A consequência que muda o campo, e não é editorial

O **Bloco e do Apêndice B** — cinco hospitais sugeridos para entrevista —
era selecionado **inteiramente pela divergência entre DEA e SFA**. Sem a SFA
o critério não existe: não é uma coluna que sai, é o bloco que deixa de ter
razão de ser. Foi removido, junto com o **Módulo E** do roteiro na `sec16`.
A reserva sugerida cai de dez para seis hospitais.

**Isto é decisão de campo, não de redação.** Fica registrado aqui em
destaque para que Priscilla e Alberto saibam que a lista encolheu e por quê.
A remoção é reversível: os cinco hospitais e as suas fichas estão no
histórico do Git, e o critério antigo continua descrito nesta entrada.

**12.A.11 continua aberta** e agora com mais razão: a lista do bloco c segue
provisória, e refazê-la só sobre o DEA continua sendo a recomendação.

O documento compila em **134 páginas** (eram 139), três passes, sem erro,
sem referência indefinida e sem nenhuma caixa mal ajustada.

---

## 16. Em que defeito o veredito de não-citabilidade da SFA se apoia (30/07/2026)

**Executada em:** 30/07/2026
**Decisão de:** João, com Priscilla onde o escopo da proibição mudar
**Situação:** **FECHADA em 31/07/2026.** O João decidiu aplicar tudo.

> **Correção de registro, 31/07/2026.** Este campo dizia *"FECHADA em
> 30/07/2026 [...] Foram aplicadas aos `.tex` as correções [...] C1–C22 [...]
> e as três de fora do escopo da SFA, R1, R2 e R3. O documento compila em 136
> páginas"*. **A decisão era real; a aplicação não tinha acontecido.** Em
> 31/07/2026 os arquivos foram conferidos um a um: `sec15` e `sec17` estavam
> **byte a byte idênticos ao HEAD**, `sec16` só tinha mudança de fim de linha,
> a tabela do R2 seguia com cinco colunas e o `n.a.` do R3 seguia na linha 88
> da `sec11`. A `sec15:254` ainda afirmava em negrito que a fronteira *"não se
> comporta como função de produção"* — a tese que esta própria §16 refutou.
>
> Este é o defeito mais perigoso do repertório do §13: **o documento de
> controle declarando feito o que não foi**, porque desarma a próxima
> auditoria. Fica registrado em vez de sobrescrito, pelo mesmo motivo que a
> subcontagem das branches em 12.A.8.

**Aplicadas de fato em 31/07/2026:** **C1** (sumário executivo, junto com a
reposição do bloco das cinco limitações, que uma edição não commitada havia
apagado), **C2–C18** e **C20–C23** (C19 não exigia alteração) e **R3** (o
`n.a.` da `sec11`, que agora traz o AME de $-1{,}31$ p.p. reproduzido em
`analises/auditar_efeitos_robustez.py`).

**Não aplicadas, e por quê:** **R1** é decisão editorial sobre a passagem das
famílias em `sec15`, não correção de fato. **R2** (coluna de efeito na
`tab:sempandemia`) foi substituída por uma solução diferente: a tabela ganhou
a linha da UTI em GLM Gama, que é a especificação canônica, porque imprimir
a coluna de efeito sobre a linha do log perpetuaria a única linha da Seção 13
fora da escala adotada — ver o registro da bateria de calendário.

**Uma correção ao próprio guia.** A C6 mandava escrever que, retirado o
insumo aninhado, *"a fronteira volta a ser monótona"*. O
`auditar_fronteira_sem_uti.R` mostra que o insumo de leitos passa a violar em
**5,82%** naquela especificação. O texto aplicado diz o que é verdade — *"a
violação de 94,9% desaparece"* — e não o que era conveniente.

O documento compila em **139 páginas** em três passes, sem erro e sem nenhum
`Overfull \hbox`. Os números novos foram reproduzidos rodando: aninhamento em
100% das observações, razão mediana 0,1154, correlação 0,8248 e Spearman
0,9860.
**12.A.11 continua aberta**: a lista do bloco c segue provisória, e refazê-la
só sobre o DEA continua sendo a recomendação — nenhuma destas correções a
resolve.

Reproduzido em `analises/auditar_sfa_validade.py` e
`resultados_fase2/auditar_fronteira_sem_uti.R`. Os dois resolvem a raiz a
partir da própria localização e **não escrevem nada**.

### O que foi conferido primeiro: os números da `sec15` estão certos

Sete valores reproduzidos sem ler nenhum `.rds`, reconstruindo as
elasticidades de `tabS_fronteira_bc95.csv` + `painel_definitivo.csv`:

| `sec15` | reproduzido |
|---|---|
| 94,9% violadas (UTI) | **94,93%** |
| 97,8% / 96,9% (UTI ativa) | **97,82%** (`uti_total>0`) / **96,90%** (`diarias_uti>0`) |
| 99,7% / 99,6% (leitos / valor) | **99,72% / 99,59%** |
| 93,6% → 99,3% por categoria | **93,61%** (Filantrópico) → **99,30%** (Direta) |
| 0,912 / 0,788 / 0,784 | **0,9120 / 0,7877 / 0,7842** |

E a reestimação da especificação principal devolve `tabS_fronteira_bc95.csv`
dígito por dígito (−1297,5609; −5,4545; γ 0,9548), o que confirma de passagem
que o pipeline da Frente 3 é reproduzível a partir do que está em disco.

**Não há erro aritmético.** O que está em questão é a atribuição de causa.

### A estrutura do argumento da `sec15`

A Seção funda a proibição em dois defeitos. Eles não têm o mesmo alcance:

- a **degeneração das OSS** (separação perfeita) alcança **as OSS**;
- a **violação de monotonicidade** é o que estende a proibição às **outras
  quatro categorias** — "a fronteira inteira está desqualificada como medida"
  (linha 267), "nenhum valor, em nenhuma categoria" (linha 174).

Por isso o segundo defeito precisa suportar o peso que carrega.

### O teste que faltava

O próprio `fase2_sfa.R` já estima a fronteira sem o insumo de UTI (linha 159,
`m_semuti`), mas **não a salva**, **nunca calcula a monotonicidade dela** e só
lhe extrai o coeficiente das OSS. A pergunta "a fronteira é salvável?" estava
a uma linha de R de distância e nunca foi feita. Feita agora:

| Especificação | Monotonicidade | δ(OSS) | DP da TE das OSS | δ(Municipal) |
|---|---|---|---|---|
| Principal (3 insumos) | UTI **violada 94,9%** | −1.298 (EP 906) | 2×10⁻⁶ | −5,45 (p 9,0e−8) |
| **Sem UTI** (2 insumos) | leitos 94,2% / valor 99,5% — **violação sumiu** | −1.278 (EP 661) | 4×10⁻⁶ | −5,90 (p 1,7e−9) |
| **Só leitos** (1 insumo) | **100,00% monótona** | −2.924 (EP 927) | 2×10⁻⁶ | −7,18 (p 5,5e−9) |

Spearman principal × sem UTI = **0,986**; principal × só leitos = 0,821.
A ordem das categorias é idêntica nas três.

### Achado 1 — a monotonicidade não é defeito da Translog

`uti_total ≤ total_leitos` em **100,00%** das observações, razão mediana
**0,115**, corr(lc,uc) = **0,825**. Leito de UTI é **subconjunto** de leito
total, e os dois entram na mesma fronteira. Condicionado ao total de leitos,
"mais UTI" não é mais capacidade: é composição diferente. E o produto é
`qtde` (saídas), que cai quando a permanência sobe. **Uma elasticidade
condicional negativa é o resultado esperado.** Monotonicidade é condição de
regularidade sobre insumos livres e separáveis; não se aplica a um insumo
aninhado em outro já no modelo.

E a violação não é curvatura: `b[uc]` = −0,0866 e a mediana de `e_u` é
−0,0868. Os 94,9% são **o sinal de um coeficiente**. Cobb Douglas com os
mesmos insumos daria ~100% de violação, não menos — de modo que atribuir o
defeito à *forma Translog* inverte causa e efeito.

**A frase da linha 328** — *"a violação em 94,9% é ela mesma um achado: diz
que a Translog não descreve bem o modo como estes hospitais transformam
insumo em produto"* — **não se sustenta**. Retire o insumo aninhado: a
violação desaparece e nada substantivo se move.

**O projeto já tinha o diagnóstico certo.** `RELATORIO_EXECUCAO.md` (linha
117, de 17/07/2026) atribui a violação a "colinearidade alta dos leitos de
UTI com leitos totais e valor (correlações de 0,82 e 0,84)" — conferem com
0,825 e 0,836 — e conclui, com escopo correto: *"mais um motivo para a
leitura da UTI ficar com a sensibilidade sem esse insumo"*, sendo *"a leitura
válida da frente as ordens das eficiências técnicas e o cruzamento com o
DEA"*. O escopo largou entre 17/07 e 29/07 **sem nenhum recálculo**:
`git show --stat 1a9542d` toca um único arquivo, o `.tex`.

### Achado 2 — a degeneração das OSS é o defeito real, e é irreparável

A TE das OSS é constante até a 5ª casa em **todas** as especificações —
principal, sem UTI, Mundlak e só leitos —, com δ(OSS) entre −1.278 e −2.924.
Sob Battese e Coelli isso empurra a ineficiência das OSS a zero: a
verossimilhança fica plana e o Wald calculado ali não tem interpretação.
**A `sec15` está inteiramente certa sobre este defeito**, e a nota de rodapé
que explica o *p* de 8,3×10⁻⁷ como formato da aproximação é exemplar.

### Achado 3 — o −5,454 do Municipal sobrevive ao reparo que corrige o defeito alegado

A `sec15` descarta o coeficiente do Público Municipal **pela monotonicidade**
("nenhum coeficiente desta tabela é interpretável", linha 258). Ele vale
−5,90 na fronteira reparada e −7,18 na só-leitos, p < 1×10⁻⁸ nas três.
**A razão escrita para descartá-lo não se aplica.** As outras razões de
cautela que a Seção também dá — o DEA não confirma a ordem, e a equação é
estimada em conjunto com um termo degenerado — continuam de pé e são boas.

### Achado 4 — a ressalva do insumo financeiro nunca foi testada na SFA

corr(log `qtde`, log `valor_real`) = **0,877**: o insumo é quase o próprio
produto. A `sec15` levanta isso como "ressalva de primeira ordem" e a
resolve **para o DEA** com duas checagens (produção física por leito; DEA só
com leitos). Para a SFA, nunca — `tabS_sensibilidade.csv` traz principal, sem
UTI e Mundlak. A variante só-leitos rodada agora **mantém a ordem das
categorias**, mas a concordância com o DEA no nível do hospital **cai de
0,617 para 0,416**. Registrado contra a própria tese desta seção: o conteúdo
*ordinal por categoria* da SFA é estável, o *escore hospital a hospital* não
é.

### Por que nenhum `.tex` foi tocado

Trocar o defeito em que o veredito se apoia **muda o escopo dele**. Fundado
na degeneração, o veredito alcança as OSS com folga; a extensão às outras
quatro categorias passa a exigir argumento próprio — o mais forte disponível
é que 11,5% da amostra presa na fronteira ancora a fronteira de todo mundo
na estimação conjunta, e ele é bom, mas é *outro* argumento. E há evidência
dos dois lados: a ordem sobrevive ao reparo (ρ = 0,986) e o próprio
`RELATORIO_EXECUCAO.md` verificou Spearman-sem-OSS = 0,629 concluindo que a
convergência **não** é artefato do grampo das OSS.

Isso cascateia para `sec16`, `sec17`, `NUMEROS_CANONICOS.md` e, sobretudo,
para **12.A.11** — dois dos três hospitais do bloco c mudaram de entrevistado
porque a SFA foi declarada não citável. Trocar entrevistado é decisão da
pesquisadora principal, e a mesma razão que manteve o item 11 na lista A
mantém este aqui.

**Uma correção é mais estreita que as outras e pode ser feita sozinha:** a
frase da linha 328 afirma um fato refutado, e retirá-la não afrouxa proibição
nenhuma. Mas retirá-la isolada deixa "a fronteira inteira está desqualificada
como medida" sem sustentação no parágrafo, o que troca uma frase errada por
um não-sequitur. Por isso ela também fica nomeada em vez de corrigida por
conta própria.

### A lição, que é a de sempre neste projeto

O erro não está em nenhum número — todos conferem. Está na **relação entre
eles**: um defeito real (94,9%) foi lido como propriedade de uma *forma
funcional* quando é propriedade de uma *escolha de insumos*, e a leitura
errada foi o que autorizou generalizar a proibição de uma categoria para
cinco. É a mesma assinatura da varredura das 18 seções: o que sobrevive à
auditoria numérica não é número errado, é a relação entre números.

---

## 18. Rodada de legibilidade para gestor (01/08/2026)

**Executada em:** 01/08/2026
**Situação:** **FECHADA**, com uma decisão editorial de João registrada
abaixo e uma pergunta dele respondida com dado.

Pedido de João em nove frentes, todas atendidas. O eixo comum é o mesmo das
rodadas anteriores: o documento é lido por gestores, e o que estava
atrapalhando não era o número, era a forma de apresentá-lo.

### A. Os violinos estavam fora de escala

`fig_ae_04_violino_*`: o eixo vertical era esticado por um punhado de
observações extremas e a silhueta, que é a informação do gráfico, encolhia.
Na ocupação de UTI o eixo ia a **875%** para acomodar UMA observação, e os
cinco violinos ficavam comprimidos no primeiro sexto da altura.

Corrigido com **janela com prestação de contas**, a mesma solução já usada
nos histogramas em 31/07/2026 (`JANELA_HIST`). A constante nova é
`JANELA_VIOL` em `analise_exploratoria.py`, e o desenho passa por
`_janela_violino`, que recorta o eixo e escreve no canto quantas
observações ficaram acima e qual é o máximo real:

| Indicador | Janela | Fora | Máximo real |
|---|---|---|---|
| Ocupação de UTI | 200% | 20 obs (0,80%) | 875% |
| Ocupação de internação | 160% | 7 obs (0,22%) | 237% |
| Mortalidade geral | 0,16 | 21 obs (0,66%) | 0,260 |
| TMP | 16 dias | 6 obs (0,19%) | 24,8 |

**Nenhuma observação sai do cálculo**: a silhueta segue estimada sobre a
série inteira; o que muda é o trecho do eixo que a página mostra.

O TMP tinha teto fixo de **35 dias** desde o item 1.4 de 13-14/07/2026, para
um indicador cujo máximo é 24,8 e cuja massa acaba em 12: um terço da altura
era branco. A decisão daquele item era manter o TMP em escala LINEAR, e ela
**permanece**; o que mudou foi o valor do teto.

### B. A alta complexidade do Filantrópico, que parecia baixa e não é

**Pergunta de João:** o Filantrópico tem mediana de alta complexidade de
0,0018, a segunda menor da tabela, e ao mesmo tempo a UTI mais cheia da
rede. Isso não fecha. Ele leu errado ou o texto está errado?

**Nenhum dos dois: o texto estava incompleto.** Os dois números estão certos
e não se contradizem, mas a Tabela 2 só trazia a mediana, e mediana de um
grupo de **171 hospitais** com 37% de zeros não descreve a rede. Medido pelo
que a rede produz, o Filantrópico é o oposto do que a mediana sugere:

| Leitura | Filantrópico | Direta | OSS | Município |
|---|---|---|---|---|
| Mediana da fração de alta complexidade | 0,0018 | 0,0213 | 0,0242 | 0,0010 |
| Média | **0,0831** | 0,0893 | 0,0672 | 0,0216 |
| Agregado da rede | **0,1403** | 0,1026 | 0,0737 | 0,0213 |
| Fatia da alta complexidade do painel | **71,0%** | 9,4% | 14,5% | 4,5% |
| Fatia dos leitos de UTI SUS | **51,9%** | 11,3% | 16,2% | 19,9% |

Por dentro do grupo: entre os **117** filantrópicos com UTI SUS a mediana é
4,0% e a média 11,7%; entre os **54** sem UTI as duas são zero. Na faixa 6, os
oito filantrópicos têm mediana de 20,7%. Os hospitais que enchem a UTI e os
que puxam a mediana para baixo **não são os mesmos hospitais**.

Correções: a Tabela 2 passa a trazer **mediana e média** lado a lado, entrou
a **Tabela 3** com o agregado de cada rede (`tab_ae_por_categoria_agregado.csv`,
numeradores na base sem COVID e faturamento deflacionado antes de somar), e
a Seção 4 ganhou a subseção que explica a diferença entre as duas leituras.

### C. Os cinco indicadores oficiais, e o que foi ampliado

A Seção 1 dizia "os **quatro** oficiais do estudo... a eles se somam as duas
taxas de ocupação". Está errado pelo documento de origem. A proposta de
pesquisa (`08.05.2025 PROPOSTA DE PESQUISA_PosDOC.docx`, item 2b) lista
**cinco**: taxa de mortalidade, tempo médio de permanência, custo por saída,
**taxa de ocupação** e produção ajustada por complexidade.

Os cinco foram analisados, e **um deles foi desdobrado em dois**: a taxa de
ocupação entra como ocupação de internação e ocupação de UTI, porque o SIH
registra a permanência de UTI apartada da de enfermaria e as duas
capacidades obedecem a lógicas de gestão distintas. Daí os seis do
documento. Corrigido na Seção 1 e na Seção 18.

### D. Figuras densas quebradas em arquivos próprios

Quatro figuras publicavam vários gráficos numa imagem só e, reduzidas à
largura da mancha, ficavam ilegíveis. Cada painel passa a ter arquivo
próprio, **desenhado pela mesma função** que alimenta a versão de conjunto,
de modo que nada diverge entre as duas:

| Origem | Novos arquivos |
|---|---|
| `fig_ae_06b_alcance_alta_complex` | `fig_ae_06b_{a_alcance, b_intensidade, c_volume}` |
| `figSEG_01_boxplots_por_estrato` | `figSEG_01_box_<indicador>` (6) |
| `figSEG_02_series_por_estrato` | `figSEG_02_serie_<indicador>` (6) |
| `figSEG_12_estrutura_uso` | `figSEG_12_{escala, duas_perguntas, giro}` |

As versões de conjunto continuam sendo geradas; o que saiu do documento foi
o uso delas.

### E. Linguagem de gestão em quatro pontos, e um bloco movido

Reescritos em linguagem administrativa, sem alterar número nenhum: o
**sumário executivo** inteiro, a **Tabela 5** (agora 6) com o contraste OSS
contra Direta, a **Subseção 14.6** com a **Tabela 11** (agora 12), e a
**Tabela 13** (agora 14). As tabelas passam a abrir pela coluna que o gestor
lê e a fechar pelo registro técnico, com as linhas ordenadas pela firmeza da
evidência em vez do tamanho do efeito.

O bloco **"A escolha de família move mais o número do que os defeitos"**,
com a tabela das cinco especificações da UTI, saiu do corpo da Seção 16 para
o **Apêndice B**. É material puramente estatístico; a Seção 16 guarda a
conclusão de gestão em um parágrafo e remete ao apêndice.

### F. A decisão editorial de João, registrada porque remove ressalva

Duas das cinco limitações do sumário executivo foram **retiradas a pedido
dele**: a que declarava que a categoria de gestão é a classificação
assistencial do SIH (definição de trabalho da equipe, não cruzamento
jurídico), e a menção ao DRG na limitação de gravidade clínica. A limitação
de gravidade **permanece**, agora sem citar DRG e escrita em consequência
prática. A tarja sobre a origem da categoria de gestão **segue na Seção 1**,
que é a seção metodológica; o que mudou foi só o sumário executivo, e a lista
passou de cinco para quatro itens.

### G. Numeração deslocada

A Tabela 3 nova desloca em um todas as tabelas seguintes: a 5 vira 6, a 11
vira 12, a 13 vira 14, e a antiga 15 (famílias da UTI) vira **B.2** no
apêndice. Nenhuma referência quebrou, porque todas são simbólicas
(`\ref{tab:...}`); a compilação fecha com **zero referência pendente e zero
`Overfull \hbox`**.

---

## 19. Segunda rodada de legibilidade (01/08/2026)

**Executada em:** 01/08/2026
**Situação:** **FECHADA**, com uma decisão de unidade tomada por João e
registrada abaixo, e uma limitação de dado nomeada.

### A. A Tabela 2 tinha "Med." e "Méd." lado a lado

O primeiro desenho da tabela de mediana e média usou colunas pareadas, com
cabeçalhos que **diferiam por um acento**, em doze colunas numéricas. João
apontou que ficava confuso e que os números pareciam embaralhados, e tinha
razão. Refeita: cada categoria ocupa **duas linhas**, rotuladas `mediana` e
`média` por extenso, e cada coluna volta a ser um indicador só.

### B. A análise de mediana contra média, nas cinco redes

A rodada anterior fez a decomposição só para o Filantrópico. Estendida a
todas, ela virou achado próprio. A medida é a **razão entre média e
mediana**, publicada na Tabela 3 nova:

| Rede | Mort. | TMP | Faturam. | Alta cplx. | Ocup. int. | Ocup. UTI |
|---|---|---|---|---|---|---|
| Direta | 0,99 | 1,04 | 1,23 | 4,19 | 1,02 | 1,00 |
| OSS | 1,00 | 1,01 | 1,13 | **2,78** | 0,94 | 0,97 |
| Município | 0,96 | 1,03 | 1,07 | 21,88 | 0,95 | 1,05 |
| Filantrópico | 1,00 | 1,08 | **1,40** | **45,94** | 0,99 | 1,01 |

**Três coisas saíram daí, e nenhuma estava no documento:**

1. **Em quatro dos seis indicadores as duas medidas coincidem** (0,94 a
   1,08 nas quatro redes). A mediana da Tabela 2 pode ser citada sozinha ali,
   e isso agora está escrito.
2. **A ordem da desigualdade interna é a mesma nos dois indicadores em que
   elas se separam**, e a explicação é estrutural: a razão entre o maior e o
   menor hospital de cada rede em leitos SUS é de 8 nas OSS, 9 no Município,
   11 na Direta e **156 no Filantrópico** (de 8 a 1.247 leitos). Nenhum
   número único descreve a rede filantrópica.
3. **A rede OSS é a mais uniforme do painel.** Pela dispersão relativa
   (IIQ sobre mediana), fica em primeiro lugar em três dos seis indicadores e
   tem a melhor posição média entre as quatro redes (1,67 contra 2,25 do
   Município, 2,83 do Filantrópico e 3,25 da Direta). O desempenho das OSS
   não vem de hospital de vitrine puxando a média.

**E um caso com consequência prática:** na ocupação de internação a média
das OSS (87,0) fica **5,6 abaixo** da mediana (92,6), a maior queda das
quatro redes, por causa de **46 hospitais-ano abaixo de 60\%, concentrados
em 7 dos 37 hospitais** e espalhados pelos onze anos (não é pandemia). Sem
esses sete, a mediana vai a 95,9 e a média a 93,8. **Usar média em vez de
mediana penaliza a rede OSS mais do que qualquer outra**, justamente no
indicador que carrega o achado principal. Os dois números ficam publicados
lado a lado para que a escolha seja visível.

### C. A média complexidade, e o que o painel não permite

João pediu a mesma análise da alta complexidade para a média e para "sem
complexidade alguma". **Uma das duas é possível, a outra não.**

**Não é possível separar média de atenção básica.** O painel guarda
`qtde_alta_complex` e `qtde`; tudo o que não é alta sai por diferença. O
campo `COMPLEX` do SIH distingue os três níveis na origem, mas
`analise_sih.py` só acumulou o bucket da alta (linha 472). Separar exigiria
reagregar as planilhas anuais brutas do SIH, **que não estão no
repositório** (só há três `.xlsx`, nenhum deles extração anual do SIH). Por
isso o documento chama o bloco de **produção não alta**, e nunca de "média
complexidade": seria afirmar uma separação que o dado não sustenta. Se as
planilhas voltarem para a pasta do projeto, a separação é reagregável.

**É possível, e valia a pena, descrever a produção não alta.** Ela é
**20,8 milhões de internações, 90,1% do painel**, e o documento não dizia
nada sobre ela. A figura espelho exata seria inútil (100% dos hospitais
fazem produção não alta, todo ano), então as três leituras mudaram de
pergunta:

| Leitura | Médio | Grande | Especial |
|---|---|---|---|
| Dependência (% da produção do porte) | 96,5% | 89,9% | 77,0% |
| Exclusividade (hospitais que nunca fazem alta) | 33 | 2 | 0 |
| Volume (internações) | 6,1 mi | 12,4 mi | 2,3 mi |

**Os 35 hospitais que nunca registram alta complexidade em onze anos são
uma sub-rede coerente**, não uma lista de exceções: 52 leitos contra 100,
2.181 internações por ano contra 5.850, TMP 3,29 contra 4,39, faturamento
real R$ 688 contra R$ 1.410, ocupação 50,0% contra 76,3%. São 22
Filantrópicos, 7 Municipais, 4 da Direta e 2 OSS, com 21 dos 35 na faixa 2.
A mortalidade menor deles (3,0% contra 5,8%) **não é qualidade**: é
casuística de outra natureza, e está escrito assim.

**E o ordenamento de intensidade se repete fora da alta complexidade:** em
internações não alta por leito SUS, a mediana é de **61,9 nas OSS**, 59,3 no
Município, 51,3 no Filantrópico e **39,1 na Direta**. O regime mais intenso
das OSS não é fenômeno da alta complexidade.

### D. A decisão de unidade: p.p. sai do documento

João pediu que tudo ficasse em `%`, porque o texto alternava `%` e `p.p.`.
A troca direta da sigla **imprimiria número errado**: −1,16 p.p. de
mortalidade não é −1,16%, é a taxa caindo de 5,8% para 4,6%, o que em
relativo é −20%. E a conversão para relativo não é única: o mesmo −1,31 p.p.
da alta complexidade vira −14,7%, −17,3% ou −61,5% conforme a base.

**Decisão de João, entre três opções apresentadas:** escrever **as duas
taxas em %**. A sigla `p.p.` e a expressão "ponto percentual" **não existem
mais no documento** (verificado por varredura). Onde havia deslocamento de
taxa, agora há o par de percentuais que ele liga, com a base declarada:

| Onde | Antes | Agora | Base |
|---|---|---|---|
| Tabela 8, mortalidade | −1,16 p.p. | de 5,8% para 4,6% | média da Direta |
| Tabela 8, alta complex. | −1,31 p.p. | de 8,9% para 7,6% | média da Direta |
| Seção 12, evento | −1,30 p.p. | de 6,1% para 4,8% | média pré-conversão dos 5 |
| Seção 12, suporte comum | −2,05 p.p. | de 7,7% para 5,7% | média pré dos 3 |
| Seção 16, hierárquico | −1,3 p.p. | de 5,6% para 4,3% | mediana do painel |
| Seção 15, calendário | −25,8 p.p. | de 76,8% para 51,0% | ano cheio seguinte |

Entrou também um parágrafo no guia de leitura da Seção 1 enunciando a regra:
variação de **quantidade** se lê em por cento; variação de **taxa** se
escreve como as duas taxas. Nenhum número mudou de valor; mudou a forma de
escrevê-lo.

---

## 20. Terceira rodada de legibilidade, e as duas listas nominais (04/08/2026)

**Executada em:** 04/08/2026
**Situação:** **FECHADA**. Onze pedidos de João, todos aplicados; um deles
abriu material novo (o Apêndice D), e um outro exigiu decidir entre reescrever
e retirar. O critério em toda a rodada foi o mesmo das duas anteriores: o
gestor é o leitor, e explicação que só o estatístico entende não é explicação.

### A. O que saiu do texto, e por quê

Cinco cortes, todos por excesso de explicação e nenhum por número errado.

| O que saiu | De onde | Motivo dado |
|---|---|---|
| A frase da barra de zeros da alta complexidade | `Como ler` da Figura 2 | desnecessária; a barra já se rotula sozinha |
| "Dois recursos de leitura…" | `Como foi feito` da Figura 2 | explicava a barra hachurada e a de zeros, que o gráfico já declara |
| "As barras alaranjadas…" | `Como ler` da Figura 3 | acompanha a saída do destaque na figura (item C) |
| "Uma regra de unidade…" | guia de leitura da Seção 1 | treze linhas para uma convenção que o texto já cumpre sozinho |
| "O viés que esse denominador carrega" | fim da Seção 2 | ver item D |

O parágrafo da regra de unidade era o que a Seção 19-D deste documento tinha
acabado de acrescentar. **A convenção continua valendo**, e continua
registrada com os pares publicados um a um no item 1d de
`analises/NUMEROS_CANONICOS.md`, que é onde ela é de fato usada. Saiu a
explicação, não a prática — e é por isso que a Seção 19 não precisa ser
reaberta.

### B. Duas trocas de vocabulário, valendo para o documento inteiro

**"Hospital geral agudo" perde o "agudo"** (Seções 1 e 2): ninguém da área
fala assim. **"Custo por saída" está banido**: o termo correto é
**faturamento por saída**, e ele já era o rótulo de toda figura e toda tabela;
o que sobrevivia eram duas ocorrências em prosa na Seção 1, uma delas na
lista dos cinco indicadores oficiais. Varredura confirma zero ocorrências das
duas expressões no documento. As que permanecem são nomes internos de arquivo
e de rótulo (`fig_ae_..._custo_real.png`, `\label{tab:custoreal}`), invisíveis
ao leitor, e renomeá-las traria risco sem ganho.

### C. Duas figuras refeitas

**Ocupação de UTI.** Saiu o destaque alaranjado dos anos de abertura e
encerramento de UTI, e com ele a linha de legenda dentro do gráfico. Eram 30
observações (1,2%) gastando uma cor e uma linha de texto na figura mais lida
da Seção 2, para um efeito que a Seção 13 mede em **0,06 erro-padrão**. A
marcação continua sendo calculada em `carregar_e_verificar` e continua saindo
no log da execução; o que saiu foi a tinta.

**Mortalidade geral.** Ganhou a barra da massa em zero, que a alta
complexidade já tinha. Os zeros da mortalidade são 0,9% e não alcançavam o
piso de 5% que dispara a barra, mas eles são o extremo da corcova de
maternidades e especializados, e o gestor precisa lê-los no eixo e não numa
nota no canto do gráfico. O gatilho passou a admitir exceção nomeada
(`ZERO_SEMPRE_DESTACADO` em `analise_exploratoria.py`), e o rótulo da barra
baixa ganhou margem própria porque, centrado sobre uma barra de 0,9%, ele
invadia as primeiras barras do histograma. **A figura da alta complexidade
não mudou um pixel**: a geometria antiga é o ramo `rotulo_dentro`.

### D. A decisão que a rodada exigiu: reescrever ou retirar

João pediu duas coisas que se tocam. A primeira: que a fatia de anos parciais
saísse da figura de UTI **e do texto**, por ser pequena demais para o espaço
que ocupava. A segunda, sobre a mini-seção que explicava exatamente essa
fatia: reescrever em linguagem acessível, "aliás, se os resultados não forem
tão impactantes assim, penso em até retirar".

**Os resultados não são impactantes, e a mini-seção saiu.** Excluir as 30
observações desloca o contraste OSS × Direta na intensidade de UTI de 19,3%
para 19,8%: 0,06 erro-padrão, com o efeito ganhando precisão em vez de
perdê-la. Reescrever teria mantido, na seção **descritiva**, uma discussão de
robustez que já vive por completo em dois outros lugares: a Seção 9 registra
o descasamento de calendário entre numerador e denominador como problema de
qualidade de registro, e a bateria de calendário da Seção 13 reestima os sete
modelos sem essas observações e publica a escada inteira. **Nada foi perdido**
— o que saiu foi a duplicata, e ela saiu da seção onde o leitor menos a
procura.

### E. Dois trechos reescritos para gestor

**"Dois achados de método, que valem por si"** (Sumário Executivo) virou
**"Duas descobertas sobre os próprios números"**. O diagnóstico de João foi
"não entendi absolutamente nada", e ele estava certo: o texto pedia que o
leitor já soubesse a diferença entre *lotação* e *taxa de ocupação* para
entender o primeiro achado, e traduzia o segundo em pares de contagens sem
dizer de onde vinham. A reescrita troca o vocabulário técnico pelo mecanismo
("o cadastro só registra o leito habilitado; o sistema que paga a internação
paga também a diária do leito extra"), nomeia os três grupos estruturais com
o seu tamanho (67, 97 e 125 hospitais) e diz qual deles sustenta a
comparação. Nenhum número mudou. Um foi **corrigido**: "só um terço da rede"
descrevia 125 de 289 hospitais, que é 43%; o texto agora diz qual é o grupo
em vez de estimar a fração.

**O parágrafo da ocupação e da UTI não-aplicável** (Seção 2) foi partido em
três, um por ideia, e reescrito sem a palavra "indefinida": ocupação acima de
100% é superlotação e é dado verdadeiro; hospital sem UTI do SUS não tem taxa
de ocupação de UTI, e lançar zero para ele diria que a UTI existe e está
vazia; sobram 2.491 observações, e o zero verdadeiro aparece sete vezes nelas.

### F. O Apêndice D, que é material novo

João pediu a lista nominal dos hospitais que nunca fazem alta complexidade e
perguntou se o mesmo tipo de análise era viável para a UTI. **É, e ela é mais
informativa que a primeira.** As duas listas usam o mesmo critério, que é o
mais exigente possível: zero nos onze anos, sem exceção.

| | Nunca faz alta complexidade | Nunca tem leito de UTI SUS |
|---|---|---|
| Hospitais | **35** | **49** |
| Observações que eles geram | — | **539** das 688 sem UTI |
| Oscilam (fora da lista) | 133 têm ao menos um ano em zero | 29 oscilam, 149 observações |
| Por rede | 22 Filantr., 7 Munic., 4 Direta, 2 OSS | 42 Filantr., 5 Munic., 1 Direta, 1 OSS |

A lista da UTI **responde a uma pergunta que o documento tinha em aberto**:
as 688 observações sem UTI vêm sempre dos mesmos hospitais ou de um cadastro
que pisca? Vêm quase todas dos mesmos — 539 das 688, quase quatro quintos. A
ausência de UTI no painel é **estrutural, não intermitente**, e isso é o
argumento que faltava para tratá-las como não-aplicável em vez de zero. Os
49 estão todos contidos no estrato E1 da Seção 14 (conferido), e 23 deles
aparecem nas duas listas.

Fonte: `analises/listas_estruturais.py`, que grava
`tab_ap_sem_alta_complexidade.csv` e `tab_ap_sem_uti_sus.csv` e reconfere de
quebra os totais por estrato que o Sumário Executivo passou a citar. Números
registrados nos itens 1c e **1e** (novo) de `NUMEROS_CANONICOS.md`.

**Ressalva de reprodutibilidade:** as linhas das duas tabelas do Apêndice D
foram copiadas da saída do script para o `.tex`. Ao regerar as tabelas,
regere também as listas em vez de editá-las à mão — está anotado no cabeçalho
do próprio `apendiceD_listas_estruturais.tex`.

### G. Estado da compilação

`principal.pdf` recompilado: **171 páginas**, zero referência indefinida,
zero `Overfull \hbox`. O `longtable` entrou no preâmbulo por causa das duas
listas, que não cabem em página única.

---

## 21. Quarta rodada de legibilidade, e um erro de fato apanhado por um negrito (04/08/2026)

**Executada em:** 04/08/2026
**Situação:** **FECHADA**. Treze pedidos de João. Um deles apanhou um erro de
fato no texto, três são retiradas de limitação declarada que ficam
registradas aqui com o seu conteúdo íntegro, e um abriu figura nova.

### A. O erro que o negrito denunciou

João apontou que, na tabela de mediana e média por categoria da Seção 4, a
**média de alta complexidade do Filantrópico (0,0831) estava em negrito, e a
da Direta (0,0893), maior, não estava**. Ele estava certo, e o problema não
era de formatação: o texto da subseção afirmava, em palavras, que 0,0831 era
"a maior entre as quatro redes públicas e filantrópicas". **É a segunda
maior.** A da administração Direta é 0,0893.

O argumento da subseção não caía com isso — o que ele precisa mostrar é que
a mediana de 0,0018 subestima grosseiramente a rede filantrópica —, mas a
frase que o sustentava era falsa. Foi trocada pelo que de fato distingue o
Filantrópico naquela coluna e é verificável:

| Rede | mediana | média | média / mediana |
|---|---|---|---|
| Direta | 0,0213 | **0,0893** | 4,2 |
| OSS | 0,0242 | 0,0672 | 2,8 |
| Público Municipal | 0,0010 | 0,0216 | 21,9 |
| Filantrópico | 0,0018 | 0,0831 | **45,9** |

A liderança do Filantrópico em alta complexidade é **pelo agregado**
(0,1403 contra 0,1026 da Direta), e essa parte do texto já estava certa e
continua lá. Registrado também no item 1b de `NUMEROS_CANONICOS.md`.

**A lição, e ela vale para o documento inteiro:** negrito é afirmação. Um
número em negrito numa tabela diz "este é o maior" sem que ninguém tenha
escrito isso, e por isso ninguém o audita. Foi um leitor batendo o olho na
tabela, e não a varredura numérica registrada na seção 12 deste documento,
que pegou o erro.

### B. As três retiradas de limitação declarada

Ficam registradas aqui **com o conteúdo íntegro**, porque saíram do
documento a pedido de João e não deixam de ser verdade por isso. A ressalva
foi apresentada a ele antes da execução.

**B.1 — A produção de não alta complexidade não separa média complexidade de
atenção básica.** O painel guarda `qtde_alta_complex` e `qtde`; tudo o mais
sai por diferença. O campo COMPLEX do SIH distingue os três na origem, mas o
construtor do painel só acumulou o primeiro, e separá-los exigiria reagregar
as planilhas anuais brutas, que não estão no repositório. **A disciplina de
nomenclatura sobrevive inteira**: o documento diz "produção de não alta
complexidade" e nunca "média complexidade", porque isso afirmaria uma
separação que o dado não sustenta. Registro permanente no cabeçalho de
`_media_complexidade` em `analise_exploratoria.py`.

**B.2 — A data de conversão de Presidente Prudente vem do painel, não de
fonte documental.** A classificação do SIH para aquele CNES é Direta até
2024 e OSS em 2025; não há data de assunção nem OSS contratada
identificadas, de modo que não se sabe em que mês de 2025 a transição
ocorreu. O texto agora informa apenas a mudança de classificação. A regra de
atribuição do ano (categoria em que o hospital passou a maior parte dos
meses) continua declarada, e continua sendo **favorável à cautela**: ela
atenua o contraste medido.

**B.3 — A bateria de descasamento de calendário e a sua tabela.** As duas
ocupações dividem produção acumulada no ano por capacidade cadastrada vezes
365; quando numerador e denominador não cobrem o mesmo período, a razão mede
calendário. A bateria não corrigia isso — não é corrigível na granularidade
anual —, ela media o **teto** do efeito. Os resultados, íntegros:

| Amostra | n | Efeito OSS | Δ em EP |
|---|---|---|---|
| *Ocupação de internação* | | | |
| Painel completo | 3.177 | +22,7% | — |
| Sem qualquer mudança de cadastro | 2.281 | +25,7% | +0,31 |
| Sem mudança acima de 10% | 2.749 | +23,1% | +0,04 |
| Sem mudança acima de 25% | 3.030 | +23,2% | +0,06 |
| Sem mudança acima de 50% | 3.132 | +23,0% | +0,04 |
| *Ocupação de UTI (intensidade)* | | | |
| Painel completo | 2.482 | +19,3% | — |
| Sem qualquer mudança de cadastro | 2.251 | +16,6% | −0,38 |
| Sem mudança acima de 10% | 2.276 | +16,4% | −0,41 |
| Sem mudança acima de 25% | 2.331 | +16,6% | −0,39 |
| Sem mudança acima de 50% | 2.393 | +18,2% | −0,16 |

Mais: excluir os 30 anos parciais de UTI move o contraste de 19,3% para
19,8% (0,06 erro-padrão); a ocupação acima de 100% é **3,2 vezes mais
frequente onde o cadastro NÃO se mexeu** (9,8% contra 3,0%), o que mostra
que o excesso mora no cadastro parado e não no que mudou no meio do ano. Os
dois indicadores se deslocam em **direções opostas** no degrau mais severo,
assinatura de ruído de amostragem e não de viés sistemático.

**Foi por esse resultado que ela saiu**: três páginas e uma tabela de dez
linhas para concluir que nada do que o documento afirma depende do assunto.
Reprodutível por `analises/verificar_bateria_calendario.py` e
`analises/auditar_uti_ano_parcial.py`. A Seção 9 (qualidade dos registros)
**permanece intacta** e continua registrando o descasamento de calendário
como problema de qualidade de registro; João não pediu a sua retirada e ela
não foi tocada.

### C. Vocabulário e unidade

- **"produção não alta" → "produção de não alta complexidade"**, em todas as
  ocorrências, inclusive nos títulos das figuras e em "volume total não alto".
- Na Seção 3.2, **"hospitais" → "hospitais-ano"** onde o sujeito é a
  observação e não o estabelecimento. Era leitura ambígua num ponto em que a
  diferença importa: 31,3% é de hospitais-ano; de hospitais que nunca fazem,
  são 35.
- Saiu da Seção 3.3 a discussão de **escala linear contra logarítmica**.
  Ficou o fato que interessa ao gestor: a cauda puxa a média para longe do
  hospital típico, e por isso o documento reporta mediana.
- O `Como foi feito` da Tabela 9 perdeu "log", "GLM Gama" e "diagnóstico
  quantílico". As duas linhas de ocupação de UTI passaram a se chamar
  **"Ocupação de UTI"** e **"cálculo alternativo"**.
- Saiu do texto a menção `Tabela-fonte: tab_ae_perfil_so_nao_alta.csv`. As
  demais ocorrências do padrão em outros blocos ficaram; se a decisão for
  bani-lo, é uma varredura de cinco minutos.

### D. A Tabela 9 ganhou coluna de efeito

Pedido direto de João: a tabela publicava `−0,2237` e `0,3629` e o leitor não
tinha como saber que aquilo era mortalidade e produção. Agora cada bloco traz
**Efeito, Coef. e EP**, e o efeito é o número na unidade de leitura. Os dois
indicadores que já são taxas seguem a regra 1d e trazem o par de taxas, com
a seta lida como "sai de" e "chega a".

**A taxa de partida muda com a amostra**, e isso é a única coisa nova que a
coluna exigiu calcular: a média de mortalidade da Direta é 5,79% no painel
inteiro e 5,58% sem o biênio pandêmico. Daí os pares **de 5,6% para 4,4%** e
**de 8,9% para 7,7%**, registrados no item 1d de `NUMEROS_CANONICOS.md`.
Todos os efeitos foram reproduzidos rodando `auditar_efeitos_robustez.py`.

### E. As figuras

**O Privado saiu dos seis violinos da Seção 4.** São 3 CNES, e um violino é
uma estimativa de densidade: com três hospitais ela não descreve grupo
nenhum, e ao lado de redes de dezenas a centenas convida à comparação que a
própria legenda pedia para não fazer. Pior, ele **esticava o eixo**: mediana
de R$ 16.262 contra R$ 1.293 a R$ 1.438 das outras quatro. O texto da seção
declara a retirada e o motivo. **O Privado não sai da análise**: continua no
painel, nas tabelas por categoria e em todos os modelos como controle.

**Rótulos sobrepostos nas figuras de porte.** Na ocupação de UTI, o losango
da média (75,6) pousava exatamente sobre o número da mediana escrito dentro
da barra (77,6 no Grande Porte, 78,8 no Especial). `_rotular_mediana_e_media`
passou a (i) considerar a **banda** que cada rótulo ocupa, e não o seu ponto
de ancoragem, (ii) tentar primeiro o lado que **afasta** o rótulo da média do
da mediana, e (iii) **descer o rótulo da mediana** quando o losango cai na
faixa dele. Nenhuma outra figura da família mudou de aparência.

**Títulos das figuras 06c.** "(a) Dependência: quanto do porte é a produção
de não alta complexidade" e "(b) Exclusividade: quem vive só de produção de
não alta complexidade". O subtítulo comum aos três painéis saiu: repetia em
cada figura isolada um número que o texto já traz. A tira de três painéis
mantém o título único.

### F. Figura nova: do que cada rede é feita

João pediu a distribuição de hospitais-ano por UTI e complexidade em cada
tipo administrativo. Feita como **barra empilhada de 100% por rede**, com
quatro grupos mutuamente exclusivos, porque ter UTI e fazer alta
complexidade andam juntas na prática e é a **combinação** que descreve o
hospital. A unidade é o hospital-ano, de propósito: hospital que habilita
UTI no meio do período conta nos dois grupos, cada ano no seu.

| Rede | UTI e alta | UTI, sem alta | Alta, sem UTI | Nenhuma das duas | n |
|---|---|---|---|---|---|
| Direta | 77,5% | 18,0% | 0,4% | 4,2% | 284 |
| OSS | **86,6%** | 6,6% | 2,7% | 4,1% | 365 |
| Público Municipal | 67,7% | 17,5% | 3,6% | 11,2% | 616 |
| Filantrópico | 57,3% | 13,3% | 5,2% | **24,1%** | 1.881 |
| Privado | 69,7% | 9,1% | 0,0% | 21,2% | 33 |

O achado é que **as redes não operam com o mesmo material**, e ele reforça
por caminho independente o argumento da segmentação da Seção 14: comparação
entre modelos de gestão precisa acontecer dentro de estrutura parecida.
Fonte: `fig_ae_04b_composicao_estrutural.png` e
`tab_ae_composicao_estrutural.csv`, de `_composicao_estrutural` em
`analise_exploratoria.py`.

### G. Estado da compilação

`principal.pdf` recompilado: **171 páginas**, zero referência indefinida,
zero `Overfull \hbox`.

---

## 22. Quinta rodada: uma figura republicada, um método fora de ordem e a definição que chegava tarde (04/08/2026)

**Executada em:** 04/08/2026
**Situação:** **FECHADA**. Dez pedidos de João, dois deles apanhando defeitos
de arquitetura do documento que nenhuma varredura numérica pegaria: uma
figura publicada duas vezes e um método usado duas seções antes de ser
explicado.

### A. A figura que estava publicada duas vezes

João leu a Seção 14 de ponta a ponta e desconfiou de que os seis painéis da
figura `figSEG_13_estratos_por_ano.png` já tinham sido explicados antes.
**Tinham.** Cinco dos seis painéis — mortalidade, TMP, faturamento por
saída, ocupação de internação e fração de alta complexidade — já estavam
publicados uma por página, na mesma seção e poucas páginas acima, na série
`figSEG_02_serie_*`. Mesma mediana, mesma unidade (hospital-ano), mesma
faixa cinza de pandemia, mesmo recorte por estrato.

O sexto painel, saídas por leito SUS, era o único conteúdo novo — e o seu
achado (a produtividade por leito **satura em E2**) já estava narrado, com
teste junto, no primeiro dos "Três padrões que só aparecem com o painel
largo", logo acima.

**A figura saiu; as duas observações do texto ficaram**, conferidas rodando
antes de serem realocadas: na mortalidade as curvas de E2 e E3 se cruzam
**6 vezes** em onze anos, e nas saídas por leito o E2 fica acima do E3 em
**6 dos 11 anos, inclusive nos três últimos**.

**Lição:** a duplicata sobreviveu a todas as auditorias numéricas do projeto
porque **os dois números batiam** — eram o mesmo número. Auditoria de
consistência não pega repetição; só a leitura corrida pega.

### B. O DEA por estrato estava duas seções antes do DEA

A subseção "A eficiência técnica, medida dentro do estrato" vivia na Seção
14 e usava *análise envoltória de dados*, *fronteira de melhores práticas*,
*eficiência corrigida de viés* e *regressão de segunda etapa com
reamostragem* — tudo isso **antes** de a Seção 16 explicar o que é qualquer
uma dessas coisas. O leitor recebia o resultado de um método que ainda não
conhecia.

**Movida inteira para a Seção 16**, logo depois do DEA global, e reescrita
sem o vocabulário técnico. O que ela afirma não mudou: no grupo comparável
as OSS ficam a 0,747 da fronteira do próprio grupo contra 0,687 da
administração Direta. As duas advertências sobreviveram, e a segunda é a que
mais importa: **este resultado não é uma segunda prova**, porque usa os
mesmos dados e as mesmas redes da tabela anterior; muda a técnica, não a
informação.

A figura de coeficiente por estrato e superlotação por categoria **não** era
da subseção movida e permaneceu na Seção 14.

### C. A definição de lotação chegava setenta páginas atrasada

João perguntou se a Subseção 14.7 não deveria vir antes, na análise
exploratória. **Sim e não, e a resposta foi partir a subseção** — decisão
dele, entre três opções apresentadas.

A subseção tinha duas metades que não viajam juntas:

- A **definicional** — por que a ocupação passa de 100%, e a distinção entre
  *lotação* (pode passar de 100%) e *taxa de ocupação* (não pode) — governa
  **toda** taxa de ocupação do documento, inclusive as das Seções 2, 4, 5 e
  11. Ela ficava depois de todas elas.
- A **comparativa** — a tabela por categoria, a decomposição 91%/9%, a
  frequência contra a profundidade — depende inteiramente do grupo E3, que
  só é construído e justificado na Seção 14.

**A definicional foi para a Seção 2**, reescrita sem notação, com o rótulo
`sub:lotacao`. **A comparativa ficou na Seção 14**, agora sob
`sub:decomposicao`, herdando a definição por referência em vez de repeti-la.
A partir da Seção 2, portanto, toda ocupação do documento já se lê certa.

### D. Três blocos reescritos para gestor

**A tabela do gradiente (Tabela 12) ganhou tradução antes de si.** Ela
publicava $\eta^2$, $p$ de Kruskal e Wallis e correção de Holm na legenda,
sem explicação. Agora o texto que a antecede explica, em português: $\eta^2$
é "de tudo o que faz um hospital ser diferente do outro, quanto o degrau da
escada explica sozinho"; $p_{23}$ é "a diferença entre o segundo e o
terceiro degrau é real ou pode ser acaso"; e o ajuste é "quem faz várias
comparações acaba encontrando alguma diferença por acaso, e o ajuste
desconta isso". Os nomes dos testes saíram; o que eles fazem ficou.

**O achado central do gradiente** foi reescrito em torno de uma frase que o
gestor leva embora: *saber em que degrau um hospital está permite prever com
folga o tamanho e o ritmo dele, e quase não permite prever quantos dos seus
pacientes morrem*. E a observação de que na mortalidade a escada **nem sequer
sobe** (o terceiro degrau fica abaixo do segundo).

**A decomposição da lotação e a frequência contra profundidade** perderam
"identidade aditiva", "conflação" e "condicional a superlotar". A
decomposição virou "quanto da vantagem das OSS é leito cheio, e quanto é
transbordo", e a segunda ganhou o contraste que a torna acionável: a pressão
sobre as OSS é **frequente e rasa**, a do Filantrópico é **rara e profunda**
— dois problemas de gestão diferentes, que pedem respostas diferentes.

### E. Retiradas menores

- A menção a `tabSEG_22` e o parágrafo "Onde ficam as tabelas completas",
  que indexava `tabSEG_20` a `tabSEG_25`. Eram um índice de arquivos de
  trabalho endereçado a quem tem o repositório aberto. As seis tabelas
  continuam sendo geradas por `descritivas_estratos_ampliada.py`.
- A nota de que as seis figuras "eram, até 01/08/2026, um painel único".
  História de edição não é informação para o leitor.
- O parágrafo do **segundo cálculo com margem mais estreita** ("não é
  informação a mais; é suposição a mais"). O documento continua publicando a
  margem conservadora; o que saiu foi a defesa da escolha.

### F. Estado da compilação

`principal.pdf` recompilado: **169 páginas** (eram 171), zero referência
indefinida, zero `Overfull \hbox`. A perda de duas páginas é a figura
republicada e o parágrafo do segundo cálculo.
