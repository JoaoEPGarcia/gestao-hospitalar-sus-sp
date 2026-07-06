# Relatório de execução da fase 2: Bayesiana hierárquica, DEA e SFA

Pacote de resultados da fase 2 da estimação (hospitais SUS/SP, painel de 314 CNES por 11 anos, 3.454 observações), produzido para revisão externa. Todos os scripts desta pasta são reexecutáveis; nenhum artefato do pipeline original foi alterado. Sementes fixadas em 20260706 em tudo que é estocástico.

## 1. Ambiente e versões

R 4.6.0 (Windows 11), biblioteca de usuário em LOCALAPPDATA. Pacotes: glmmTMB 1.1.14, Benchmarking 0.33, rDEA 1.2.8, frontier 1.1.8, truncreg 0.2.5, maxLik 1.5.2.2. O painel de entrada é analises/painel_definitivo.csv, verificado no início de cada script (314 CNES, 3.454 linhas, 11 anos por CNES, sem NaN nas variáveis chave; o script aborta se não conferir).

Preparo comum (preparo_fase2.R): custo e valor deflacionados pelo IPCA dez sobre dez para preços de 2025; porte fixo pela mediana de leitos; exclusão das 2 observações de denominador frágil (CNES 2097613, 2020 e 2021); dummy dos 18 hospitais de longa permanência (fora das equações de TMP); winsorização das ocupações no p99 (124,2% e 164,2%, reproduzidos exatamente); Mundlak pela média da dummy OSS por hospital; categoria com Direta como referência; ano como fator.

## 2. Salvaguardas cumpridas

1. Circularidade: complexidade_pond_mort não entra como covariável em nenhum modelo desta fase; seu único uso é como fator de ajuste do OUTPUT de produção no DEA, comparado com a versão estrutural (registra se que essa recomendação do estatístico segue pendente de ratificação pela pesquisadora principal).
2. Custo e valor sempre reais (preços de 2025).
3. Exclusões vigentes aplicadas (frágeis, longa permanência no TMP, winsorização p99).
4. Variável institucional: modelo_gestao_proxy; o Privado (3 CNES) aparece apenas como demonstração de encolhimento na Frente 1 e como registro nas demais, nunca interpretado.
5. Dependência intra hospital: efeito aleatório de intercepto por CNES na Frente 1; bootstrap reamostrando hospitais inteiros na segunda etapa do DEA; a limitação da SFA pooled é discutida na Frente 3.
6. Ano como dummies em todas as fronteiras e equações (na equação de ineficiência do SFA, tendência linear, decisão documentada na Frente 3).

## 3. Frente 1: hierárquica (escada de backend e degradação documentada)

A escada prevista era brms com cmdstanr, depois rstan, depois glmmTMB. O ambiente não possui toolchain de compilação (sem Rtools instalado; cmdstanr e rstan exigem compilador C++ para gerar o amostrador). A frente desceu, portanto, para **glmmTMB** (máxima verossimilhança com efeitos aleatórios via TMB), com as seguintes degradações explícitas em relação ao plano Bayesiano pleno:

- intervalos de Wald e bootstrap paramétrico no lugar de intervalos de credibilidade;
- checagem preditiva por simulação do modelo ajustado (30 réplicas) no lugar do pp_check de posteriori;
- comparação lognormal vs Gama por AIC no lugar de LOO;
- sensibilidade de especificação (sem Mundlak; efeito aleatório de ano) no lugar de sensibilidade de priors, que não existem aqui;
- encolhimento demonstrado com categoria como efeito aleatório (partial pooling clássico de máxima verossimilhança).

A migração para brms/Stan fica listada como pendência para ambiente com toolchain (Seção 8).

**Modelos ajustados** (todos com intercepto aleatório por hospital, dummies de ano, complexidade estrutural padronizada, porte fixo, dummy de longa permanência onde cabe e Mundlak): mortalidade geral e ajustada em Beta com inflação em zero (componente de zeros com complexidade e porte; a categoria fica fora do componente de zeros por separação perfeita, OSS e Municipal não têm zeros); TMP sem longa permanência e custo real em lognormal (Gama comparada por AIC e derrotada nos dois casos: custo 49.051 contra 49.090); produção em Binomial Negativa com log de leitos; ocupação de internação em lognormal da razão winsorizada; UTI em duas partes (Bernoulli e Gama nos positivos). Objetos .rds em bayes/.

