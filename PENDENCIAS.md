# Pendências abertas do projeto

Itens que aguardam decisão e **não** estão cobertos pelas pendências técnicas
da fase 2, registradas na Seção 8 de `resultados_fase2/RELATORIO_EXECUCAO.md`
(brms/Stan, SFA degenerado, segunda etapa do DEA). Cada item aqui traz a data
de abertura, a evidência que o motivou e de quem é a decisão.

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
*sabia* estarem desatualizados pela ETAPA F. Um erro que nunca dependeu da
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
OSS, 27 Direta, 3 Privados), os 25 excluídos pela ETAPA F, os 5 conversores.

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
**Situação:** bloqueada por ambiente, não por decisão

O ambiente de trabalho da auditoria de julho de 2026 **não tem Python
instalado**: `python`, `python3` e `py` resolvem apenas para os *stubs*
da Microsoft Store em `WindowsApps`, não há venv no repositório, conda
está ausente e não há instalação em `Programs\Python`, `Program
Files\Python*`, `C:\Python*`, `anaconda3` ou `miniconda3`. Três itens
ficaram parados por isso.

**(a) Figuras dos conversores em valores reais.** As cinco
`fig_ae_09_conversor_*_custo_saida.png` plotam valores **nominais**,
porque `analise_exploratoria.py:905-923` itera sobre `INDICADORES`, que
contém `custo_saida`. Como o documento passou a tratar o faturamento
sempre em valores reais, a Seção 7 deixou de imprimir a variação
percentual nominal e remete à Seção 16; as cinco legendas declaram
"valores correntes". A conversão completa — prosa e figuras — depende de
regerar as figuras com `custo_real`.

**(b) Seções 2 e 9 em valores reais.** `tab_ae_univariada.csv` e
`tab_ae_outliers.csv` não têm coluna `custo_real`. As duas seções
declaram "valores correntes" com remissão à Seção 6, mas a conversão
exige recomputar as duas tabelas.

**(c) Item 10 — geografia da seleção.** Ver item 5 abaixo, que tem
motivo próprio além deste.

---

## 5. Classificação geográfica em `selecao_entrevistas.py`

**Aberta em:** 27/07/2026
**Decisão de:** Priscilla e Alberto (não é correção editorial)
**Situação:** **não aplicar sem ratificação**

A Seção 16 rotula três hospitais como "interior" incorretamente: Santos
(2 hospitais) é Baixada Santista, e Cotia e Guarulhos são Região
Metropolitana de São Paulo. A origem é `selecao_entrevistas.py:90-91`:

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

## 6. Data de conversão do Hospital Estadual de Presidente Prudente

**Aberta em:** 27/07/2026
**Decisão de:** João (pesquisa documental)
**Situação:** aberta

A Subseção 7.1 documenta as datas de assunção das cinco conversões. Duas
estão confirmadas e duas são aproximadas:

| CNES | Hospital | OSS | Assunção | Confiança |
|---|---|---|---|---|
| 2081695 | Conjunto Hospitalar de Sorocaba | Seconci-SP | 1º/11/2018 | confirmada |
| 2078287 | CRSM / Pérola Byington | Seconci-SP | set/2022 | confirmada |
| 2082225 | H. Geral de Taipas | IRSSL / Sírio-Libanês | ~set/2024 | **aproximada** |
| 2091755 | H. Geral de Vila Penteado | IRSSL / Sírio-Libanês | ~set/2024 | **aproximada** |
| 2750511 | H. Est. de Presidente Prudente | **não localizada** | **não localizada** | — |

As datas aproximadas foram inferidas de reportagem de 08/10/2024 que
noticiava os "primeiros trinta dias de contrato". A do Presidente
Prudente não foi localizada, e a OSS responsável também não.

**Por que importa.** A data de assunção determina quantos meses de cada
ano pertencem a cada regime, e a Subseção 7.1 argumenta que os anos
parciais **atenuam** o contraste medido. Sem a data de Presidente
Prudente, esse argumento vale para quatro dos cinco conversores.

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

As `figB01_ppcheck_*` **não estão no documento** — existem em
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
