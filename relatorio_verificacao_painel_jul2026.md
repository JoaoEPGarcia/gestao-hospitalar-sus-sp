# Relatório de Verificação do Painel Analítico Definitivo — jul/2026

**Projeto:** Modelos de gestão hospitalar e desempenho — rede SUS/SP, 2015–2025
**Data da execução:** 02–03/07/2026
**Escopo:** aplicação das duas correções de código (CHANGE 1 e CHANGE 2), reexecução integral do pipeline e verificação exaustiva do painel resultante (`analises/painel_definitivo.csv`), com comparação contra a cópia pré-patch (`analises/painel_definitivo_ANTES.csv`).
**Ferramentas:** `verificacao_pos_patch.py` (bateria de 36 checks com PASS/FALHA) + saídas de console de `analise_sih.py`, `construir_painel_definitivo.py`, `verificacoes_painel_definitivo.py` e `diagnostico_painel_definitivo.py`.

**Resultado global: 34 PASS / 2 FALHA (ambas explicadas e sem impacto na integridade — ver "Discrepâncias").**

---

## 0. Mudanças aplicadas e UM DESVIO IMPORTANTE em relação ao resumo

### CHANGE 1 — `analise_sih.py` (classificação assistencial de 2025)

Aplicada conforme especificado — `construir_indice_colunas` ganhou o parâmetro `preferir_ultima` (frozenset) e `processar_arquivo_sih` passa `{"Classificação assistencial"}` somente quando `ano == 2025`; textos do item D2 e do `MAPA_VARIACOES` atualizados. **Porém o mecanismo descrito no resumo era insuficiente, e isso precisa ficar registrado:**

> **DESVIO DOCUMENTADO:** a coluna da posição ~38 do arquivo de 2025 ("Classificação Assistencial") **não é uma coluna por linha** — é uma **tabela de lookup embutida nas primeiras 637 linhas de produção** (pares CNES na posição 37 → rótulo na posição 38), conforme já registrado na inspeção de junho (`_resultado_2025.txt`: "pos37 não-None em qualquer linha: 637"). Nas linhas-resumo — as únicas de onde o pipeline lê `class_assistencial` — a posição 38 vem `None`.
>
> **Evidência da falha do mecanismo literal:** com apenas `preferir_ultima`, o primeiro re-stream produziu `class_assistencial` de 2025 = **NaN em 637/637 CNES** no painel bruto e **314/314** no definitivo (verificado com script auxiliar antes de qualquer decisão).
>
> **Complemento aplicado (ainda dentro do escopo da CHANGE 1):** em `processar_arquivo_sih`, quando `ano == 2025`, os pares (posição 37 → posição 38) são acumulados durante o streaming e o rótulo da linha-resumo é atribuído por CNES ao final ("D2/2025: lookup CNES→classificação com 637 pares; 637/637 CNES do resumo com rótulo atribuído"). Nenhuma outra lógica foi alterada.

### CHANGE 2 — `construir_painel_definitivo.py` (ETAPA E)

Aplicada exatamente como especificado: nova função `etapa_sem_barcelona(painel, aud, df_classif)` chamada no `main()` logo após `etapa_d_balanceado` e antes de `calcular_escores_complexidade`, via `aud.aplicar_filtro` com rótulo **"ETAPA E"**; `AVISO_PROXY` e LEIA-ME atualizados ((i) 3 CNES excluídos; (ii) `modelo_gestao_proxy` = categorias de `class_assistencial` como definição adotada, sem desmembrar PPP/Autarquia, com "Público Municipal" como dummy única). `CNES_SEM_MODELO_GESTAO` permaneceu `set()` vazio, e a ocupação não foi tocada.

### Reexecução

Cache `painel_hospital_ano.*` apagado e pipeline reexecutado duas vezes na parte 1 (a segunda após o complemento do lookup): `analise_sih.py` → 830 CNES × 11 anos = **7.016 linhas** (908.413 linhas de produção só em 2025); `construir_painel_definitivo.py` → funil íntegro (abaixo); `verificacoes_painel_definitivo.py` e `diagnostico_painel_definitivo.py` sem erros (exit 0). Observação de ambiente: o parquet do painel **bruto** não foi gravado ("pyarrow indisponível" — fallback CSV, mesmo estado do artefato pré-patch); o `painel_definitivo.parquet` foi gravado normalmente.

---

