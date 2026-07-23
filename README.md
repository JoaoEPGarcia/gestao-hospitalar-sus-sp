# Gestão Hospitalar no SUS: Modelo Institucional e Desempenho (SUS/SP, 2015 a 2025)

Repositório da pesquisa sobre o impacto do modelo institucional e
organizacional na prestação de serviço hospitalar da rede SUS do Estado
de São Paulo. Reúne os códigos, as tabelas, as figuras e os relatórios
da etapa de Análise Exploratória, construída sobre um painel balanceado
de **289 hospitais acompanhados de 2015 a 2025 (3.179 observações de
hospital e ano; pós-ETAPA F de 15/07/2026)**.

O painel definitivo corrente é `analises/painel_definitivo.csv` (289
hospitais × 11 anos = 3.179 observações, pós-ETAPA F de 15/07/2026);
qualquer arquivo com `317`/`3.487` ou `314`/`3.454` no nome ou no
conteúdo é **histórico** (estados pré-patch e pré-ETAPA F). A fonte de verdade operacional do
painel é `analises/LEIAME_painel_definitivo.txt`; o registro da
verificação pós-patch é `relatorio_verificacao_painel_jul2026.md`.

## Equipe

* João Eduardo Pastori Garcia (Estatístico Responsável)
* Priscilla Reinisch Perdicaris (Pesquisadora Principal)
* Alberto Tomasi Diniz Tiefensee (Revisor e Responsável pelo Banco de Dados)

## Estrutura

* `analise_sih.py`: pipeline de leitura dos arquivos anuais do SIH/SUS
  (streaming dos xlsx) e agregação em painel de hospital e ano.
* `construir_painel_definitivo.py`: funil documentado de seleção
  (etapas A, B, C1, C2, D, E e F) que gera o painel analítico
  `analises/painel_definitivo.csv`.
* `analise_exploratoria.py`: script da Análise Exploratória; gera as 94
  figuras de `analises/figuras_analise_exploratoria` e as tabelas
  `tab_ae_*` de `analises/tabelas`.
* `diagnostico_painel_definitivo.py`, `verificacoes_painel_definitivo.py`,
  `verificacao_pos_patch.py`: scripts de diagnóstico e auditoria do painel.
* `analises/analise_exploratoria.md`: relatório da Análise Exploratória
  em prosa, com todos os números extraídos das execuções.
* `analises/latex/`: documento da pesquisa em LaTeX para o Overleaf
  (`principal.tex`, seções em `secoes/` e instruções em
  `LEIAME_overleaf.txt`), com linguagem adaptada para gestores e um
  bloco explicativo para cada figura.
* `estimacao.py`: estimação (fase 2 em Python) sobre o painel definitivo.
* `resultados_fase2/`: reexecução em R da fase 2 (`preparo_fase2.R` e os
  `fase2_*.R`), com `RELATORIO_EXECUCAO.md` documentando ambiente e ordem.
* `analises/LEIAME_painel_definitivo.txt`: fonte de verdade operacional
  do painel (definição das colunas e das decisões da equipe).
* `relatorio_verificacao_painel_jul2026.md`: registro da verificação
  pós-patch (CHANGE 1 e CHANGE 2; 317→314 e 3.487→3.454).
* `criterios_construcao_painel.md`: critérios metodológicos do funil de
  seleção do painel.

## Como reproduzir

1. Instalar as dependências: `pip install pandas openpyxl matplotlib
   seaborn numpy pyarrow scipy statsmodels`.
2. Colocar na raiz os arquivos anuais do SIH (excluídos deste
   repositório pelo tamanho; ver a nota abaixo).
3. Rodar o pipeline do painel nesta ordem: `python analise_sih.py` →
   `python construir_painel_definitivo.py` →
   `python verificacoes_painel_definitivo.py` →
   `python diagnostico_painel_definitivo.py`.
4. Análises sobre o painel: `python analise_exploratoria.py` (Análise
   Exploratória) e `python estimacao.py` (estimação). A fase 2 em R fica
   em `resultados_fase2/`: rodar `preparo_fase2.R` e depois os
   `fase2_*.R` (todos leem `analises/painel_definitivo.csv`).
5. Para o documento: subir `analises/latex/principal.tex`, a pasta
   `analises/latex/secoes` e a pasta
   `analises/figuras_analise_exploratoria` no Overleaf e compilar duas
   vezes com pdfLaTeX. Detalhes em `analises/latex/LEIAME_overleaf.txt`.

### Compilar localmente em outro computador

As pastas de figuras dentro de `analises/latex/` são vínculos locais
(*junctions*) e ficam de fora do git; as imagens em si estão
versionadas em `analises/figuras_*`. Depois de clonar, recrie os
vínculos uma vez e compile:

```powershell
cd analises/latex
./vincular_figuras.ps1     # recria os vínculos para as figuras versionadas
latexmk -pdf principal.tex # ou: pdflatex principal.tex (duas vezes)
```

## Nota sobre os dados

Os arquivos brutos anuais do SIH (86 a 113 MB cada) não estão
versionados por excederem o limite de tamanho do GitHub; a fonte é o
DataSUS (SIH/SUS, Estado de São Paulo, 2015 a 2025). O painel agregado
(`analises/painel_definitivo.csv`), a planilha de classificação
Barcelona e todas as saídas derivadas estão versionados, de modo que a
Análise Exploratória é reproduzível diretamente a partir do painel.

## Decisões registradas

O IPCA usado na correção monetária é a variação de dezembro a dezembro
do IBGE, com 2025 fechado em 4,26%. O porte hospitalar usa
classificação fixa pela mediana de leitos (cortes oficiais 50, 150 e
500). As análises que envolvem mortalidade usam somente a versão
estrutural do escore de complexidade (salvaguarda de circularidade). O
modelo de gestão é definido pela variável `modelo_gestao_proxy` (a
partir da classificação assistencial do SIH), adotada como **definição
do projeto** — não mais um proxy provisório: PPP e Autarquia não são
desmembrados e "Público Municipal" entra como dummy única. A categoria
Privado tem 3 CNES — inclui o HU-UFSCar (hospital público federal da
Ebserh, agrupado por conveniência estatística, n=3) — e não admite
leitura de efeito médio.
