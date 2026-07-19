# Relatório da ETAPA 1 — Revisão da reunião de 13/07/2026

**Caráter:** investigação somente-leitura. Nenhum arquivo do pipeline foi alterado.
**Única exceção autorizada pelo encaminhamento:** registro documental do item 1.9 em `criterios_construcao_painel.md` (§7, novo item 4).
**Scripts de investigação (reprodutíveis):** `_investigacao_etapa1_13jul2026.py` e `_investigacao_etapa1_13jul2026_anexo.py` (ambos apenas leem dados e imprimem no terminal).

---

## 1.1 — Alta complexidade nos Filantrópicos: **não é bug — é confusão entre duas métricas**

**Reprodução do número:** a mediana de `pct_alta_complex` do grupo Filantrópico no painel definitivo é **0,00107 (0,11%)** — bate exatamente com o 0,0011 de `tab_def_por_modelo_gestao.csv` e com o "0,001" citado na reunião.

**Mas a participação estadual bate com o Alberto:** somando internações, os Filantrópicos respondem por **71,0% de toda a alta complexidade do painel definitivo** (1.650.475 de 2.324.945 internações de alta complexidade) e **68,4% na base bruta de 830 CNES** — na prática o mesmo número dos "~75%" citados por ele.

**Por que as duas coisas coexistem:** o grupo Filantrópico tem 187 dos 314 CNES e vai de grandes centros (InCor, Dante Pazzanese, Pio XII/Barretos, Amaral Carvalho...) a pequenas Santas Casas do interior. **41,1% dos hospital-ano filantrópicos têm zero alta complexidade**, o que puxa a mediana para perto de zero; os 10 maiores concentram 50,5% da alta complexidade do grupo. A proporção interna agregada (soma/soma) do grupo é 13,7% — não 0,1%.

**Checagem de bug de junção:** 33 dos 187 CNES filantrópicos não têm nenhuma internação de alta complexidade em 11 anos, mas todos com produção normal (`qtde` > 0 sempre). `qtde_alta_complex` vem do mesmo streaming de produção que `qtde` (não há junção separada que pudesse zerar só esse campo), e o padrão é o esperado para hospitais gerais pequenos. **Hipótese (c) do encaminhamento confirmada: não há bug.**

**Recomendação para a Etapa 2 (ajustada no veredito de 14/07/2026):** não alterar dado nenhum; **trocar a estatística primária**. Em qualquer tabela ou texto que reporte `pct_alta_complex` por `modelo_gestao_proxy`, a **proporção agregada do grupo (soma de alta complexidade ÷ soma de internações)** passa a ser a estatística principal — a mediana interna vira estatística secundária, útil para mostrar a assimetria (41% dos hospital-ano filantrópicos com zero alta complexidade), não como resumo de destaque. Motivo: mediana (0,001) e agregado (0,137) diferem por dois fatores de dez numa variável com 41% de zeros, e foi a mediana em destaque que produziu a confusão da reunião.

---

## 1.2 — "Custo real por saída" → "faturamento": **confirmado que é só nomenclatura**

- `custo_saida = valor / qtde`, onde `valor` = "VALOR TOTAL" da AIH (reembolso SIH). **Nunca houve fonte de custo operacional no pipeline.** A troca é correção de precisão metodológica, não mudança de variável.
- **Não existe** nenhum ponto do pipeline que compare `custo_saida`/`custo_real` com benchmark de custo operacional — o risco apontado no encaminhamento não se materializa.
- Atenção: hoje existem **dois rótulos** em uso: "custo por saída" (nominal, `custo_saida`) e "**custo real** por saída" (`custo_real` = deflacionado pelo IPCA a preços de 2025). A proposta de novos rótulos precisa cobrir os dois — sugestão: **"faturamento por saída (SIH)"** e **"faturamento real por saída (R$ de 2025)"**.
- **Ressalva obrigatória acoplada ao relabeling (veredito de 14/07/2026):** hospitais OSS não são reembolsados por AIH — são custeados por contrato de gestão com orçamento global; o valor de AIH registrado no SIH é, para eles, produção sem consequência financeira direta, com incentivo estruturalmente mais fraco de maximizar o valor registrado por saída. Como "faturamento" soa financeiramente mais concreto que "custo", o novo rótulo **deve vir acompanhado dessa ressalva no mesmo texto** sempre que o número do item 1.7 for citado — não como nota de rodapé isolada. Os itens 1.2 e 1.7 andam juntos: não aplicar um sem o outro.
- **Colunas mantêm os nomes** (`custo_saida`, `custo_real`) por estabilidade de código, salvo decisão em contrário.

