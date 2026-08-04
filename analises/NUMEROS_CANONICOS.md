# Números canônicos do relatório

Instrumento de auditoria criado em 27/07/2026. Lista os valores que
**aparecem em mais de uma seção** do `analises/latex/principal.tex`, com
a sua fonte, a base de leitura e a completude do reporte.

Serve para impedir que renasçam três defeitos já corrigidos: o mesmo
número impresso com valores diferentes em seções distintas, o mesmo
indicador lido em bases diferentes sem rótulo, e a tabela-fonte que
contém mais linhas do que o texto reporta.

**Como usar:** antes de alterar qualquer número do relatório, procure-o
aqui. Se ele estiver listado, a alteração precisa alcançar **todas** as
seções da coluna "Seções". Ao acrescentar um número novo que apareça em
duas ou mais seções, acrescente a linha aqui.

## Legenda das colunas

- **BASE** — para valores monetários: `corrente` (reais do próprio ano)
  ou `real` (deflacionado pelo IPCA para R$ de dez/2025). `—` para
  valores não monetários.
- **Fonte/citadas** — número de linhas de resultado na tabela-fonte
  contra o número efetivamente reportado no texto. Divergência exige
  justificativa explícita (nota de rodapé remetendo à tabela completa).

---

## 1. Painel

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| 289 | hospitais do painel | 1, 2, 4, 12, 16, 17 | — | `painel_definitivo.csv` | — |
| 3.179 | observações hospital-ano | 1, 2, 3, 17 | — | idem | — |
| 3.178 | exclui o TMP zero | 3, Ap. A | — | idem | — |
| 3.177 | exclui os 2 denominadores frágeis | 3, 15 | — | idem | — |
| 2.482 | observações com UTI ativa | 3, 14 | — | idem | — |
| 284 | hospitais nunca convertidos | 12, 14 | — | idem | — |
| 830 | estabelecimentos da base bruta | 1, 17 | — | `tab_auditoria_filtros.csv` | — |
| 25 | CNES excluídos na ETAPA F | 1, 14 | — | `tab_auditoria_cnes_removidos.csv` | — |
| 171 / 56 / 37 / 27 / 3 | hospitais por categoria (por período) | 4 | — | `tab_ae_por_categoria.csv` | — |
| 159 / 120 / 10 | hospitais por porte | 1, 5 | — | `tab_ae_por_porte.csv` | — |

## 1b. As duas leituras de cada categoria (01/08/2026)

A Seção 4 passou a publicar **mediana, média e agregado** de cada rede,
porque a mediana sozinha descrevia mal categorias muito desiguais por
dentro. As três respondem perguntas diferentes e **não são intercambiáveis**:
a mediana é o hospital do meio da fila, a média é a média das taxas dos
hospitais, e o agregado é a taxa da rede (soma dos numeradores sobre soma
dos denominadores, na base sem COVID). Quem trocar uma pela outra erra por
ordens de grandeza: no Filantrópico, a fração de alta complexidade vale
0,0018 pela mediana e 0,1403 pelo agregado, distância de 78 vezes.

**Correção de 04/08/2026, apanhada por João pelo negrito da tabela.** A
Seção 4 afirmava que a média de alta complexidade do Filantrópico (0,0831)
era "a maior entre as quatro redes públicas e filantrópicas". **Não é**: a
da administração Direta é 0,0893. É pela **média agregada** que o
Filantrópico lidera (0,1403), e é essa a leitura que sustenta o argumento
da subseção. O texto passou a afirmar o que de fato distingue a rede
filantrópica na coluna da média: a distância entre média e mediana, de
**45,9 vezes**, contra 4,2 na Direta, 2,8 nas OSS e 21,9 no Município ---
a maior da tabela. Lição de auditoria: **negrito é afirmação**, e
afirmação sem dono numa tabela é onde o erro se esconde.

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| 0,0018 / 0,0831 / **0,1403** | alta complexidade do Filantrópico: mediana / média / agregado | 4 | — | `tab_ae_por_categoria.csv` e `tab_ae_por_categoria_agregado.csv` | 3/3 |
| 0,0213 / **0,0893** / 0,1026 | idem, administração Direta | 4 | — | idem | 3/3 |
| 0,0242 / 0,0672 / 0,0737 | idem, OSS | 4 | — | idem | 3/3 |
| **71,0%** | fatia do Filantrópico na alta complexidade do painel | 4 | — | `tab_ae_por_categoria_agregado.csv` | — |
| **51,9%** | fatia do Filantrópico nos leitos de UTI SUS | 4 | — | idem | — |
| 80,2 / 80,9 | ocupação de UTI do Filantrópico: mediana / média | 4 | — | `tab_ae_por_categoria.csv` | — |

## 1c. A produção não alta complexidade (01/08/2026)