## 1. Correção de 2025 (CHANGE 1) — o ponto mais importante

**Nº de valores distintos de `class_assistencial` em 2025 (excluindo NaN):**

| Painel | Valores distintos | Distribuição (2025) |
|---|---|---|
| ANTES (317 CNES) | **5** | Filantrópico 187; Público Municipal 60; OSS 39; Direta 28; Privado 3 |
| DEPOIS (314 CNES) | **5** | Filantrópico 187; Público Municipal 58; OSS 39; Direta 27; Privado 3 |

> **ACHADO CENTRAL (contradiz a hipótese de corrupção): o painel ANTES NÃO era degenerado em 2025.** O artefato entregue já trazia rótulos variando por CNES. A comparação rótulo a rótulo nos **314 CNES comuns** mostra **0 divergências** entre ANTES e DEPOIS em 2025 — a diferença nas contagens (60→58 Público Municipal, 28→27 Direta) é somente a saída dos 3 CNES da ETAPA E.
>
> **Interpretação:** no código antigo, `class_assistencial` era lida da posição 17 **da linha-resumo**, onde o valor já era correto por CNES. A constância da posição 17 observada na inspeção de junho refere-se às primeiras linhas de **produção** (todas 'Público Municipal'), que pertencem aos primeiros CNES do arquivo. A CHANGE 1 permanece válida como blindagem documentada (a fonte agora é o lookup, inequívoco), mas **seu efeito sobre o conteúdo do painel final foi nulo**.

**Check formal:** 2025 DEPOIS não-degenerado (≥2 categorias) e sem NaN → **PASS** (5 categorias, 0 NaN).

**Rótulo de 2025 dos 5 switchers — ANTES × DEPOIS:**

| CNES | ANTES | DEPOIS |
|---|---|---|
| 2081695 | OSS | OSS |
| 2078287 | OSS | OSS |
| 2082225 | OSS | OSS |
| 2091755 | OSS | OSS |
| 2750511 | OSS | OSS |

**Histórico completo 2015–2025 (painel DEPOIS) e coerência com as datas de contrato — 10/10 checks PASS:**

| CNES | Contrato | Proxy | Histórico |
|---|---|---|---|
| 2081695 | OSS desde nov/2018 | 2019 | Direta 2015–2018; **OSS 2019–2025** ✓ |
| 2078287 | OSS desde set/2022 | 2023 | Direta 2015–2022; **OSS 2023–2025** ✓ |
| 2082225 | OSS desde 01/09/2024 | 2025 | Direta 2015–2024; **OSS 2025** ✓ |
| 2091755 | OSS desde 01/09/2024 | 2025 | Direta 2015–2024; **OSS 2025** ✓ |
| 2750511 | OSS desde jan/2025 | 2025 | Direta 2015–2024; **OSS 2025** ✓ |

Para cada switcher: todos os anos ≥ proxy são "OSS" (PASS) e nenhum ano < proxy é "OSS" (PASS). Os 5 estão PRESENTES no painel final com 11/11 anos (V1 do `verificacoes_painel_definitivo.py`).

---

## 2. Dimensões do painel

- `nunique(cnes)` = **314** (esperado 314) → **PASS**
- Nº de linhas = **3.454** (esperado 3.454) → **PASS**
- Balanceamento: **0** CNES com nº de anos ≠ 11 → **PASS**

**Funil reproduzido de `tab_auditoria_filtros.csv`:**

| Etapa | Critério | CNES rem. | Obs rem. | CNES rest. | Obs rest. |
|---|---|---:|---:|---:|---:|
| ETAPA 0 | painel bruto (sem filtros) | 0 | 0 | 830 | 7.016 |
| ETAPA A | tipo (hosp. dia 62 / psiq. 07+006 / CAPS 70) | 76 | 646 | 754 | 6.370 |
| ETAPA B | porte: mediana total_leitos > 50 | 349 | 2.538 | 405 | 3.832 |
| ETAPA C1 | hospitais de campanha COVID | 6 | 9 | 399 | 3.823 |
| ETAPA C2 | remoção do cód. 999 dos indicadores (613 hospital-ano afetados; 6,7% da produção do biênio; nenhuma linha removida) | 0 | 0 | 399 | 3.823 |
| ETAPA D | painel balanceado (11 anos) | 82 | 336 | 317 | 3.487 |
| **ETAPA E** | **sem pontuação de Barcelona** | **3** | **33** | **314** | **3.454** |

