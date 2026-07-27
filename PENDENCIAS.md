# Pendências abertas do projeto

Itens que aguardam decisão e **não** estão cobertos pelas pendências técnicas
da fase 2, registradas na Seção 8 de `resultados_fase2/RELATORIO_EXECUCAO.md`
(brms/Stan, SFA degenerado, segunda etapa do DEA). Cada item aqui traz a data
de abertura, a evidência que o motivou e de quem é a decisão.

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