O documento descrevia a alta complexidade, que é 9,9% das internações, e
não dizia nada sobre os outros 90,1%. **O painel não separa média
complexidade de atenção básica**: ele guarda `qtde_alta_complex` e `qtde`,
e tudo o mais sai por diferença. Por isso o rótulo canônico é
**produção não alta**, nunca "média complexidade".

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| **20,8 milhões** | internações não alta complexidade (90,1% do painel) | 5 | — | `painel_definitivo.csv` | — |
| 96,5 / 89,9 / 77,0 | % da produção não alta, por porte | 5 | — | `tab_ae_media_complexidade.csv` | 3/3 |
| **35** | hospitais que nunca registram alta complexidade em 11 anos | 2, 5, Ap. D | — | idem | — |
| 33 / 2 / 0 | idem, por porte | 5 | — | idem | 3/3 |
| 22 / 7 / 4 / 2 | idem, por rede: Filantrópico, Município, Direta, OSS | 5, Ap. D | — | `tab_ap_sem_alta_complexidade.csv` | 4/4 |
| 133 | hospitais com **ao menos um** ano sem alta complexidade | Ap. D | — | idem | — |
| 61,9 / 59,3 / 51,3 / 39,1 | internações não alta por leito SUS: OSS, Município, Filantrópico, Direta | 5 | — | `painel_definitivo.csv` | 4/4 |

## 1d. Unidade dos deslocamentos de taxa (decisão de 01/08/2026)

`p.p.` e "ponto percentual" **não aparecem mais no documento**. Onde o
modelo estima deslocamento de uma taxa, o texto imprime **o par de taxas em
%**, com a base declarada. Ao alterar qualquer um destes, altere o par
inteiro, nunca só uma ponta.

| Par publicado | Deslocamento subjacente | Base | Seções |
|---|---|---|---|
| de 5,8% para 4,6% | −1,16 na escala da taxa | média da Direta | 11 |
| de 8,9% para 7,6% | −1,31 na escala da taxa | média da Direta | 11 |
| de 6,1% para 4,8% / 3,5% / 3,2% / 3,9% | −1,30 / −2,64 / −2,91 / −2,23 | média pré-conversão dos 5 | 12 |
| de 7,7% para 5,7% | −2,05 na escala da taxa | média pré dos 3 do suporte comum | 12 |
| de 5,6% para 4,3% | −1,3 na escala da taxa | mediana do painel | 16 |
| de 76,8% para 51,0% | −25,8 na escala da taxa | ocupação do ano cheio seguinte | 15 |
| de 5,6% para 4,4% | −1,18 na escala da taxa | média da Direta **sem 2020–21** | 13 |
| de 8,9% para 7,7% | −1,25 na escala da taxa | média da Direta **sem 2020–21** | 13 |

Os dois últimos pares entraram em 04/08/2026, quando a Tabela 9 da Seção 13
ganhou coluna de efeito legível ao lado do coeficiente bruto. **A taxa de
partida muda com a amostra**: a média de mortalidade da Direta é 5,79% no
painel inteiro e 5,58% sem o biênio, e é por isso que o par sem pandemia não
é o mesmo do painel completo. Fonte: `auditar_efeitos_robustez.py` para o
deslocamento e `painel_definitivo.csv` para a base.

## 1e. A ausência de UTI é estrutural, não intermitente (04/08/2026)

O documento publicava as 688 observações sem leito de UTI do SUS (21,6%)
sem dizer se elas vêm sempre dos mesmos hospitais ou de um cadastro que
oscila. **Vêm quase todas dos mesmos**: 539 das 688 são dos 49 hospitais
que nunca tiveram UTI do SUS em nenhum dos onze anos. É isso que justifica
tratá-las como *não-aplicável* e não como ocupação zero, e o Apêndice D
nomeia os 49 um a um. Ao alterar qualquer linha desta tabela, altere também
a Seção 2 e o Apêndice D, que citam os mesmos valores.

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| **688 (21,6%)** | observações sem leito de UTI SUS cadastrado | 2, 4, Ap. D | — | `painel_definitivo.csv` | — |
| **49** | hospitais **sem** UTI SUS nos 11 anos (539 observações) | 2, Ap. D | — | `tab_ap_sem_uti_sus.csv` | — |
| 211 / 29 | hospitais **com** UTI nos 11 anos / que oscilam (149 obs) | Ap. D | — | idem | — |
| 42 / 5 / 1 / 1 | os 49 por rede: Filantrópico, Município, Direta, OSS | Ap. D | — | idem | 4/4 |
| 6 / 23 | dos 49: com UTI não SUS / também sem alta complexidade | Ap. D | — | `listas_estruturais.py` | — |

Fonte das duas listas do Apêndice D: `analises/listas_estruturais.py`, que
também reconfere os totais por estrato citados no Sumário Executivo.

