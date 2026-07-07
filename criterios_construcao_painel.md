# Critérios de Construção do Painel Analítico Definitivo

**Projeto:** Modelos institucionais de gestão e desempenho na rede hospitalar SUS do estado de São Paulo (2015–2025)
**Estatístico Responsável:** João Eduardo Pastori Garcia
**Pesquisadora Responsável (PI):** Priscilla Reinisch Perdicaris
**Responsável pela Base de Dados:** Alberto Tomasi
**Data deste documento:** conforme decisões formalizadas pela equipe até a presente data

Este documento consolida as decisões metodológicas já fechadas pela equipe sobre escopo, critérios de inclusão e exclusão de hospitais, tratamento dos dados da pandemia de COVID-19, definição de complexidade e modelo de financiamento. Serve como especificação técnica para a construção do painel hospital-ano definitivo a partir da base SIH/SUS já processada, e complementa o documento técnico-metodológico principal do projeto.

## 1. Escopo da Pesquisa

A equipe, composta por João Eduardo Pastori Garcia, Priscilla Reinisch Perdicaris e Alberto Tomasi, decidiu formalmente expandir o recorte geográfico da pesquisa. O escopo anterior, restrito à região metropolitana de São Paulo, passa a cobrir **todos os hospitais do estado de São Paulo**, mantendo a janela temporal de 2015 a 2025.

## 2. Critérios de Inclusão e Exclusão de Hospitais

### 2.1 Tipo de estabelecimento

Serão incluídos hospitais gerais e especializados. Ficam **excluídos**:

- Hospitais dia (`tipo_hospital` código 62)
- Hospitais psiquiátricos, identificados pela combinação `tipo_hospital` código 07 (Hospital Especializado) com `especializacao` código 006 (Psiquiatria)
- Centros de Atenção Psicossocial — CAPS (`tipo_hospital` código 70)

Maternidades (`especializacao` código 005) são explicitamente **mantidas** no estudo.

**Regra de classificação fixa por tipo (valor modal).** Como o tipo de estabelecimento e a especialização declarados no SIH variam entre anos para um mesmo CNES, a aplicação dos critérios acima **não é feita ano a ano**: cada hospital é classificado pelo **valor modal** (mais frequente) de `tipo_hospital` e `especializacao` ao longo dos anos em que possui produção registrada, com desempate pelo ano mais recente — extensão da mesma lógica de robustez a anos-anomalia adotada para o porte (§2.2). Hospitais mantidos cuja série tocou uma categoria de exclusão em ano isolado são registrados em log de revisão manual. Verificação empírica (jul/2026): dos 830 CNES da base, apenas **2** apresentam cadastro instável de tipo e apenas **1** (CNES 2707209) teria decisão diferente sob o critério alternativo do último ano com produção — caso sem efeito sobre o painel final, pois o estabelecimento é eliminado de todo modo pelos filtros de porte e de balanceamento.

### 2.2 Porte mínimo — regra de classificação fixa

A amostra é restrita a hospitais com **mais de 50 leitos**. Como o número de leitos declarado no SIH varia ano a ano para um mesmo estabelecimento — em alguns casos de forma expressiva, inclusive com anos isolados que sugerem erro de cadastro —, a aplicação do critério **não é feita ano a ano**, sob risco de o mesmo hospital entrar e sair da amostra entre anos consecutivos, o que violaria a lógica de painel balanceado já adotada no projeto (apenas hospitais presentes em todos os anos do período são retidos).

**Regra adotada:** calcula-se a **mediana** do número total de leitos de cada hospital ao longo de todos os anos em que ele possui produção registrada no SIH. Hospitais com mediana superior a 50 leitos são incluídos, em caráter fixo, para todos os anos do painel; hospitais com mediana igual ou inferior a 50 são excluídos, também de forma fixa. A mediana foi preferida à média por ser mais robusta a anos-anomalia isolados (picos ou quedas abruptas no número de leitos declarado em um único ano).

Essa regra classifica de forma definitiva e estável cerca de 91 hospitais que, sem esse critério, oscilariam repetidamente em torno da linha de corte entre anos.

