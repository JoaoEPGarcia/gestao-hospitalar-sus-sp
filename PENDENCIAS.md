# Pendências abertas do projeto

Itens que aguardam decisão e **não** estão cobertos pelas pendências técnicas
da fase 2, registradas na Seção 8 de `resultados_fase2/RELATORIO_EXECUCAO.md`
(brms/Stan, SFA degenerado, segunda etapa do DEA). Cada item aqui traz a data
de abertura, a evidência que o motivou e de quem é a decisão.

---

## 0-bis. Varredura de `resultados_fase2/tabelas/` (27/07/2026) — achados abertos

**Aberta em:** 27/07/2026
**Decisão de:** João, com Priscilla onde indicado
**Situação:** aberta — relatório apenas, nada corrigido

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

**Camada 3, pendente.** 48 PNGs únicos, em 8 seções que declaram valores
impressos na figura (`sec01` a `sec06`, `sec08`, `sec11`) — a estimativa
inicial de 25 a 40 estava baixa. Subdividir: piloto em `sec08` e `sec04`
(10 PNGs, com base de comparação já conhecida) → validação → resto.

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
**Situação:** aberta, sem decisão de quando resolver

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
**Situação:** legendas corrigidas; conversão do código depende de Python

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
premissa errada e foi interrompida; a branch `repaginacao-jul2026`
existe, está vazia e atrás de `master`.

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
O documento vai de 113 a **127 páginas**, com compile limpo em três passes.

O que segue aberto está separado em **duas listas**, porque são coisas
diferentes e misturá-las esconde qual delas depende de alguém decidir.

### A. Pendente por DECISÃO HUMANA — o trabalho está pronto ou não se aplica

Nenhum destes é destravado por mais análise.

1. **Leitura humana do PDF por João.** Nenhuma auditoria numérica substitui.
   As 138 conferências automáticas testam texto contra fonte; não testam se
   o texto está bem escrito nem se a argumentação se sustenta.
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

### B. Pendente por TRABALHO NÃO FEITO — ninguém precisa decidir nada

Estes só dependem de alguém executá-los.

1. **Verificação da coluna `Leitos` do arquivo Barcelona** contra o histórico
   `ST_LEITO` do DataSUS. Asserção registrada em R1, nunca medida.
2. **Comparação do leito contratualizado CGCSS/SES-SP com `leitos_sus`.**
   Asserção do Alberto, nunca medida. O portal não está no painel.
3. **Datas exatas de contrato e OSS responsável** dos cinco conversores
   (item 6). O mês de Presidente Prudente e a OSS contratada seguem não
   identificados.
4. **Eixo "Densidade" dos histogramas** (item 7): a decisão entre remover a
   curva KDE ou reescalá-la já está formulada; falta executar.
5. **Camada 3 da varredura de consistência** (item 1): 48 PNGs em 8 seções
   que declaram valores impressos na figura, nunca conferidos.
6. **Contagens inteiras** (item 3): 412 inteiros, 188 anos e 89 códigos CNES
   sem verificação. A auditoria de 29/07 cobriu as contagens do texto novo,
   não as do documento antigo.
7. **Os quatro achados da varredura de `resultados_fase2/tabelas/`**
   (item 0-bis), todos abertos: a equação de ineficiência da SFA ausente do
   documento, a violação de monotonicidade do insumo de UTI não reportada, o
   "todas as amostras" da Seção 15 e a cobertura de
   `tabS_sensibilidade.csv`.
8. **Indexar `painel_definitivo.csv`, `resultados_fase2/dea/` e
   `resultados_fase2/sfa/`** na triagem automatizada — pré-requisito comum
   dos itens 1 e 3.
9. **`estimacao.md` cobre só as seções 1 a 3 de `estimacao.py`** (item 2).
   *Este item tem uma metade em cada lista:* ampliar ou não é decisão
   editorial; ampliar, se decidido, é trabalho.