## 2. Contraste OSS × Direta (modelos principais)

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| **43,7%** | produção maior | 11, 13, 15, 16, 17 | — | `tab_est_resumo_oss.csv` | 7/7 |
| **22,7%** | ocupação de internação maior | 11, 13 | — | idem | 7/7 |
| **19,3%** | uso de UTI maior — **valor canônico** | 11, 13, 14, 17 | — | `tab_est_ocup_uti_gama.csv` | 3/3 |
| 22,8% | uso de UTI, especificação log **superada** | 11 (nota), 14 | — | `tab_est_uti_alternativas.csv` | 3/3 |
| 23,3% | uso de UTI, variante de corte mínimo | 14 | — | idem | 3/3 |
| **10,2%** | queda do TMP | 11, 13, 14, 15, 16, 17 | — | `tab_est_resumo_oss.csv` | 7/7 |
| **8,3%** | queda do faturamento (não significativa) | 11 | real | idem | 7/7 |
| **1,16 p.p.** | efeito marginal na mortalidade | 11, 13 | — | idem | 7/7 |
| **1,31 p.p.** | efeito marginal na fração de alta complexidade (não significativo, $z$ de $-0{,}87$) | 11, 13 | — | `auditar_efeitos_robustez.py` | 7/7 |
| 11,4% / 44,7% | TMP e produção sem 2020–21 | 13 | — | `tab_est_robustez_sem_pandemia.csv` | 7/7 |
| 8,0% / 22,3% / 24,3% | faturamento, ocupação e UTI sem 2020–21 | 13 | real (faturamento) | idem | 7/7 |
| 1,18 / 1,25 p.p. | mortalidade e alta complexidade sem 2020–21 | 13 | — | `auditar_efeitos_robustez.py` | 7/7 |

## 3. Estudo de eventos e inferência

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| 1,30 / 2,64 / 2,91 / 2,23 p.p. | mortalidade por janela (TWFE) | 12, 14 | — | `tab_est_cs_evento.csv` | 20/8 † |
| 24,6% | queda do TMP na janela longa | 12 | — | idem | 20/8 † |
| 13,5% | queda do faturamento na janela longa | 12 | real | idem | 20/8 † |
| **0,254** | p do teste de tendências paralelas, TMP | 12, 14, 17 | — | `tab_est_tendencias_paralelas.csv` | 10/10 |
| 0,229 / 0,046 / <0,001 | idem, demais indicadores | 12 | — | idem | 10/10 |
| **0,153** | p da permutação, TMP | 11, 14, 17 | — | `tab_est_permutacao.csv` | 2/2 |
| 0,395 (40%) | p da permutação, faturamento | 12, 14 | real | idem | 2/2 |
| **0,324** | p do bootstrap selvagem, TMP | 14, 17 | — | `tab_est_wild_bootstrap.csv` | 2/2 |
| **0,597** | p do bootstrap selvagem, faturamento | 14 | real | idem | 2/2 |
| 1,296 / 1,293 | mortalidade no ano zero, TWFE × CS | 14 | — | `tab_est_cs_evento.csv` | 20/8 † |

† Reporte parcial **por decisão**, com nota de rodapé remetendo à tabela
completa. As linhas não citadas apontam na mesma direção das citadas.

## 4. Controle sintético — as seis linhas

| Hospital | Indicador | Lacuna | RMSPE pré | p | Seções | BASE |
|---|---|---|---|---|---|---|
| Sorocaba | mortalidade | −0,54 p.p. | 0,00 | 0,67 | 14, 17 | — |
| Sorocaba | permanência | −0,24 dias | 0,00 | 0,78 | 14, 17 | — |
| Sorocaba | faturamento | −56,38 | 0,00 | 0,75 | 14 | real |
| Pérola | mortalidade | −1,06 p.p. | 0,29 | 0,32 | 14, 17 | — |
| Pérola | permanência | −0,13 dias | 0,00 | 0,75 | 14, 17 | — |
| Pérola | faturamento | −353,92 | 0,00 | 0,25 | 14 | real |

Fonte: `tab_est_sintetico.csv`. **6/6** desde 27/07/2026 (eram 3/6).

## 5. Fase 2 — hierárquico e eficiência

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| **0,262** | mortalidade no logito, hierárquico (≈1,3 p.p.) | 14, 15, 17 | — | `tabR_frente1_variantes.csv` | 24/8 ‡ |
| **0,003** | mortalidade sem os conversores (nulo) | 14, 15, 17 | — | idem | 24/8 ‡ |
| 0,281 / 0,492 / 0,235 | TMP, produção, ocupação sem conversores | 15 | — | idem | 24/8 ‡ |
| **0,293** | eficiência, 2ª etapa (≈25% menos distância) | 15, 17 | — | `tabE_segunda_etapa_log.csv` | 4/4 |
| 0,272 / 0,331 / 0,319 | idem, três variantes | 15, 17 | — | idem | 4/4 |
| 0,733 / 0,634 / 0,632 / 0,595 | medianas DEA por categoria | 15, 0 | — | `dea_escores_principal.csv` | — |
| 0,51 / 0,48 | correlação financeira × só leitos | 15 | — | `dea_escores_so_leitos.csv` | — |
| 55 / 51 / 36 / 35 | saídas por leito por categoria | 15, 17 | — | `painel_definitivo.csv` | — |