**Mapa de ocorrências do rótulo humano (grep reprodutível):**

| Onde | Arquivos |
|---|---|
| Python (dicionários de rótulos e prints) | `analise_sih.py` (ROTULOS), `analise_exploratoria.py` (ROT), `estimacao.py`, `inferencia_robusta.py`, `selecao_entrevistas.py` |
| R (rótulos de tabelas fase 2) | `fase2_bayes.R` ("Custo real por saída (log)") |
| LaTeX | `sec01, 02, 03, 04, 05, 06, 07, 08, 10, 11, 12, 14, 16, 17`, `apendiceA_diagnosticos.tex`, `roteiro_entrevistas.tex` |
| Markdown/relatórios | `analises/estimacao.md`, `analises/analise_exploratoria.md`, `resultados_fase2/RELATORIO_EXECUCAO.md`, `analises/LEIAME_painel_definitivo.txt` |
| CSVs com rótulo embutido (regenerar, não editar) | `tab_est_resumo_oss.csv`, `tab_est_wild_bootstrap.csv`, `tab_est_cs_att.csv`, `tab_est_cs_evento.csv`, `tabB_comparacao_freq_bayes.csv` |
| Figuras com o termo no título/eixo | `fig_ae_01/03/04/05/06/07/08/09_*custo*`, `fig_est_01_evento_custo_real`, `fig_est_03_contraste_oss_direta`, figuras fase 2 |

---

## 1.3 — Ocupação sem 2020–2021: **prévia calculada; efeito pequeno na internação, moderado na UTI**

- Entendimento confirmado: exclusão por **ano civil completo** (linhas de 2020 e 2021), porque o denominador da ocupação não é decomponível por procedimento (LEIA-ME, decisão D-C2). Não há como "remover só o COVID" da ocupação.
- Seriam removidas **628 de 3.454 observações (18,2%)** de cada indicador de ocupação (Filantrópico 374, Público Municipal 116, OSS 70, Direta 62, Privado 6).

Prévia (mediana, completo → sem 2020–2021):

| Categoria | Ocup. internação | Ocup. UTI |
|---|---|---|
| Direta | 62,8 → 63,2 | 57,3 → 55,8 |
| Filantrópico | 68,2 → 68,7 | 66,8 → 65,9 |
| OSS | 91,6 → 92,3 | 73,4 → 72,0 |
| Público Municipal | 87,3 → 89,1 | 69,7 → 67,5 |
| Privado (n=3) | 40,5 → 37,0 | 3,5 → 3,9 |
| **Agregado** | 73,5 → 74,1 | 67,2 → 65,7 |

Nas **médias** de UTI o efeito é maior (53,3 → 50,0 no Filantrópico; agregado 56,8 → 53,2), porque saem os extremos de 2021 (mediana estadual de ocupação de UTI foi 82,9% em 2021 contra 60–72% nos demais anos). **Aguarda aprovação para materializar a tabela definitiva (Etapa 2, item 5 da ordem).**

**Adendo (C4, veredito de 14/07/2026):** a linha do Privado (ocupação de UTI ~3,5%) é produção SUS de UTI **residual**, não erro: Leforte 30 leitos SUS com 595 diárias medianas (5,4%), Unimed Sorocaba 4 leitos SUS (2,2%), HU-UFSCar sem leito de UTI declarado (0%). A tabela definitiva sairá com a ressalva de não-interpretação estampada na própria linha do grupo (n=3).

---