Checks da ETAPA E: −3 CNES → **PASS**; −33 obs → **PASS**; 314 restantes → **PASS**; 3.454 restantes → **PASS**.

**Os 3 CNES excluídos (categoria modal de `class_assistencial` no painel ANTES; rótulo estável em 11/11 anos):**

| CNES | Categoria modal | Presença no DEPOIS |
|---|---|---|
| 2042894 | Público Municipal (11/11) | 0 linhas → PASS |
| 2078031 | Direta (11/11) | 0 linhas → PASS |
| 2082209 | Público Municipal (11/11) | 0 linhas → PASS |

---

## 3. Distribuição por `modelo_gestao_proxy` (painel de 314, 2025 corrigido)

**Contagens** (um CNES pode contar em duas categorias se o rótulo mudou entre anos — é o caso dos 5 switchers, contados em Direta e em OSS; por isso a soma de `n_cnes` é 319 = 314 + 5):

| Categoria | Nº CNES | Hospital-ano |
|---|---:|---:|
| Filantrópico | 187 | 2.057 |
| Público Municipal | 58 | 638 |
| OSS | 39 | 387 |
| Direta | 32 | 339 |
| Privado | 3 | 33 |
| **Total** | — | **3.454** (0 NaN) |

**Medianas dos 5 indicadores por categoria (todos os anos):**

| Categoria | mort_all | mort_sem_excl | tmp | custo_saida (R$) | pct_alta_complex |
|---|---:|---:|---:|---:|---:|
| Direta | 0,0475 | 0,0475 | 6,067 | 1.192,67 | 0,0088 |
| Filantrópico | 0,0545 | 0,0545 | 4,111 | 1.086,13 | 0,0011 |
| OSS | 0,0493 | 0,0492 | 4,854 | 1.147,39 | 0,0242 |
| Privado | 0,0256 | 0,0256 | 4,244 | 12.798,36 | 0,9836 |
| Público Municipal | 0,0564 | 0,0564 | 4,768 | 978,96 | 0,0010 |

(A categoria "Privado", n=3, inclui o HU-UFSCar por decisão de agrupamento da equipe; seus valores extremos de custo e alta complexidade refletem o perfil de nicho dos 3 hospitais — coeficientes desse grupo não são interpretáveis como efeito médio, conforme LEIA-ME.)

Arquivos gravados: `tab_pospatch_contagem_por_modelo.csv`, `tab_pospatch_medianas_por_modelo.csv` (além de `tab_def_por_modelo_gestao.csv` do diagnóstico).

## 4. Complexidade

- NaN em `complexidade_estrutural`: **0** (esperado 0) → **PASS** — a ETAPA E cumpriu seu propósito.
- Spearman(`complexidade_estrutural`, `complexidade_pond_mort`) = **0,9256** (referência ~0,926; tolerância ±0,02) → **PASS**.
- Distribuição por `faixa_barcelona` (nº de CNES): **2: 49 | 3: 134 | 4: 106 | 5: 15 | 6: 10**, soma **314** — exatamente o esperado → **PASS** (2 checks).

## 5. Ocupação (decisão de distribuição na modelagem)

| Métrica | ocupacao_internacao | ocupacao_uti |
|---|---:|---:|
| Escala detectada | **percentual [0,100]** | **percentual [0,100]** |
| n (NaN) | 3.454 (0) | 3.454 (0) |
| p50 | 73,46 | 67,15 |
| p90 | 103,83 | 96,10 |
| p95 | 109,11 | 101,33 |
| p99 | 124,19 | 164,16 |
| máximo | 236,61 | **875,21** |
| obs. > 100% | **509 (14,74%)** | **209 (6,05%)** |
| obs. = 0 | 0 (0,00%) | **881 (25,51%)** |

**Recomendação empírica: Gamma ou LogNormal sobre a razão de ocupação** — a fração acima de 100% NÃO é desprezível (14,74% na internação), o que inviabiliza a Beta no suporte (0,1) sem truncamento arbitrário. Atenção adicional para a UTI: 25,51% de zeros (hospitais sem UTI ou sem diárias de UTI no ano) exigem componente de massa em zero (hurdle/two-part) ou restrição da amostra a hospitais com UTI; e o máximo de 875% sugere erro de denominador em casos isolados — vale inspeção dos extremos antes da modelagem.

