# Relatório de execução — Etapa 3/4 do ciclo de revisão (15/07/2026)

**De:** João Eduardo Pastori Garcia (estatística do projeto)
**Data:** 15/07/2026
**Assunto:** exclusão final (ETAPA F), reexecução única do pipeline e reconciliação — fechamento das três perguntas do memorando de 14/07/2026

---

## 1. Resumo executivo

O pipeline foi reexecutado uma única vez, do zero (caches apagados), com a nova **ETAPA F** no funil de auditoria. O painel definitivo passou de **314 CNES / 3.454 hospital-ano** para **289 CNES / 3.179 hospital-ano** (−25 CNES / −275 hospital-ano; todos os 25 excluídos tinham os 11 anos no painel balanceado, 25 × 11 = 275). O valor real coincide exatamente com a projeção registrada em `criterios_construcao_painel.md` §2.3.

Nota de escopo: o desenho original desta etapa previa a exclusão de 20 CNES (314 → 294). Por decisão de João em 15/07/2026, a ETAPA F foi aplicada com o escopo completo documentado no §2.3 — **25 CNES** (20 ratificados + 4 casos decididos em 15/07 + 1 pelo critério §2.1), levando o painel a **289**.

## 2. As quatro decisões desta rodada (todas de João, 15/07/2026)

1. **Exclusão (Pergunta 3 do memorando, parte a):** lista de 20 CNES **ratificada por João** — **mudança de procedimento** em relação ao desenho original, que previa ratificação pela Priscilla. Registrada no docstring de `construir_painel_definitivo.py` (nota D-F), em `criterios_construcao_painel.md` §2.3/§7 e no adendo do memorando.
2. **TMP (Pergunta 1):** **não há teto de 30,5 dias** como regra dos dados/critérios do estudo. O empilhamento de 80 hospital-ano perto de ~30 dias fica registrado como **achado descritivo**, não como censura. Verificado em código: nenhuma lógica de teto/cap/winsorização de `tmp` existe em `analise_sih.py` nem em `construir_painel_definitivo.py` (referências a 30,5 só em scripts de investigação somente-leitura). **Nenhuma mudança de código foi necessária.**
3. **Ocupação de UTI (Pergunta 2):** mantido o denominador de **leitos-UTI SUS anuais** do SIH — decisão **confirmatória** da prática vigente. Verificado: `ocupacao_uti` é lida diretamente do resumo SIH e não há branch alternativo (leitos totais / fotografia Barcelona 2026) ativo no pipeline. **Nenhuma mudança de código.**
4. **Mortalidade (item 1.13):** **reversão à definição original.** `mort_all` **e** `mort_sem_excl` seguem como indicadores paralelos (simplificação não aplicada); `complexidade_pond_mort` **não** foi aposentada (forma funcional segue pendente da Priscilla); o cruzamento óbito×complexidade **não** foi implementado — o código preparatório foi **desativado por flag única** (`ITEM_113_MORT_ESTRATIFICADA = False` em `analise_sih.py`, referenciada também por `construir_painel_definitivo.py`), permanecendo no repositório para eventual reativação. A **salvaguarda de circularidade** (`complexidade_estrutural` exclusiva em modelos com mortalidade como dependente) **permanece intacta** — não fazia parte da reversão.

## 3. Lista final dos 25 CNES excluídos na ETAPA F

**Pediátricos/onco-pediátricos (9)** — população estruturalmente incomparável por faixa etária/perfil epidemiológico; ratificação de 15/07/2026:
2071371 Darcy Vargas; 2078325 Menino Jesus; 2080427 HMCA Guarulhos; 2088517 Cândido Fontoura; 2081482 Boldrini; 2089696 GRAACC; 2076985 Casa da Criança Betinho (SP); 2082454 Casa da Criança de Tupã; 2079321 GPACI Sorocaba.

**Crônicos/reabilitação/ex-sanatórios (11)** — população estruturalmente incomparável por intensidade/duração do cuidado; ratificação de 15/07/2026:
2079208 Lar Espírita Maria de Nazaré; 2790998 Lar Irmã Dulce; 2082276 Casas André Luiz; 2089572 Assoc. Cruz Verde; 2688522 Casa de David; 2080192 Hosp. Est. de Reabilitação (Itu); 2084236 C. Reab. Dr. Arnaldo Pezzuti; 2082675 Amparo ao Excepcional Ritinha; 2081725 CAIS Clemente Ferreira; 2079194 Nestor Goulart Reis; 3753433 Leonor Mendes de Barros (C. do Jordão).