## 1.4 — Gráfico de TMP: **os gráficos citados na reunião já são lineares; o limite de 120 dias é inócuo — não existe TMP acima de 41 dias em lugar nenhum**

- Gráficos que usam TMP em **escala log** hoje (todos da exploratória): `fig_ae_03_hist_log_tmp.png` (eixo X em log) e `fig_ae_04_violino_tmp.png` (eixo Y em log). Os citados no encaminhamento — `fig06_series_temporais`, `fig04_boxplots_por_ano`, `figD01`, `figD02` — **já são lineares**. `extremos_tmp_top10/bottom10.csv` são tabelas, sem escala.
- **Nenhuma observação excede 120 dias**: máximo no painel definitivo = **30,5 dias** (teto da própria base SIH — o achatamento em 30,5 já está documentado na exploratória) e máximo na base bruta = **41,0 dias** (Hospital Dia Irmão Altino, que nem entra no painel definitivo).
- As duas leituras possíveis do "limite fixo em 120":
  - (a) **cortar o eixo Y em 120** — tecnicamente inócuo: o eixo ficaria 4× maior que o dado máximo e *comprimiria* a leitura em vez de melhorá-la;
  - (b) **winsorizar/anotar outliers** — sem objeto: não há outliers acima de 120.
- **Recomendação (a decidir por vocês):** escala linear com teto **fixo em 35 dias** para o painel definitivo (cobre o teto de 30,5 com folga) — ou 45 dias se o gráfico incluir a base bruta — em vez de 120. Se a decisão da reunião for literal, o teto de 120 pode ser aplicado, mas o gráfico perde resolução.
- Confirmado: mudança **apenas de visualização**; a variável `tmp` dos modelos (CRE/Mundlak, Bayes, DEA, SFA) não é tocada.

**Adendo (C2, veredito de 14/07/2026) — o achado principal deste item não é a escala, é a censura:** o teto de ~30,5 dias é **censura à direita** da base, não ausência de outliers. Assinatura: 80 hospital-ano do painel em [30,0; 30,5] e zero acima; na base bruta inteira (7.016 obs), p99,9 = 30,50 e o único estabelecimento que ultrapassa o teto em toda a década é um hospital-dia (tipo 62, regime próprio de AIH, fora do painel). Os ~18 CNES de longa permanência (TMP mediano > 20, incluindo as duas "Casas da Criança" do item 1.10) estão empilhados no teto — o TMP deles mede o teto, não a permanência. **Item retido**: nenhuma decisão de eixo antes da resposta de Alberto sobre a regra de diárias por AIH (Pergunta 1 do memorando de 14/07/2026).

---

## 1.5 — Correção IPCA: **já existe na estimação; falta só na camada descritiva**

- Variáveis monetárias do painel (todas em **R$ correntes**): `valor`, `valor_covid`, `valor_sem_covid`, `custo_saida`, `custo_saida_com_covid` (a mediana anual de `custo_saida` sobe de R$ 908 em 2015 a R$ 1.317 em 2025, confirmando valores correntes).
- **A correção já está implementada e em uso nos modelos:** `custo_real = custo_saida × fator IPCA` (IPCA dez/dez IBGE, base = preços de 2025, série anual fixada no código: 2015 = 10,67% ... 2025 = 4,26%; fator de 2015 = 1,6479) em `estimacao.py`, `analise_exploratoria.py` (fig_ae_07 e `tab_ae_custo_real_ano.csv`) e `resultados_fase2/preparo_fase2.R` (que também deflaciona `valor` → `valor_real`). Toda a Fase 1/Fase 2 de custo já roda sobre `custo_real`.
- **O que NÃO é deflacionado hoje:** a camada descritiva — `tab_def_por_modelo_gestao.csv`, `tab_pospatch_medianas_por_modelo.csv`, `tab_def_descritiva_*`, `figD01–figD05`, violinos e cortes da exploratória (`fig_ae_04/05/06/08`), `tab_ae_por_categoria.csv` etc.
- **Proposta para aprovação:** manter IPCA (não INPC — IPCA é o índice-alvo do regime de metas e o já adotado), dez/dez, **base dez/2025**, fonte IBGE/SIDRA (série 1737) com a série anual fixada em código e auditável (como hoje). Escopo a decidir: aplicar às **tabelas/figuras de apresentação** (os modelos já são reais). Comparação "Barcelona × modelo próprio" não é afetada por deflação (ocupação não é monetária).

