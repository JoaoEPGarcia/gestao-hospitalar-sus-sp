# Relatório consolidado — Blocos 3, 4 e 6 (14/07/2026)

**Caráter:** investigação somente-leitura (`_investigacao_blocos34_6_14jul2026.py`). Nenhum CNES foi excluído; nenhuma mudança em `analise_sih.py`. Este relatório alimenta a validação de João antes de qualquer exclusão adicional e o ajuste final do memorando antes do envio.

---

## Bloco 3 — Ampliação do item 1.10

### 3.1 Perfil psiquiátrico não capturado pelo filtro 07+006: **1 candidato**

- Nenhum CNES do painel definitivo declarou especialização psiquiátrica (006) em nenhum ano — o filtro da ETAPA A não deixou escapar ninguém *pela via da especialização*.
- Pela via do **nome**, um único candidato: **CNES 2812703 — Fundação Faculdade de Medicina HCFMUSP, Instituto de Psiquiatria (São Paulo)**. Tipo modal "07 HOSPITAL ESPECIALIZADO", especialização modal **vazia** — escapou porque o filtro exige tipo 07 **E** espec. 006, e a especialização nunca foi preenchida. Filantrópico, Médio Porte, faixa Barcelona 3, TMP mediano 26,7 dias (está no grupo de longa permanência), mortalidade mediana ~0. **Candidato a exclusão pelo critério psiquiátrico já vigente** — aguarda validação.

### 3.2 Casas da Criança (Betinho e Tupã)

Decisão já tomada em 14/07/2026: **excluir**. Passam à lista firme do item 1.10 junto com os 6 inequívocos → **9 CNES na lista de exclusão pediátrica/psiquiátrica proposta** (6 pediátricos/onco-pediátricos + 2 Casas da Criança + 1 psiquiátrico), pendente de ratificação combinada (memorando, pergunta 3). Painel passaria de 314 para **305 CNES** (3.355 hospital-ano) se todos forem confirmados.

### 3.3 Falso positivo documentado (para não repetir o padrão)

**Santa Casa de Presidente Epitácio (2751038) — MANTÉM no painel.** Causa do falso positivo: o padrão de busca por nomes de instituições onco-pediátricas incluía a substring `ITACI` (Instituto de Tratamento do Câncer Infantil), sem delimitador de palavra — e `ITACI` casa dentro de `EPITACIO` (Presidente Ep**itáci**o, com o texto normalizado sem acento). Lição registrada: padrões de sigla curta em busca nominal devem usar bordas de palavra (`\bITACI\b`) e **toda** lista gerada por palavra-chave passa por validação manual linha a linha antes de qualquer exclusão — exatamente o processo que capturou este caso.

---

## Bloco 4 — Os 18 CNES de longa permanência (TMP mediano > 20 dias)

Classificação caso a caso (tabela completa na saída do script):

| Classe | n | CNES |
|---|---|---|
| (a) ligado a critério de exclusão já adotado | **3** | 2082454 e 2076985 (Casas da Criança — pediátrico, decisão tomada); 2812703 (Inst. de Psiquiatria HCFMUSP — psiquiátrico, aguarda validação) |
| (b) causa identificada, fora dos critérios — mantém com ressalva de censura (30,5 d) | **7** | 2079208 (Lar Espírita Maria de Nazaré, Mogi Mirim), 2790998 (Lar Irmã Dulce, Pirajuí), 2082276 (Casas André Luiz, Guarulhos), 2089572 (Assoc. Cruz Verde, SP), 2688522 (Casa de David, SP), 2080192 (Hosp. Est. de Reabilitação, Itu — Direta), 2084236 (Centro Esp. em Reabilitação Dr. Arnaldo Pezzuti, Mogi das Cruzes — Direta) |
| (c) causa não identificada por sinal automático — decisão manual | **8** | ver abaixo |

**Os 8 casos (c), com leitura qualitativa preliminar para a decisão manual:**

| CNES | Nome | Observação |
|---|---|---|
| 2082675 | Assoc. de Amparo ao Excepcional Ritinha (Araçatuba) | "Amparo ao excepcional" indica instituição para pessoas com deficiência — perfil (b) provável; o regex não cobria "EXCEPCIONAL" |
| 2081725 | CAIS Clemente Ferreira (Lins — Direta) | CAIS = Centro de Atenção Integral à Saúde, rede estadual de crônicos (ex-sanatório) — perfil (b) provável |
| 2079194 | Hospital Nestor Goulart Reis (Américo Brasiliense — Direta) | Unidade estadual historicamente de crônicos/reabilitação — perfil (b) provável |
| 3001466 | Centro Hospitalar do Sistema Penitenciário (SP — **OSS**) | População carcerária: perfil único; decidir se é comparável (não é pediátrico nem psiquiátrico; TMP 21,1) |
| 2082470 | Hospital São Leopoldo Mandic (Araras) | Sem sinal no nome; conferir com Alberto |
| 3753433 | Hospital Leonor Mendes de Barros (Campos do Jordão) | Ex-sanatório de altitude — crônicos/reabilitação provável |
| 3223728 | Santa Casa de São Bernardo do Campo | Destoa do grupo: mortalidade mediana **9,9%** (alta) com TMP 24,8 — perfil de retaguarda/cuidados prolongados? conferir |
| 2081466 | Hospital N. Sra. da Divina Providência (Jaci) | Sem sinal no nome; conferir |

Nenhum switcher e nenhum Privado no grupo. **Consequência para o item 1.4:** se a resposta de Alberto confirmar o teto de diárias por AIH, os (b) e os (c) que permanecerem carregam ressalva de leitura no TMP (e a decisão sobre mantê-los no indicador TMP dos modelos fica para o gate do memorando).