‡ Escopo declarado: a Seção 15 anuncia que o pacote completo está em
`resultados_fase2/`, e o `RELATORIO_EXECUCAO.md` reporta as variantes.

## 6. Conversores — antes e depois

Fonte da mortalidade, do TMP e do faturamento:
`tab_ae_conversores_pre_pos.csv`, que desde 27/07/2026 traz o faturamento
apenas na linha `custo_real`. A linha `custo_saida` **nominal**, que
convivia com ela e foi a origem direta da divergência de 2026 (o mesmo
hospital aparecia com +19,3% e com −12,2%), **deixou de ser gerada**:
não há mais como ler a base errada por engano.
`tab_sel_conversores_trajetoria.csv` confere os mesmos valores.

| Hospital | Mortalidade | TMP | Faturamento | Seções | BASE |
|---|---|---|---|---|---|
| Sorocaba | 9,34% → 7,95% (−14,8%) | 8,29 → 7,13 (−14,0%) | 2.734,63 → 2.401,47 (−12,2%) | 7, 16 | **real** |
| Pérola | 7,55% → 4,57% (−39,5%) | 4,12 → 3,40 (−17,5%) | 1.989,40 → 1.423,76 (−28,4%) | 7, 16 | **real** |
| Taipas | 7,90% → 6,47% (−18,1%) | 5,41 → 5,35 (−1,1%) | 869,18 → 977,07 (+12,4%) | 16 | **real** |
| Vila Penteado | 7,48% → 8,31% (+11,1%) | 5,03 → 5,50 (+9,3%) | 940,08 → 1.246,13 (+32,6%) | 16 | **real** |
| P. Prudente | 0,60% → 0,68% (+13,4%) | 3,72 → 3,91 (+5,4%) | 1.132,81 → 1.082,27 (−4,5%) | 16 | **real** |

## 7. Valores monetários descritivos — base por seção

| Seção | O que imprime | BASE | Rotulado? |
|---|---|---|---|
| 2 | mediana 1.327,62, média 1.833,34, máx 41.996,85 | **real** | sim, desde 27/07/2026 |
| 4 | medianas por categoria (1.293 a 1.438; Privado 16.262) | **real** | sim |
| 5 | 631 → 3.780 (faixa); 1.035 / 1.806 / 3.831 (porte) | **real** | sim |
| 6 | 866 → 1.283 nominal; 1.427 → 1.283 real; tabela IPCA | **ambas** | sim, por desenho |
| 7 | Sorocaba −12,2%; Pérola −28,4% | **real** | sim, desde 27/07/2026 |
| 9 | 90 extremos acima de 5.117,74 | **real** | sim, desde 27/07/2026 |
| 11, 12, 14, 15 | modelos | **real** | sim |
| 16 | conversores | **real** | sim, desde 27/07/2026 |
| A (apêndice) | AIC e r dos cinco moldes do faturamento | **real** | sim, desde 27/07/2026 |

**Fechado em 27/07/2026.** Não há mais valor monetário em base nominal no
documento. A única exceção é a Seção 6, cujo assunto **é** a comparação
entre as duas bases: ali o par nominal × real é o próprio conteúdo, e a
tabela do IPCA declara os dois lados. `tab_ae_univariada.csv` e
`tab_ae_outliers.csv` passaram a ser calculadas sobre `custo_real`.

## 8. Outros valores repetidos

| Valor | Significado | Seções |
|---|---|---|
| 0,926 | Spearman entre as duas versões de complexidade | 1 (nota) |
| 1,000 | correlação entre mortalidade geral e ajustada | 2, 8 |
| 4,5% a 38,2% | faixa da variação *within* | 8, 10 |
| 0,77 | Spearman faturamento × alta complexidade | 8 |
| 31,3% | observações com alta complexidade zero | 2, 3 |
| 15,5% / 21,9% | ocupação >100% e zeros de UTI | 2, 9 |
| 875% | ocupação de UTI máxima (CNES 2022648) | 2, 9, 16 |
| 13 e 4 | saídas não COVID do CNES 2097613 | 9, 10, 16 |
| 0,814 → 0,944 | diagnóstico da UTI antes e depois da Gama | 13, 14, Ap. A |
| 0,976 / 0,991 / 0,967 / 0,970 / 0,952 | resíduos quantílicos | Ap. A |