**Casos decididos autonomamente em 15/07/2026 (4)** — evidência individual própria (§2.3):
3223728 Santa Casa de S. Bernardo do Campo (retaguarda/cuidados prolongados); 3001466 Centro Hosp. do Sistema Penitenciário (população cativa em regime não-clínico); 2082470 São Leopoldo Mandic, Araras (psiquiátrico não capturado pelo §2.1 — ex-Clínica Sayão); 2081466 N. Sra. da Divina Providência, Jaci (dependência química/cuidados prolongados/paliativos).

**Critério §2.1, fora da ratificação (1):**
2812703 Instituto de Psiquiatria do HCFMUSP (psiquiátrico — correção de falha de preenchimento da especialização).

Detalhe por CNES gravado em `analises/tabelas/tab_auditoria_cnes_removidos.csv` (25 entradas na ETAPA F) e resumo do funil em `tab_auditoria_filtros.csv`.

## 4. Verificações de integridade

- **Sobreposição com switchers/Privado: vazia** (verificação programática pré-aplicação): nenhum dos 25 é conversor Direta→OSS (5 CNES) nem do grupo Privado (3 CNES).
- **Pós-reexecução (verificacoes_painel_definitivo.py):** os 5 switchers permanecem no painel com 11/11 anos e transições confirmadas; o grupo Privado permanece com 3 CNES × 11 anos; a ETAPA D removeu os mesmos 82 CNES de antes (o balanceamento não mudou).
- **Funil completo (real):** 830/7.016 → A: 754/6.370 → B: 405/3.832 → C1: 399/3.823 → C2 (sem remoção de linhas) → D: 317/3.487 → E: 314/3.454 → **F: 289/3.179**.
- **Base bruta reconstruída identicamente** (7.016 hospital-ano, 830 CNES) e diagnóstico prévio de cabeçalho validou a estrutura dos 11 arquivos brutos.
- **Flag do 1.13 respeitada na prática:** o novo cache base não contém `qtde_obito_alta_complex` e o log da ETAPA C2 registra "item 1.13 INATIVO".

## 5. Composição por modelo de gestão no painel de 289 (hospital-ano | CNES distintos)

Direta 284 | 27 · Filantrópico 1.881 | 171 · OSS 365 | 37 · Privado 33 | 3 · Público Municipal 616 | 56.

Medianas (todos os anos, painel novo): mortalidade Direta 0,0584 vs OSS 0,0494 — **a inversão de sinal descrita no memorando se mantém**; TMP Direta 6,01 vs OSS 4,74 dias. *Nota de registro:* os valores reais diferem marginalmente das projeções do §2.3 (0,0585/0,0504 e 5,86/4,80), que foram calculadas em investigação prévia; os números oficiais passam a ser os do pipeline (`tab_def_por_modelo_gestao.csv`).

## 6. O que ainda depende de Alberto/Priscilla

- **Priscilla:** a **forma funcional de `complexidade_pond_mort`** segue pendente de ratificação (questão separada, não decidida nesta rodada).
- **Alberto:** a leitura técnica sobre regra de diárias por AIH (P1, agora de interesse interpretativo, não bloqueio) e sobre os 4 casos decididos em 15/07 (revisáveis se a resposta trouxer informação nova).

## 7. Impacto a jusante (sinalizações — não executado nesta rodada)

1. **Fase 2 (CRE/Mundlak, Bayesiano hierárquico, DEA, SFA — `fase2_*.R`):** estimada sobre o painel de **314**; **precisa ser reestimada** sobre o painel de 289 antes de qualquer resultado voltar a circular. Ciclo separado.
2. **Fase 1 (`estimacao.py`, `analise_exploratoria.py`, `inferencia_robusta.py`, gráficos):** mesmo status — resultados atuais refletem o painel de 314.
3. **Seleção de entrevistas da fase qualitativa** (`tab_selecao_entrevistas.csv`, `tab_sel_conversores_trajetoria.csv`): depende do painel atualizado e **deve ser refeita depois da reestimação**, não em paralelo.
4. **Documentos com N antigo** (README, LaTeX `sec01_painel.tex` e seções de resultados, rótulos do `diagnostico_painel_definitivo.py`): o enunciado do painel será reconciliado em edição própria; as seções de **resultados** só devem ser atualizadas junto com a reestimação, para não misturar N novo com estimativas antigas.
