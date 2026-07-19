# Parágrafos "como ler" — bateria fig_cruz (diretriz B1, 15/07/2026)

As figuras da bateria de cruzamento **não embutem mais caixa de "como ler"**:
a explicação acompanha cada figura como parágrafo no documento em que ela for
usada (LaTeX, slides, relatório). Este arquivo é a fonte desses parágrafos —
um por figura, mesmo conteúdo que estava nas caixas. Valem para a versão
completa e para a versão `_sem_pandemia` de cada figura (quando existir);
a diferença entre versões está indicada no próprio título de cada PNG.

O que **permaneceu dentro das figuras** por ser conteúdo, não instrução de
leitura: o selo "PRÉVIA — painel pré-Etapa 3 (314 CNES)"; a anotação factual
da fig_cruz_02 (medianas brutas vs. coeficientes de modelo); os rótulos de
quadrante da fig_cruz_05; e a nota do grupo Privado nas figs. 03/07/08,
exigida pela regra única aprovada em 15/07/2026.

---

## fig_cruz_01 — Trajetória dos 5 conversores (pequenos múltiplos)

Cada linha de painéis é um hospital que converteu de administração Direta para
OSS, em ordem cronológica de conversão; a linha vermelha tracejada marca o ano
de entrada na gestão OSS, e a escala é igual dentro de cada coluna para
permitir comparar hospitais no mesmo indicador. Os indicadores oficiais já
excluem os procedimentos específicos de COVID (código 999); a versão "sem
2020–2021" remove os dois anos por inteiro, porque a composição de casos do
biênio pode diferir por outras razões além do código 999 — as duas versões
não são redundantes. Na versão completa, a faixa cinza marca 2020–2021.

## fig_cruz_02 — Mortalidade OSS com/sem os 5 conversores

A linha verde cheia é a mediana anual de mortalidade da categoria OSS como
está no painel; a tracejada recalcula a mesma mediana retirando os 5
hospitais que converteram de Direta para OSS; a linha azul é a administração
Direta, como referência. São medianas simples por ano, sem controles — leitura
descritiva. A categoria Privado não entra (n=3, não interpretável). A caixa de
texto dentro da figura não é instrução de leitura, é o achado: nas medianas
brutas a OSS nunca esteve abaixo da Direta; é nos modelos (efeito fixo) que o
sinal do efeito OSS inverte quando os 5 conversores saem.

## fig_cruz_03a/03b/03c — Heatmap-bolha: categoria × complexidade

Cada bolha é uma célula categoria administrativa × faixa de complexidade
Barcelona: a cor mostra a mediana do indicador (mais escura = maior) e o
tamanho mostra quantos hospital-ano sustentam a célula (o "n=" impresso sob
cada bolha). Células com bolha pequena têm poucas observações e devem ser
lidas com cautela. O grupo Privado (n=3) fica fora desta comparação — nota na
própria figura.

## fig_cruz_04 — Eficiência técnica (DEA e SFA) no tempo

Escore mais alto significa mais produção para os mesmos insumos. Os dois
painéis estimam a mesma ideia por métodos diferentes (DEA-BCC corrigida de
viés à esquerda; SFA/BC95 à direita) — a concordância entre eles reforça a
leitura. O Privado aparece em pontilhado cinza: com n=3, não há leitura de
efeito médio para o grupo.

## fig_cruz_05 — Dispersão faturamento × mortalidade

Cada ponto é um hospital-ano; o tamanho é proporcional ao volume de saídas e o
eixo horizontal está em escala logarítmica. As linhas tracejadas são as
medianas gerais das 4 categorias comparáveis — o Privado fica fora das
referências e aparece apenas como X cinza (n=3). Os rótulos de quadrante são
descritivos, não normativos. Atenção: é correlação observada, não causa — não
há controle de complexidade, porte ou perfil de atendimento.

## fig_cruz_06 — Mapa de SP por categoria

Cada ponto é um hospital, posicionado na sede do seu município (centroide da
malha municipal do IBGE, API de malhas v3, acesso em 15/07/2026); a cor é a
categoria administrativa e o tamanho é a complexidade estrutural (Barcelona).
Municípios com mais de um hospital têm os pontos abertos em anéis ao redor da
sede, de forma determinística (ordenado por CNES) — a posição dentro do
município não é endereço. O Privado aparece como X cinza, fora da comparação
(n=3).

## fig_cruz_07a/07b — Ocupação por categoria × faixa no tempo

Há um painel por categoria administrativa; dentro de cada painel, uma linha
por faixa de complexidade Barcelona (azul mais escuro = mais complexo), com a
mesma escala em todos os painéis para permitir comparação direta. A ocupação
não tem versão "sem COVID" no nível de procedimento — por isso a variante sem
2020–2021 remove os dois anos por inteiro, e aqui a diferença entre versões é
real. O Privado (n=3) fica fora desta comparação — nota na própria figura.

## fig_cruz_08 — Radar por categoria (5 indicadores)

Os eixos são normalizados entre as 4 categorias comparáveis: em cada
indicador, 0 é a categoria com a menor mediana e 100 a com a maior, **sem
inverter direção** — mortalidade alta aparece "grande" no eixo, o que não é
bom desempenho. Por isso a área da forma não é um escore: leia apenas a
posição relativa das categorias em cada eixo, indicador a indicador. O
Privado (n=3) fica fora da comparação — nota na própria figura.