---

## 1.6 — Sorocaba (2081695): **não há queda de complexidade observável; o único proxy temporal disponível SOBE no pós-conversão**

**Caveat metodológico central:** `complexidade_estrutural` e `faixa_barcelona` são **fixas por CNES** (planilha única de classificação) — por construção não podem mostrar queda pós-2019. Os únicos sinais de composição que variam no tempo no painel são `pct_alta_complex`, volume e ocupação.

Trajetória do CNES 2081695 (faixa Barcelona 5, complexidade estrutural 675 — constante):

| Período | mort_all | tmp | pct_alta_complex | qtde (sem COVID) | faturamento real 2025 |
|---|---|---|---|---|---|
| 2015–2018 (Direta) | 0,086–0,099 | 8,0–9,1 | 8,4–9,9% | 11,9–13,6 mil | R$ 2.663–2.895 |
| 2019–2025 (OSS) | 0,074–0,091 | 6,4–7,9 | 8,9–**12,4%** | 14,8–**20,2 mil** | R$ 2.200–2.586 |

- A fração de alta complexidade **não cai** — termina 2025 em 12,4%, acima de qualquer ano pré-conversão; o volume cresce ~50% na ponta. **Não há evidência, nos dados disponíveis, de melhora por emagrecimento de case-mix**; se algo, a composição ficou mais pesada.
- **Pérola Byington (2078287, conversão 2023), para comparação:** mort 0,075→0,046, tmp 4,1→3,4, faturamento real 1.989→1.424, volume 5,6 mil→14,0 mil (+151%), e `pct_alta_complex` **cai de 27–34% para 23,7–24,8%** — aqui sim há mudança de composição concomitante (diluição por volume), que deve ser citada como ressalva.
- **"Comparativo de atendimento" — 3 leituras possíveis, escolher uma (ou mais):**
  1. **Volume de saídas** (`qtde_sem_covid`) ano a ano, hospital × mediana da categoria;
  2. **Perfil de complexidade atendida** (`pct_alta_complex`) ano a ano;
  3. **Taxas de ocupação** (internação e UTI) ano a ano.

---

## 1.7 — Os −6,7% no faturamento: **origem localizada; IC95% já existe e cruza zero — nada precisa ser reestimado para reportar**

- **Fonte primária:** `tab_est_custo_fe.csv` (`estimacao.py` — log de `custo_real`, efeitos fixos de hospital e ano, EP agrupado por CNES, n = 3.452): coef OSS = **−0,0696 log-pontos**, EP = 0,095, p = 0,464 → efeito = **−6,73%**, **IC95% = [−22,6%, +12,4%]**. Já descrito por extenso em `analises/estimacao.md`.
- Réplicas do mesmo número: `tab_est_resumo_oss.csv` (efeito_pct −6,72); `tabB_comparacao_freq_bayes.csv` (hierárquico bayesiano: −0,0696 ± 0,0604, IC [−17,1%, +5,0%]); `tabR_frente1_variantes.csv` (CRE/Mundlak: −6,7%, IC [−17,1%, +5,0%]; sem_pandemia −6,3%; sem_switchers −17,1% com IC ainda mais largo); `tab_est_wild_bootstrap.csv` (p wild-cluster = **0,68**, o mais conservador dado que só 5 clusters são tratados).
- **Leitura:** todos os ICs cruzam zero em todas as especificações e métodos — o −6,7% é ponto central de um efeito **estatisticamente indistinguível de zero**. O texto deve reportá-lo sempre com o IC.
- **"Reflete piora no atendimento?" (enquadramento corrigido no veredito de 14/07/2026):** a premissa da pergunta não se sustenta — o −6,7% é ponto central de um efeito não significativo (IC95% cruzando zero em todas as especificações; wild-cluster p = 0,68; a variante sem switchers dá −17,1% com IC ainda mais largo) e não deve circular como achado. Além disso, há uma **explicação alternativa que compete de igual para igual** com qualquer leitura assistencial: hospitais OSS são custeados por contrato de gestão com **orçamento global**, não por reembolso de AIH — o valor registrado por saída é, para eles, produção sem consequência financeira direta, e o próprio −6,7% pode ser artefato do regime de pagamento, exatamente a variável cujo efeito se quer medir. O número, quando citado, deve vir sempre com o IC e com essa ressalva na mesma frase. Os demais indicadores do período (TMP −10,2%, produção +45,4%, mortalidade −1,12 p.p., complexidade atendida sem queda) seguem valendo como contexto descritivo — mas não convertem o −6,7% em evidência sobre qualidade, em nenhuma direção.
- **Nota:** após os itens 1.10/1.11/1.12 o painel muda; a reestimação completa (já prevista) atualizará o número — este item deve ser refeito **no painel novo** (item 11 da ordem da Etapa 2).

