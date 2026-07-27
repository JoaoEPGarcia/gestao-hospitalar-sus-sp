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

## 2. Contraste OSS × Direta (modelos principais)

| Valor | Significado | Seções | BASE | Fonte | Fonte/citadas |
|---|---|---|---|---|---|
| **43,7%** | produção maior | 11, 13, 15, 16, 17 | — | `tab_est_resumo_oss.csv` | 7/7 |
| **22,7%** | ocupação de internação maior | 11 | — | idem | 7/7 |
| **19,3%** | uso de UTI maior — **valor canônico** | 11, 14, 17 | — | `tab_est_ocup_uti_gama.csv` | 3/3 |
| 22,8% | uso de UTI, especificação log **superada** | 11 (nota), 14 | — | `tab_est_uti_alternativas.csv` | 3/3 |
| 23,3% | uso de UTI, variante de corte mínimo | 14 | — | idem | 3/3 |
| **10,2%** | queda do TMP | 11, 13, 14, 15, 16, 17 | — | `tab_est_resumo_oss.csv` | 7/7 |
| **8,3%** | queda do faturamento (não significativa) | 11 | real | idem | 7/7 |
| **1,16 p.p.** | efeito marginal na mortalidade | 11, 13 | — | idem | 7/7 |
| 11,4% / 44,7% | TMP e produção sem 2020–21 | 13 | — | `tab_est_robustez_sem_pandemia.csv` | 7/7 |

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
| 0,733 / 0,634 / 0,632 / 0,595 | medianas DEA por categoria | 15 | — | `dea_escores_principal.csv` | — |
| 0,788 / 0,784 | SFA Direta e Filantrópico | 15 | — | `tabS_te_categoria_ano.csv` | — |
| 0,62 / 0,63 | correlação DEA × SFA | 15 | — | `figS02` | — |
| 0,51 / 0,48 | correlação financeira × só leitos | 15 | — | `dea_escores_so_leitos.csv` | — |
| 55 / 51 / 36 / 35 | saídas por leito por categoria | 15, 17 | — | `painel_definitivo.csv` | — |

‡ Escopo declarado: a Seção 15 anuncia que o pacote completo está em
`resultados_fase2/`, e o `RELATORIO_EXECUCAO.md` reporta as variantes.

## 6. Conversores — antes e depois

Fonte da mortalidade e do TMP: `tab_ae_conversores_pre_pos.csv`.
Fonte do faturamento: `tab_sel_conversores_trajetoria.csv`, coluna
`custo_real`. **Atenção:** `tab_ae_conversores_pre_pos.csv` traz também
uma coluna `custo_saida` **nominal**, que não deve ser usada — foi a
origem da divergência de 2026.

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
| 2 | mediana 1.034, média 1.431, máx 27.888 | **corrente** | sim, desde 27/07/2026 |
| 4 | medianas por categoria (1.293 a 1.438; Privado 16.262) | **real** | sim |
| 5 | 631 → 3.780 (faixa); 1.035 / 1.806 / 3.831 (porte) | **real** | sim |
| 6 | 866 → 1.283 nominal; 1.427 → 1.283 real; tabela IPCA | **ambas** | sim, por desenho |
| 7 | — (remete à Seção 16) | — | n/a |
| 9 | 87 extremos acima de 4.223 | **corrente** | sim, desde 27/07/2026 |
| 11, 12, 14, 15 | modelos | **real** | sim |
| 16 | conversores | **real** | sim, desde 27/07/2026 |

**Pendente de pipeline:** as Seções 2 e 9 seguem em valores correntes
porque `tab_ae_univariada.csv` e `tab_ae_outliers.csv` não têm coluna
`custo_real`; convertê-las exige reexecutar `analise_exploratoria.py`.
Ver `PENDENCIAS.md`.

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