**Contrastes OSS vs Direta (hierárquicos)**, tabela completa em tabelas/tabB_modelos_hierarquicos.csv e comparação com o frequentista em tabB_comparacao_freq_bayes.csv:

| Modelo | Coef. | EP | IC95 | Efeito |
|---|---|---|---|---|
| Mortalidade (ZIB, logito) | 0,255 negativo | 0,076 | de 0,403 a 0,107 negativos | reduz |
| Mortalidade ajustada | 0,257 negativa | 0,076 | de 0,405 a 0,109 negativos | reduz |
| TMP (lognormal) | 0,108 negativo | 0,047 | de 0,200 a 0,016 negativos | queda de 10,2% |
| Custo real (lognormal) | 0,070 negativo | 0,060 | de 0,188 negativo a 0,049 positivo | sem diferença |
| Produção (BN) | 0,287 positivo | 0,072 | 0,146 a 0,427 | alta de 33,2% |
| Ocupação internação | 0,124 positivo | 0,082 | de 0,036 negativo a 0,285 | alta de 13,2%, imprecisa |
| UTI intensidade (Gama) | 0,268 positivo | 0,106 | 0,060 a 0,475 | alta de 30,7% |

Duas leituras importantes da comparação com o frequentista: o TMP e o custo hierárquicos replicam quase exatamente os efeitos fixos do relatório (0,108 e 0,070 negativos), o que confirma que o efeito aleatório está fazendo o papel do agrupamento; e a produção e a ocupação encolhem em relação ao pooled do relatório (33% contra 45%; 13% contra 24%), porque o intercepto aleatório absorve parte do contraste between entre redes, exatamente o que a especificação promete. A mortalidade hierárquica fica MAIS negativa e mais precisa que a via Mundlak pooled (0,255 contra 0,230 no logito; EP 0,076 contra 0,133), e o bootstrap paramétrico (100 réplicas válidas de 100) alarga o EP para 0,093 com IC95 de 0,465 a 0,086 negativos, ainda excluindo o zero.

**Diagnósticos e ressalvas da Frente 1**:
- Todos os modelos convergiram (código 0 do otimizador).
- A checagem preditiva da mortalidade mostra que a simulação MARGINAL do modelo suaviza a bimodalidade observada: o efeito aleatório normal não reproduz por completo os dois grupos de hospitais, embora os resíduos quantílicos condicionais da fase 1 (r de 0,984) mostrem que a média condicional está bem especificada. Registrado como limitação de forma da distribuição dos efeitos, não da média.
- A parte 1 da UTI (Bernoulli hierárquica) produz coeficiente OSS instável (ponto em torno de 11 negativos com EP acima de 7): ter ou não UTI quase não varia dentro de hospital, e o efeito aleatório absorve o nível; o contraste dessa parte não é informativo e não deve ser citado.
- Encolhimento (figB02, tabB_encolhimento): o efeito do Privado encolhe de 0,32 negativo (sem pooling) para 0,03 negativo (com pooling), a demonstração pedida de que 3 CNES não sustentam efeito próprio; as demais categorias encolhem pouco.
- Sensibilidade da mortalidade (tabB_sensibilidade_mortalidade): principal 0,255 negativo; sem Mundlak 0,216 negativo; com efeito aleatório de ano 0,253 negativo. A conclusão qualitativa não se move.
- Bootstrap paramétrico da mortalidade: tabB_bootstrap_mortalidade.csv (200 réplicas; a primeira execução falhou por a chamada do modelo depender de variáveis locais de um helper, corrigida com chamada explícita; o defeito e a correção ficam registrados).

## 4. Frente 2: DEA com bootstrap de Simar e Wilson

**Desenho.** Fronteira estimada POR ANO (11 fronteiras contemporâneas), orientação a output, CCR e BCC; eficiência de escala pela razão das duas. Inputs: leitos totais e valor total real; os leitos de UTI ficaram fora do conjunto principal porque 25,5% das observações têm UTI zero (o bootstrap exige inputs positivos) e porque são subconjunto dos leitos totais; a sensibilidade com o input de UTI na subamostra com UTI ativa dá Spearman de 0,91 com o conjunto principal, ou seja, a escolha não dirige os resultados. Outputs: saídas totais e saídas de alta complexidade. Bootstrap do algoritmo 1 de Simar e Wilson com 2.000 réplicas por ano sobre o BCC (41,6 minutos no total); escores pontuais e corrigidos em dea/dea_escores_principal.csv.