---

## 1.8 — UTI Barcelona × modelo próprio: **não operacionalizável hoje — não existe campo de ocupação na classificação Barcelona**

- `tab_classificacao_hospitais.csv` (e a planilha 20260303) tem apenas: Leitos, Salas Cirúrgicas, **UTI (nº de leitos)**, flags cirúrgicas, Pontuação, Classificação. **Não há campo de ocupação nem de UTI-dia** — nenhum proxy "Barcelona" de ocupação de UTI é computável com os dados atuais.
- Método atual (confirmado por Alberto): dias-UTI acumulados ÷ (leitos-UTI × 365), pronto no resumo SIH. Medianas anuais: 59,9%–72,0%, com pico de 82,9% em 2021.
- **Pendência de escopo para a próxima reunião (quarta/quinta):** o que seria o "modelo próprio" — fonte de leitos-UTI de referência (CNES mensal? SIH?), fórmula, tratamento de leitos bloqueados. **Nenhum código foi escrito**, conforme o encaminhamento.

**Adendo (C1, veredito de 14/07/2026) — mecanismo explicado; o que resta é uma escolha, não uma pendência técnica:** a `ocupacao_uti` do SIH usa **leitos SUS anuais** como denominador (reproduzida com erro mediano zero). A contagem Barcelona **não** é menor no geral (≥ à contagem SUS em 96,8% dos CNES), mas é uma **fotografia fixa de 2026 aplicada retroativamente**, enquanto o `uti_sus` do SIH cresce ano a ano — por isso a série "Barcelona" cruza a série SIH e passa a mostrar ocupação **maior a partir de 2022** (2025: 80,4% vs 72,0%), exatamente o que Alberto observou. Diferença adicional de tratamento: o resumo SIH atribui ocupação 0 a quem tem `uti_sus` = 0; recálculos devolvem NaN. **Decisão a tomar (Pergunta 2 do memorando):** qual denominador é o padrão do projeto — leitos SUS anuais (atual), leitos totais anuais, ou fotografia Barcelona — e se "modelo próprio" significa algo além dessa escolha.

---

## 1.9 — Classificação institucional ratificada: **documentado; e a docstring que a reunião mandou corrigir já está correta**

- Registro adicionado em `criterios_construcao_painel.md` (§7, item 4): ratificação formal de 13/07/2026 por Priscilla e Alberto, HU-UFSCar mantido em "Privado", pendência encerrada, crosswalk permanece cancelado, exceção pontual = Guilherme Álvaro (item 1.11).
- A planilha nova `Classificacao_Assistencial_UFSCar.xlsx` (trazida pela equipe) é consistente com o status quo: HU-UFSCar (5586348), São Carlos, classificação "Privado".
- **Correção prevista para a Etapa 2 que NÃO se confirma:** a docstring de `diagnostico_painel_definitivo.py` **já** trata o HU-UFSCar como "agrupado em Privado por decisão da equipe" (linhas 13–14 e na nota `NOTA_PROXY_FIG`) — foi atualizada em rodada anterior. **Não há item de código a corrigir aqui.**