**Ajuste de gráfico já aplicado (aprovado independente da investigação):** TMP em escala linear com teto fixo de **35 dias** nos dois gráficos que usavam log (`fig_ae_03_hist_log_tmp`, `fig_ae_04_violino_tmp` em `analise_exploratoria.py`); nomes de arquivo mantidos por estabilidade das referências LaTeX (renomeação avaliada na Etapa 4). Figuras regeneram na Etapa 3.

---

## Bloco 6 — Item 1.13: viabilidade da mortalidade estratificada por complexidade

**Veredicto: viável, mas exige re-stream dos 11 arquivos brutos e nasce indefinida/instável em ~53% do painel.**

1. **Estrutura dos dados permite o cruzamento.** Cada linha de produção do SIH traz, na mesma linha, QTDE, DESFECHO (óbito), COMPLEX (alta complexidade) e Cód Grupo/Subgrupo (COVID). Dá para saber, para cada óbito, se a internação era de alta complexidade — e também se era COVID (logo, as versões `_com_covid`/oficial seguem a mesma lógica do resto do painel).
2. **Mas o cache não guarda esse cruzamento** (só totais marginais). Implementar exige reprocessar os 11 xlsx (83–108 MB cada): ou (i) estender os acumuladores de `analise_sih.py` e reconstruir o cache — recomendado, porque a Etapa 3 já prevê reexecução com cache invalidado — ou (ii) re-stream dedicado no molde de `restream_numeradores_covid()`. Custo: uma leitura integral da base (ordem da construção original do painel).
3. **Variáveis propostas** (não implementadas): `mort_alta_complex` = óbitos em internações de alta complexidade ÷ internações de alta complexidade; `mort_baixa_complex` = idem para as demais — ambas com desconto dos numeradores/denominadores COVID em 2020–2021, como `mort_all` hoje.
4. **O problema é o denominador.** No painel atual (denominadores sem COVID):
   - `mort_alta_complex` **indefinida** (denominador zero) em **34,4%** dos hospital-ano; denominador < 20 em **53,0%**; ≥ 100 (estável) em só **39,0%**;
   - **50 dos 314 CNES** têm zero alta complexidade em todos os anos — variável permanentemente indefinida para eles;
   - a instabilidade concentra-se exatamente nos grupos de comparação: Público Municipal (60% dos hospital-ano com denominador < 20; mediana 8), Filantrópico (56%; mediana 3) e Direta (43%); OSS é o grupo mais estável (mediana 281);
   - problema simétrico no Privado: com ~98% de alta complexidade, a `mort_baixa_complex` fica sem denominador (mediana de 13 internações não-alta; p25 = 0).
5. **Implicação para o memorando (pergunta 3):** a estratificação é tecnicamente possível e responde à pergunta "efeito direto vs total" sem controlar por mediador, mas **não substitui** um ajuste de composição para metade do painel — qualquer uso exigirá regra explícita de denominador mínimo (ex.: reportar `mort_alta_complex` apenas onde denominador ≥ 50, e nunca em modelo de efeito fixo para o painel completo). Sugestão: anexar este quadro à pergunta 3 antes do envio, para Priscilla decidir entre (a) `mort_all` puro, (b) `pct_alta_complex` como controle (efeito direto), (c) estratificação parcial como análise descritiva complementar — as três podem coexistir, com papéis distintos.

---

## Adendos de 14/07/2026 (Passo 4 do prompt consolidado)

- **Santa Casa de S. Bernardo do Campo (3223728):** não aparece em NENHUMA tabela de extremos hospital-ano (`extremos_mort_all_top10/bottom10`, `extremos_tmp_top10/bottom10`). A trajetória ano a ano mostra padrão **consistente e em transição**, não ano-anomalia: mortalidade cai de 14,0% (2015) para 2,5% (2025) enquanto o TMP sobe de 18,8 para 28,9 dias (rumo ao teto de censura) e a ocupação vai a ~99%, com volume estável (~550 saídas/ano) — quadro compatível com consolidação de perfil de retaguarda/cuidados prolongados ao longo da década. Segue pendente de decisão (fora da lista de 20).
- **Centro Hospitalar do Sistema Penitenciário (3001466 — OSS):** registrado no dossiê do item 1.10 que este CNES tem **população cativa (carcerária)**, o que pode afetar tempo de permanência e taxas de alta por razões administrativas alheias ao quadro clínico — perfil distinto de qualquer critério de exclusão já discutido. **Nenhuma decisão de incluir/excluir tomada**; vai ao memorando como caso de confirmação com Alberto.
- **Falso positivo (registrado no Bloco 3.3):** regra permanente — siglas curtas em busca nominal exigem borda de palavra e validação manual (caso ITACI/EPITÁCIO).

## Estado após este relatório

- **Aplicados hoje:** 1.3 (tabela `tab_def_ocupacao_sem_pandemia.csv`, com ressalva do Privado na linha), princípio pediátrico vs. maternidade (§2.3 dos critérios), decisão do denominador de UTI (§7.5 dos critérios), teto de 35 dias nos gráficos de TMP.
- **Na fila (um por vez, diff + "sim"):** 1.2 (relabeling + ressalva do orçamento global — diff apresentado no chat), depois 1.5 (deflação descritiva), depois 1.6 (comparativo por `pct_alta_complex`).
- **Aguardando validação de João (este relatório):** lista firme do 1.10 ampliado (9 CNES), os 8 casos (c) de longa permanência, e o ajuste do memorando (pergunta 3) com o quadro do item 1.13.
- **Sem mudança:** `analise_sih.py`, painel em disco, modelos.