**Resultados.** Medianas da eficiência técnica BCC corrigida de viés no período completo: **OSS 0,723, Público Municipal 0,637, Direta 0,591, Filantrópico 0,577** (Privado 0,291, apenas registro). Eficiência de escala mediana entre 0,85 e 0,93 em todas as categorias. Figura figE01 (violinos por categoria) e tabela tabE_eficiencia_categoria_ano.csv (medianas por categoria e ano).

**Ajuste de complexidade do output** (único lugar da fase em que a versão ponderada por mortalidade é lícita, como fator do output de produção): os rankings MUDAM de forma relevante com o ajuste (Spearman de 0,653 entre sem ajuste e ajuste estrutural; 0,528 com o ponderado), mas **as duas versões do escore concordam fortemente entre si (Spearman 0,907)**: a escolha entre estrutural e ponderada por mortalidade importa pouco; o que importa é ajustar. Tabela tabE_spearman_ajuste_output.csv.

**Sensibilidade sem os 3 Privados.** O temor de distorção da fronteira NÃO se confirma: retirando os Privados, o escore médio dos demais sobe 0,00002 (máximo 0,028), com Spearman de 1,000 entre os rankings e só 0,06% das observações movendo mais de 0,01. Com eficiência mediana de 0,29, os Privados operam longe da fronteira neste espaço de insumos e produtos (valor alto, poucas saídas) e não servem de pares para ninguém. Tabela tabE_sensibilidade_sem_privado.csv.

**Segunda etapa.** Regressão truncada (ponto 1, à esquerda) da medida de Farrell corrigida sobre categoria, complexidade, porte e ano, com bootstrap reamostrando hospitais inteiros (1.000 réplicas). Nota metodológica: o algoritmo 2 integral de Simar e Wilson reestima o DEA em cada réplica; a aproximação usada parte dos escores já corrigidos pelo algoritmo 1 e preserva a dependência intra hospital, decisão documentada. A primeira execução falhou quando uma réplica perdeu um nível de fator (coeficientes desalinharam); a correção alinha por nome e descarta réplicas incompletas (fase2_dea_2etapa.R). Resultados em tabE_segunda_etapa_truncada.csv, comentados na Seção 7. Lembrete de leitura: a variável dependente é lambda (1 ou mais; maior = menos eficiente), então coeficiente negativo em categoria significa mais eficiência que a Direta.

## 5. Frente 3: SFA em painel (Battese e Coelli 1995)

**Desenho.** Fronteira de produção (log de saídas) sobre logs centrados de leitos totais, UTI (log de 1 mais UTI, pelos zeros) e valor real; dummies de ano na fronteira; equação de ineficiência com dummies de categoria, complexidade padronizada, porte e tendência linear. O **Translog vence o Cobb Douglas com folga** (LR de 651,0 com 6 graus de liberdade, p da ordem de 1e-137) e é a especificação adotada. **gamma = 0,943 (EP 0,009)**: a quase totalidade da variância composta é atribuível à ineficiência; LR de ausência de ineficiência de 2.261 (rejeitada em qualquer nível pela mistura de qui quadrados de Kodde e Palm).

**Elasticidades na média** (com logs centrados, os coeficientes de primeira ordem): leitos 0,339, valor real 0,465, UTI 0,067 negativa; **retornos de escala decrescentes, 0,737 na média**. Monotonicidade: respeitada em 84,7% das observações para leitos e 99,7% para valor, mas **violada em 76,5% das observações para o insumo de UTI**: o Translog é mal comportado nesse insumo (herança do log de 1 mais UTI com um quarto de zeros), defeito reportado como manda o protocolo, e mais um motivo para a leitura da UTI ficar com a sensibilidade sem esse insumo (tabS_sensibilidade.csv).

**Aviso central da frente: a equação de ineficiência degenera no contraste OSS.** As eficiências técnicas médias são OSS 0,999, Público Municipal 0,915, Filantrópico 0,747, Direta 0,721 (Privado 0,298, registro): as OSS ficam praticamente SOBRE a fronteira paramétrica, e o coeficiente delas na equação de ineficiência explode para 1.291 negativos com EP de 1.465 (sem input de UTI, 1.497; com Mundlak na fronteira, 836 com EP 681), um análogo da separação perfeita: a ineficiência das OSS é levada a zero e o parâmetro perde identificação. **O contraste OSS da equação z não deve ser citado como número**; a leitura válida da frente são as ordens das eficiências técnicas e o cruzamento com o DEA. A variante true fixed effects de Greene, que separaria heterogeneidade persistente de ineficiência, não está disponível nos pacotes usados; a aproximação de Mundlak na fronteira (sensibilidade) não muda o quadro.