---

## 1.10 — Pediátricos/onco-pediátricos: **9 candidatos dentro do painel de 314 (16 no total), validados contra a planilha do Alberto; 1 falso positivo já identificado**

Sinais usados: (A) `especializacao` = "001 PEDIATRIA"; (B) `nome_fantasia` (2020–21) com INFANTIL/PEDIATR/CRIANÇA/BOLDRINI/DARCY VARGAS/GRAACC/ITACI/...; (C) `Instituição` da classificação Barcelona (nomes completos); (D) "MATERNO" → só revisão manual. Cruzado com a planilha nova `Hospitais_por_Categoria_Painel314.xlsx` (aba Pediátrico = 3; aba Oncológico = 7, inclui os onco-pediátricos).

**Candidatos DENTRO do painel definitivo (todos com 11/11 anos; nenhum é switcher nem Privado):**

| CNES | Nome | Município | Gestão | Sinal | Leitura |
|---|---|---|---|---|---|
| 2071371 | Hospital Infantil Darcy Vargas | São Paulo | Direta | espec+nome+inst | pediátrico inequívoco |
| 2078325 | Hosp. Mun. Infantil Menino Jesus | São Paulo | Púb. Municipal | espec+nome+inst | pediátrico inequívoco |
| 2080427 | Hosp. Mun. da Criança e do Adolescente | Guarulhos | Púb. Municipal | espec+nome+inst | pediátrico inequívoco |
| 2081482 | Boldrini | Campinas | Filantrópico | nome+inst | onco-pediátrico inequívoco |
| 2089696 | GRAACC — Inst. de Oncologia Pediátrica | São Paulo | Filantrópico | nome+inst | onco-pediátrico inequívoco |
| 2088517 | Hospital Infantil Cândido Fontoura | São Paulo | Direta | nome+inst | pediátrico inequívoco |
| 2076985 | Casa da Criança Betinho | São Paulo | Filantrópico | nome+inst | **decidir**: nome infantil, mas perfil de longa permanência (TMP mediano 29,7) |
| 2082454 | Casa da Criança de Tupã | Tupã | Filantrópico | nome+inst | **decidir**: idem (TMP mediano 30,1; tipo 07 sem especialização) |
| 2751038 | Santa Casa de Presidente Epitácio | Pres. Epitácio | Filantrópico | nome+inst | **FALSO POSITIVO** — o regex "ITACI" casou dentro de "EPITÁCIO"; hospital geral, **manter** |

Os 3 da aba "Pediátrico" do Alberto (2071371, 2078325, 2080427) são subconjunto dos 6 inequívocos acima — a lista por palavras-chave adiciona Boldrini, GRAACC e Cândido Fontoura, que se encaixam na letra da decisão ("onco-pediátricos e perfil claramente equivalente"). Fora do painel definitivo há mais 7 candidatos (já excluídos por outros filtros; sem ação necessária). O único "materno-infantil" candidato (9539, S. J. dos Campos) já está fora do painel.

**Impacto se os 6 inequívocos + 2 "Casas da Criança" saírem:** painel cai de 314 para **306–308 CNES** (3.366–3.388 hospital-ano) — o funil ganharia uma "ETAPA F" nomeada. **Nada foi excluído; aguardo validação linha a linha.**