## 6. Descritivas gerais (314 hospitais) × referências do painel de 317

| Indicador | Mediana | q25 | q75 | Mediana ANTES | Referência | Dif. rel. | Check |
|---|---:|---:|---:|---:|---:|---:|---|
| mort_all | 0,0536 | 0,0300 | 0,0697 | 0,0535 | ~0,0535 | +0,12% | PASS |
| mort_sem_excl | 0,0535 | 0,0300 | 0,0697 | 0,0534 | ~0,0534 | +0,20% | PASS |
| tmp | 4,4214 | 3,5077 | 5,7590 | 4,4245 | ~4,42 | +0,03% | PASS |
| custo_saida | 1.071,27 | 735,49 | 1.733,27 | 1.064,68 | ~1.064,68 | +0,62% | PASS |
| pct_alta_complex | 0,0020 | 0,0000 | 0,0826 | 0,0017 | ~0,0017 | **+15,80%** | **FALHA (explicada)** |

A "FALHA" de `pct_alta_complex` é um **efeito composicional esperado e verificado da ETAPA E**, não um erro: as 33 observações dos 3 CNES excluídos estavam **todas (33/33)** abaixo da mediana geral (medianas por CNES = 0,0 nos três; máximo 0,00083), e retirar massa abaixo da mediana desloca a mediana para cima. Em termos absolutos a mudança é de +0,0003 (0,17% → 0,20% de alta complexidade), num indicador com q25 = 0. Os outros 4 indicadores variaram menos de 1%.

## 7. Integridade

- Duplicatas de (cnes, ano): **0** → **PASS**
- Faixas: mort_all em [0,1]: **0 violações** (PASS); mort_sem_excl em [0,1]: **0** (PASS); custo_saida > 0: **0** (PASS); pct_alta_complex em [0,1]: **0** (PASS); **tmp > 0: 1 violação → FALHA (explicada)**.
  - A violação é `tmp = 0` no CNES **2097613, ano 2021**: hospital com apenas 4 saídas no ano, 1 delas COVID; os 6 dias de permanência do ano eram todos da saída COVID, então a versão sem-COVID ficou com qtde=3 e dias=0 → tmp=0. **O caso já existia no painel ANTES (tmp=0 idêntico)** — não foi introduzido pelo patch. É um alerta útil para a modelagem: nos anos 2020–2021, hospitais quase totalmente COVID têm denominadores sem-COVID minúsculos.
- NaN por coluna: mort_all **0**; mort_sem_excl **0**; tmp **0**; custo_saida **0**; pct_alta_complex **0**; modelo_gestao_proxy **0**; complexidade_estrutural **0**; faixa_barcelona **0**.

## 8. COVID

**Peso do código 999 na produção (painel bruto, 830 CNES):**

| Período | % da qtde | % do valor | qtde_covid |
|---|---:|---:|---:|
| 2020 | 4,99% | 16,07% | 113.029 de 2.264.895 |
| 2021 | 10,69% | 34,88% | 253.978 de 2.376.689 |
| Biênio | 7,91% | 26,81% | 367.007 de 4.641.584 |

**Hospitais de campanha excluídos (ETAPA C1): 6 CNES** — 102083 (Anhembi P38, produção só 2020), 104795 (Vitória, 2020–21), 105759 (Urgência, 2020–21), 105856 (SER, 2020), 109746 (Pedro Dell Antonia, 2020–21), 113123 (Anhembi P35, 2020). Três deles fora do critério literal de classe (regra ampliada D-C1, rastreada no log). Outros 17 candidatos com produção fora do biênio foram mantidos e estão em `tab_revisao_manual_para_decisao.csv` para decisão da equipe.

No painel definitivo, a ETAPA C2 subtraiu numeradores e denominadores COVID dos indicadores em **613 hospital-ano** de 2020–2021 (6,7% da produção do biênio dos hospitais remanescentes), sem remover linhas.

---

## Discrepâncias encontradas

