# Pendências abertas do projeto

Itens que aguardam decisão e **não** estão cobertos pelas pendências técnicas
da fase 2, registradas na Seção 8 de `resultados_fase2/RELATORIO_EXECUCAO.md`
(brms/Stan, SFA degenerado, segunda etapa do DEA). Cada item aqui traz a data
de abertura, a evidência que o motivou e de quem é a decisão.

---

## 1. Varredura de consistência texto ↔ figura ↔ tabela-fonte nas 18 seções

**Aberta em:** 26/07/2026
**Decisão de:** João
**Situação:** aguardando decisão; não autorizada nesta rodada

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