**Cruzamento com o DEA (resultado síntese da fase).** Spearman entre as eficiências SFA e os escores DEA BCC corrigidos: **0,625 no agregado**, crescendo de 0,52 a 0,55 no início do período para 0,70 a 0,73 de 2020 em diante (tabS_cruzamento_dea.csv; dispersão em figS02, onde a faixa de OSS colada em 1,0 na SFA ilustra a degeneração descrita acima). Os dois métodos, um paramétrico e um não paramétrico, contam a mesma história ordinal: **OSS e Municipais operam mais perto da fronteira; Direta e Filantrópicos, mais longe; e a concordância entre métodos aumenta na segunda metade do período**.

## 6. Robustez transversal

Três variantes por frente (sem 2020 e 2021; sem os 5 conversores; suporte comum de faixas 3 e 4 e portes médio e grande), tabelas tabR_frente1_variantes.csv, tabR_frente2_variantes.csv, tabR_frente3_variantes.csv e tabE_segunda_etapa_log.csv (variantes do DEA na escala estável).

**Frente 1 (contraste OSS vs Direta, hierárquico).** Sem o biênio pandêmico, nada se move (mortalidade de 0,255 para 0,235 negativos; TMP de 0,108 para 0,121; produção de 0,287 para 0,267). No suporte comum, tudo mantém direção com magnitudes um pouco maiores (mortalidade 0,301 negativa; produção 0,423; ocupação 0,297). O resultado mais informativo é a variante **sem os 5 conversores** (efeito puro between): a mortalidade VIRA 0,095 positivo com EP 0,212, estatisticamente nulo. Ou seja, **a diferença de mortalidade entre as redes OSS e Direta não existe na comparação entre hospitais distintos; ela vem inteira da trajetória dos conversores**, em coerência com o termo de Mundlak positivo e não significativo e com as ressalvas de tendência do relatório principal. Já TMP (0,272 negativo), produção (0,473) e ocupação (0,241) mantêm sinal e força no puro between: o regime operacional distingue as redes mesmo sem os conversores; a mortalidade, não.

**Frente 2 (segunda etapa).** Na escala estável (log do lambda, tabE_segunda_etapa_log.csv), o coeficiente OSS é 0,536 negativo no principal (IC bootstrap de 0,891 a 0,243 negativos), 0,539 sem o biênio, **0,596 sem os conversores** e 0,477 no suporte comum (IC de 0,809 a 0,208 negativos): a eficiência maior das OSS é um traço da rede (between), não um artefato dos 5 conversores, ao contrário do que ocorre com a mortalidade. As variantes em nível (tabR_frente2_variantes.csv) repetem a patologia de escala em todas as amostras, com direção idêntica.

**Frente 3.** A degeneração do coeficiente OSS na equação de ineficiência se repete em todas as variantes (tabR_frente3_variantes.csv), como esperado com as OSS sobre a fronteira em qualquer subamostra; a frente não contribui com magnitudes para o quadro, apenas com a ordem das eficiências e o cruzamento com o DEA.

## 7. Quadro de convergência entre métodos

Contraste OSS vs Direta por indicador e método. "Frequentista" é o resultado do relatório principal (estimacao.py e inferencia_robusta.py); "hierárquico" é a Frente 1 desta fase.