1. **[IMPORTANTE — premissa do enunciado] O mecanismo literal da CHANGE 1 (`preferir_ultima` sozinho) produziu NaN em 2025 (637/637 CNES no bruto; 314/314 no definitivo)**, porque a posição ~38 é tabela de lookup nas primeiras 637 linhas de produção, e não coluna por linha. Foi complementado, dentro do escopo da CHANGE 1, com a atribuição do rótulo por CNES via lookup (pos37→pos38); após o complemento, 637/637 CNES receberam rótulo. O `alteracoes_codigo_jul2026.md` citado no enunciado **não estava no repositório** — se a versão íntegra do documento previa esse join, o desvio é apenas em relação ao resumo.
2. **[IMPORTANTE — hipótese de corrupção refutada] O painel ANTES NÃO era degenerado em 2025**: 5 categorias, mesmos rótulos por CNES que o DEPOIS (0 divergências em 314 CNES comuns), switchers já OSS em 2025. O artefato entregue não estava corrompido nesse quesito; o efeito líquido da CHANGE 1 sobre o conteúdo do painel foi **nulo** (a mudança vale como blindagem/documentação da fonte correta).
3. **Mediana de `pct_alta_complex` subiu 15,8% em termos relativos (0,0017 → 0,0020)** — efeito composicional mecânico da ETAPA E (33/33 obs dos 3 CNES excluídos abaixo da mediana geral); +0,0003 em termos absolutos. Demais indicadores: variação < 1% vs. referência.
4. **1 observação com `tmp = 0`** (CNES 2097613, 2021; qtde_sem_covid=3, dias_sem_covid=0) — pré-existente ao patch; artefato da subtração COVID em hospital de volume mínimo no ano. Relevante para a estratégia de modelagem de 2020–2021.
5. **Ocupação**: escala percentual (não fração); 14,74% (internação) e 6,05% (UTI) das obs acima de 100%; UTI com 25,51% de zeros e máximo implausível de 875% — recomenda-se Gamma/LogNormal (com tratamento de zeros na UTI) e inspeção dos extremos.
6. **Ambiente**: o cache bruto foi salvo apenas como CSV ("pyarrow indisponível" no `to_parquet` do painel bruto; o `painel_definitivo.parquet` foi gravado normalmente) — mesmo comportamento do estado pré-patch; sem impacto nos resultados.
7. **Textos fora do escopo não atualizados** (deliberadamente, para não violar a regra de mudança mínima): o título do bloco [1] de `diagnostico_painel_definitivo.py` ainda imprime "317 hospitais × 11 anos" (o dado real impresso na carga é 314/3.454), a figura figD05 rotula "Definitivo (317 CNES…)", e a nota `NOTA_PROXY_FIG` do diagnóstico ainda usa a redação antiga de "proxy provisório". São strings cosméticas; atualizá-las requer decisão do responsável pelo script. **[Atualização jul/2026 — faxina de reprodutibilidade: as strings de `diagnostico_painel_definitivo.py` foram atualizadas (docstring → 314/3.454; rótulos "PROXY PROVISÓRIO" → "definição adotada"). O rótulo da figD05 ("Definitivo (314 CNES…)") e a nota `NOTA_PROXY_FIG` já estavam corretos no código na data desta verificação.]**

## Veredito

**SIM — o painel de 314 hospitais × 11 anos (3.454 hospital-ano) está íntegro e pronto para a análise exploratória definitiva e os testes econométricos**, com base em: dimensões e balanceamento exatos (314/3.454, 11 anos por CNES, 0 duplicatas), funil de auditoria reproduzido com a ETAPA E (−3/−33), rótulos de gestão completos (0 NaN em `modelo_gestao_proxy`, transições dos 5 switchers coerentes com as datas de contrato), complexidade sem NaN com faixas 49/134/106/15/10 e Spearman 0,9256, e indicadores dentro das faixas válidas.

**Ressalvas para quem for modelar:**
1. Ocupação em escala percentual, com massa relevante acima de 100% (e 25,5% de zeros na UTI) → preferir Gamma/LogNormal, com tratamento de zeros e auditoria dos extremos (máx. 875% na UTI).
2. 1 obs com tmp=0 (2097613/2021) e, em geral, denominadores sem-COVID pequenos em 2020–2021 para hospitais muito "covidizados".
3. Mediana de `pct_alta_complex` deslocada (+0,0003) pela ETAPA E — usar as descritivas novas, não as do painel de 317.
4. Categoria "Privado" tem n=3 (inclui HU-UFSCar por agrupamento pragmático) — coeficientes não interpretáveis como efeito médio.
5. Dos 5 switchers, 3 têm apenas 1 ano de pós-tratamento (2025), limitando a identificação within-hospital (limitação já registrada no LEIA-ME).