## 3. Tratamento de Dados Relacionados à COVID-19

João Eduardo Pastori Garcia, Priscilla Reinisch Perdicaris e Alberto Tomasi decidiram, em conjunto, excluir da análise principal:

- **Hospitais criados exclusivamente para o atendimento de COVID-19** (hospitais de campanha e unidades emergenciais análogas), identificados no painel atual sob rótulos heterogêneos de `class_assistencial` (Público, Hospital COVID, Sem Fins Lucrativos, e parte de Desativado), e via nomenclatura do estabelecimento
- **Procedimentos específicos da pandemia** (código 999), dentro de hospitais regulares que permanecem no estudo, utilizando as versões dos indicadores calculadas sem esses registros (já disponíveis em `tab_covid_com_sem.csv`)

A série temporal da pesquisa **mantém os anos de 2020 e 2021**; apenas as unidades e os atendimentos específicos da pandemia são removidos, não o biênio inteiro.

## 4. Definição de Complexidade Hospitalar

Diante da impossibilidade de ajuste por DRG (ausência de campo de diagnóstico na base SIH), a equipe decidiu desenvolver uma métrica própria de complexidade baseada no modelo de Barcelona, **incorporando a mortalidade como variável de peso** para qualificar segurança e desempenho hospitalar.

**Ressalva metodológica a resolver com a equipe:** essa decisão tensiona com a salvaguarda de circularidade já registrada no projeto, segundo a qual o escore de complexidade ponderado por mortalidade não deve ser utilizado como variável de controle em modelos que têm a própria mortalidade como variável dependente, sob pena de endogeneidade mecânica. A recomendação técnica, até deliberação em contrário, é utilizar o escore estrutural de Barcelona sem ponderação por mortalidade especificamente nos modelos em que mortalidade é a variável dependente, reservando a versão ponderada para os demais modelos (TMP, custo, ocupação, produção).

## 5. Modelo de Financiamento e Administração

A equipe decidiu não analisar separadamente as categorias de financiamento (MAC/FAEC), por estarem diretamente ligadas ao modelo de gestão da unidade. A forma de administração (Direta, Autarquia, OSS, PPP, Filantrópico) será utilizada como variável de aproximação (*proxy*) para o modelo de pagamento.

## 6. Questões Ainda em Aberto

Os critérios acima resolvem a construção mecânica do painel, mas **não resolvem** a variável central da pesquisa. Permanecem pendentes:

1. **Público Municipal** — decisão pendente sobre se hospitais municipais permanecem no escopo do estudo e, em caso afirmativo, como distinguir internamente Direta municipal de OSS municipal
2. **Datas exatas de conversão** dos hospitais que mudaram de modelo de gestão ao longo do painel, com precisão de mês/ano, a partir de fonte oficial (contrato de gestão ou Diário Oficial)

## 7. Decisões Registradas (jul/2026)

Itens antes listados como pendências e desde então resolvidos ou decididos pela equipe:

1. **Crosswalk institucional definitivo (CNES → modelo de gestão, por ano)** — avaliado e **CANCELADO** em julho/2026. A variável `modelo_gestao_proxy`, construída a partir de `class_assistencial` do SIH, passa a ser a **definição adotada** de modelo de gestão do projeto: captura Direta, OSS e Filantrópico (inclusive os switchers Direta→OSS documentados), não desmembra Autarquia nem PPP, e mantém "Público Municipal" como categoria única. Deixou de ser pendência aberta.
2. **Duplicidade de coluna em 2025** na classificação assistencial — **resolvida**: a fonte passou a ser o lookup CNES→classificação embutido nas primeiras linhas de produção do arquivo de 2025 (637 pares CNES→rótulo), conforme `relatorio_verificacao_painel_jul2026.md` (CHANGE 1).
3. **Fonte e denominador dos indicadores de ocupação** — **resolvida** (permanência acumulada no ano ÷ leitos × 365), confirmada por Alberto e registrada neste documento e no LEIA-ME do painel definitivo.
