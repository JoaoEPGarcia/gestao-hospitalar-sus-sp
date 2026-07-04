# Gestão Hospitalar no SUS: Modelo Institucional e Desempenho (SUS/SP, 2015 a 2025)

Repositório da pesquisa sobre o impacto do modelo institucional e
organizacional na prestação de serviço hospitalar da rede SUS do Estado
de São Paulo. Reúne os códigos, as tabelas, as figuras e os relatórios
da etapa de Análise Exploratória, construída sobre um painel balanceado
de **314 hospitais acompanhados de 2015 a 2025 (3.454 observações de
hospital e ano)**.

## Equipe

* João Eduardo Pastori Garcia (Estatístico Responsável)
* Priscilla Reinisch Perdicaris (Pesquisadora Principal)
* Alberto Tomasi Diniz Tiefensee (Revisor e Responsável pelo Banco de Dados)

## Estrutura

* `analise_sih.py`: pipeline de leitura dos arquivos anuais do SIH/SUS
  (streaming dos xlsx) e agregação em painel de hospital e ano.
* `construir_painel_definitivo.py`: funil documentado de seleção
  (etapas A, B, C1, C2, D e E) que gera o painel analítico
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
* `criterios_construcao_painel.md`: critérios metodológicos do funil de
  seleção do painel.

## Como reproduzir

1. Instalar as dependências: `pip install pandas openpyxl matplotlib
   seaborn numpy pyarrow scipy statsmodels`.
2. Colocar na raiz os arquivos anuais do SIH (excluídos deste
   repositório pelo tamanho; ver a nota abaixo).
3. Rodar, nesta ordem: `python analise_sih.py`, depois
   `python construir_painel_definitivo.py`, depois
   `python analise_exploratoria.py`.
4. Para o documento: subir `analises/latex/principal.tex`, a pasta
   `analises/latex/secoes` e a pasta
   `analises/figuras_analise_exploratoria` no Overleaf e compilar duas
   vezes com pdfLaTeX.

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
estrutural do escore de complexidade (salvaguarda de circularidade). A
categoria Privado tem 3 CNES e não admite leitura de efeito médio.