**Adendo (C3, conclusão reescrita por exigência do veredito de 14/07/2026) — efeito da exclusão sobre o grupo de comparação Direta, por extenso:**
- **Mortalidade, com os pediátricos incluídos:** na comparação simples de medianas, a **Direta** tinha a mortalidade mais favorável — 0,0475, contra 0,0493 da OSS (Direta *abaixo* da OSS).
- **Mortalidade, sem Darcy Vargas e Cândido Fontoura:** a mediana da Direta sobe para 0,0535 e a relação **inverte de direção** — a Direta passa a ter mortalidade mediana *acima* da OSS (0,0535 contra 0,0493). Não é mudança de magnitude: é inversão de sinal da comparação simples.
- **TMP:** aqui **não há inversão** — a OSS já tinha TMP mediano mais favorável com os pediátricos incluídos (4,85 contra 6,07 da Direta) e continua mais favorável sem eles (4,85 contra 6,26); a exclusão apenas **amplia** a diferença na mesma direção (de −1,21 para −1,41 dia).
- **Frase para o dossiê:** com os pediátricos incluídos, a Direta parecia *melhor* que a OSS em mortalidade (0,0475 vs 0,0493); sem eles, essa relação **se inverte** (0,0535 vs 0,0493) — e em TMP a OSS já era melhor e fica ainda mais à frente (6,07→6,26 vs 4,85).
- Ressalva de leitura: comparação simples de medianas de hospital-ano por rótulo corrente (os 5 switchers contribuem anos pré para a Direta e anos pós para a OSS); não é estimativa de efeito — serve para dimensionar a mudança de composição do contrafactual, não para substituí-la pelos modelos.

---

## 1.11 — Hospital Guilherme Álvaro (Santos, CNES 2079720): **erro de origem em TODOS os anos — não é switcher**

- Localizado por nome na base e na classificação Barcelona (pontuação 486, faixa 4). Presente 11/11 anos no painel definitivo.
- `class_assistencial` na base bruta = **"OSS" estável em todos os 11 anos** (2015–2025), com produção em todos; `modelo_gestao_proxy` = OSS em todos os anos do painel.
- **Não** está entre os 5 switchers; **não** há transição nos dados — o cenário confirmado é o primeiro do encaminhamento: **rótulo errado de origem, todos os anos**. Não existe cenário "switcher OSS→Direta".
- **Proposta para a Etapa 2 (item 2 da ordem):** sobrescrita pontual de `modelo_gestao_proxy` (e não de `class_assistencial`, que permanece intacta para rastreabilidade da fonte — mesmo padrão do mecanismo de decisões da equipe em `construir_painel_definitivo.py`) para "Direta" no CNES 2079720 em todos os anos, com auditoria nomeada (nova linha em `tab_auditoria_revisao_manual.csv` ou tabela própria) e registro no LEIA-ME.
- **Impacto:** 11 hospital-ano migram do grupo OSS (387 → 376) para Direta (339 → 350) — mexe em todas as medianas por categoria e nos modelos; mais um motivo para o ciclo único de reexecução/reestimação.

---

## 1.12 — Simplificação da mortalidade: **mapa de impacto completo; nenhum modelo usa `complexidade_pond_mort` como covariável (nem fora da mortalidade)**

**Quem calcula/salva:**
- `mort_sem_excl`: `analise_sih.py` (INDICADORES, eh_obito_versao_b, DESFECHO_OBITO_VERSAO_B) e `construir_painel_definitivo.py` (versões com/sem COVID; re-stream de numeradores COVID também acumula `qtde_obito_sem_excl_covid`).
- `complexidade_pond_mort`: só `construir_painel_definitivo.py` (calcular_escores_complexidade).

**Quem consome (código):**
- `mort_sem_excl`: `analise_exploratoria.py` (painéis de mistura/inflação, medianas), `estimacao.py` (ZIB "ajustada" → `tab_est_mort_zib_ajustada.csv`), `fase2_bayes.R` (modelo de sensibilidade `f_morta`), `verificacao_pos_patch.py`, `verificacoes_revisao.py`.
- `complexidade_pond_mort`: `diagnostico_painel_definitivo.py` (figD06), `fase2_dea.R` (ajuste de output `qtde_adj_pond` — variante do DEA), `verificacao_pos_patch.py` (checagem de correlação).

**Ponto central para a decisão:** **nenhum modelo de nenhum indicador usa `complexidade_pond_mort` como covariável** — Fase 1 (`estimacao.py`) e Fase 2 (`preparo_fase2.R` → `cplx_z`) usam exclusivamente `complexidade_estrutural`. O único uso "de modelo" é o **ajuste de output do DEA** (variante ponderada, comparada em `tabE_spearman_ajuste_output.csv`). Portanto a lista de "modelos a reestimar só por causa da pond_mort" reduz-se ao DEA (variante); todo o resto será reestimado pelos itens 1.10/1.11 de qualquer forma. `complexidade_estrutural` permanece como métrica única — nada muda nela.