| Indicador | Frequentista (relatório) | Hierárquico (fase 2) | Eficiência DEA 2a etapa | SFA | Veredito |
|---|---|---|---|---|---|
| Mortalidade | 0,230 negativo no logito, AME 1,12 p.p. negativo, p 0,085; permutação e sintético fragilizam | 0,255 negativo, IC exclui zero; bootstrap [0,465; 0,086] negativos; **between puro (sem conversores): nulo (+0,09, EP 0,21)** | não se aplica | não se aplica | converge em direção; a fase 2 REFORÇA que é fenômeno within dos conversores, sem contraparte between |
| TMP | queda de 10,2%, p 0,021 (permutação 0,153) | queda de 10,2%, IC exclui zero; between puro ainda maior (queda de 23,9%) | não se aplica | não se aplica | converge (pontualmente idêntico) |
| Custo real | queda de 6,7%, não significativa | queda de 6,7%, não significativa | não se aplica | não se aplica | converge (nulo nos dois) |
| Produção | alta de 45,4% | alta de 33,2% | (ver linha de eficiência) | (ver linha de eficiência) | converge em direção, não em magnitude (o efeito aleatório absorve parte do between) |
| Ocupação internação | alta de 23,6% | alta de 13,2%, IC cruza zero | não se aplica | não se aplica | converge em direção, não em magnitude |
| UTI intensidade | alta de 18,2% (Gama) | alta de 30,7% | não se aplica | não se aplica | converge em direção |
| Eficiência produtiva | não estimada no relatório | não se aplica | OSS com log lambda 0,536 menor (cerca de 41% menos distância à fronteira), IC exclui zero, estável nas três variantes | TE médio OSS 0,999 contra Direta 0,721; coeficiente z degenerado (não citável); Spearman DEA vs SFA 0,625 | converge em direção entre os dois métodos; magnitude interpretável só no DEA |

Síntese em uma frase: **a fase 2 confirma o retrato do relatório principal e o refina**: o regime operacional e a eficiência produtiva maiores das OSS são traços robustos da rede (aparecem em todos os métodos e variantes, inclusive no between puro), o TMP menor replica com exatidão, o custo segue nulo, e a mortalidade menor é um fenômeno exclusivo da trajetória dos conversores, sem contraparte entre redes.

## 8. Pendências e degradações

- brms/Stan não executado por ausência de toolchain de compilação (Rtools) no ambiente; a Frente 1 desceu para glmmTMB conforme a escada do protocolo; migração para intervalos de credibilidade genuínos fica pendente para ambiente com compilador.
- Variante true fixed/random effects de Greene para a SFA indisponível nos pacotes usados (frontier e sfaR sem TRE); aproximação de Mundlak na fronteira reportada como sensibilidade, sem mudança de quadro.
- Segunda etapa do DEA: algoritmo 2 de Simar e Wilson aproximado por regressão truncada sobre escores corrigidos pelo algoritmo 1 com bootstrap por hospital; a versão em NÍVEL degenera numericamente (registrada em tabE_segunda_etapa_truncada.csv e tabR_frente2_variantes.csv) e a versão em LOG é a primária.
- Coeficiente OSS da equação de ineficiência da SFA degenerado (separação: OSS sobre a fronteira); reportado como não citável.
- Insumo de UTI mal comportado no Translog (monotonicidade violada em 76% das observações) e excluído do DEA principal pelos zeros; qualquer leitura fina de UTI em eficiência pede desenho próprio.
- Primeira execução do bootstrap paramétrico da Frente 1 falhou por escopo de variáveis (update em chamada com variáveis locais); corrigida com chamada explícita; B final de 100 réplicas com salvamento incremental (custo de cerca de 22 segundos por réplica).
- A recomendação de banir complexidade_pond_mort como covariável em toda a fase segue pendente de ratificação pela pesquisadora principal.

## 9. Sugestões para a próxima rodada de escrita (sem tocar no .tex nesta rodada)

1. Nova seção de eficiência no documento, com os violinos do DEA (figE01), as TE da SFA (figS01) e a dispersão da convergência entre métodos (figS02): a mensagem acessível é que dois métodos de natureza oposta ordenam as redes do mesmo jeito, com as OSS mais perto da fronteira; o Privado ganha um parágrafo mostrando que NÃO distorce a fronteira (Spearman 1,000 sem eles).
2. Um parágrafo na seção de resultados registrando a camada hierárquica: TMP e custo replicam exatamente; produção e ocupação encolhem (between contra within); e a mortalidade between é nula sem os conversores, o que reforça a Seção 14 do documento.
3. A figura de encolhimento (figB02) como ilustração didática da regra do Privado: com partial pooling, o efeito de 3 hospitais encolhe em quase 90%.
4. Registrar em nota o achado do ajuste de complexidade no DEA: ajustar o output muda os rankings (Spearman 0,65 com o sem ajuste), mas a escolha entre o escore estrutural e o ponderado por mortalidade é de segunda ordem (0,91 entre eles), condicionada à ratificação da PI.
5. Na seção de robustez, mencionar que o quadro completo de variantes da fase 2 (três amostras por três frentes) está no pacote resultados_fase2 para consulta.