**Tabelas/figuras que reportam os aposentados como resultado:**
- Ficam **obsoletas** (deixam de existir): `extremos_mort_sem_excl_top10/bottom10.csv`, `tab_est_mort_zib_ajustada.csv`, `tabB_sensibilidade_mortalidade.csv` (a variante `mort_sem_excl` da fase 2), `figD06_complexidade_duas_versoes.png` (só existia para comparar as duas versões — remover ou substituir), `tabE_spearman_ajuste_output.csv` (comparação com a versão ponderada), painéis "mortalidade ajustada" da exploratória (`fig_ae_12`-família, `tab_ae_mistura_mortalidade.csv`).
- Só **perdem uma coluna** (regenerar): `tab_def_por_modelo_gestao.csv`, `tab_pospatch_medianas_por_modelo.csv`, `tab_def_antes_depois.csv`, `tab_def_descritiva_geral/por_ano.csv`, `tab_ae_mediana_ano(.categoria).csv`, `tab_ae_por_categoria/porte/faixa_barcelona.csv`, `tab_ae_univariada.csv`, `tab_ae_inflacao_taxas.csv`, `tab_painel_completo.csv`, `tab_descritiva_por_ano.csv` e o próprio `painel_definitivo.csv` (colunas `mort_sem_excl*`, `qtde_obito_sem_excl*`, `complexidade_pond_mort`). Obs.: `tab_covid_com_sem.csv` não reporta `mort_sem_excl` (usa mort_all) — não é afetada.
- Textos a revisar (Etapa 4): `LEIAME_painel_definitivo.txt`, `criterios_construcao_painel.md` (§4), `relatorio_verificacao_painel_jul2026.md`, `RELATORIO_EXECUCAO.md`, seções LaTeX que citam "mortalidade ajustada"/duas versões de complexidade.
- Sinal empírico que apoia a simplificação: as medianas de `mort_all` e `mort_sem_excl` são idênticas até a 4ª casa em 4 das 5 categorias (só a OSS difere em 0,0001) — a versão B praticamente não acrescenta informação no agregado.
- **Nenhum `.rds`/`.csv` antigo foi apagado**; classificação regenerar × arquivar será fechada na Etapa 4, após decisão.

---

## Estado do gate (atualizado após o veredito de 14/07/2026)

- **Aplicado:** 1.11 — patch `SOBRESCRITAS_MODELO_GESTAO` em `construir_painel_definitivo.py` aplicado e verificado em 14/07/2026 (`_verificacao_patch_1_11.py`): OSS 387→376 hospital-ano e 39→38 CNES; Direta 339→350 hospital-ano e 32→33 CNES; `class_assistencial` intacta; sem interação com a regra modal da ETAPA A. O `painel_definitivo.csv` em disco continua PRÉ-patch até a reexecução da Etapa 3 (ciclo único).
- **Sem ação de código:** 1.1 (não é bug; estatística primária passa a ser a proporção agregada), 1.9 (documentado; docstring já estava correta).
- **Liberados, na fila (um por vez, diff + "sim"):** 1.3 (tabela de ocupação — próximo), 1.5 (deflação da camada descritiva), 1.2 + 1.7 (juntos, com a ressalva do orçamento global embutida no texto).
- **Retidos até resposta externa (memorando de 14/07/2026):** 1.4 (censura do TMP — Pergunta 1, Alberto), 1.8 (denominador de UTI — Pergunta 2, Alberto), 1.10 + 1.12 (ratificação combinada — Pergunta 3, Priscilla).
- 1.6 (comparativo de atendimento de Sorocaba) aguarda escolha entre as 3 leituras; não depende do memorando.
- Itens 1.10 + 1.11 + 1.12 mudam funil/rótulo/indicadores → um único ciclo de reexecução (Etapa 3) e reestimação completa da Fase 2 + reseleção de entrevistas (Etapa 4), com bloqueio do cronograma qualitativo até lá.
