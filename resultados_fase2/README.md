# Pacote de resultados da fase 2

Este diretório é autocontido para revisão externa: contém os scripts, os objetos de modelo, as figuras, as tabelas e o relatório de execução da fase 2 da estimação (Bayesiana hierárquica, DEA e SFA) do projeto de gestão hospitalar SUS/SP.

**Comece por `RELATORIO_EXECUCAO.md`**, que documenta ambiente, decisões, diagnósticos, resultados e pendências.

## Estrutura

- `preparo_fase2.R`: preparo comum (verificação do painel com aborto, IPCA a preços de 2025, porte fixo, exclusões vigentes, winsorização, Mundlak).
- `fase2_bayes.R`: Frente 1, modelos hierárquicos dos sete desfechos (glmmTMB; a escada brms/rstan/glmmTMB e a degradação documentada estão no relatório); `fase2_bayes_boot.R`: bootstrap paramétrico do contraste de mortalidade.
- `fase2_dea.R`: Frente 2, DEA CCR e BCC por ano com bootstrap de Simar e Wilson (2.000 réplicas), versões de output ajustadas por complexidade e sensibilidades; `fase2_dea_2etapa.R` e `fase2_dea_2etapa_log.R`: segunda etapa truncada (a versão em nível degenera e fica como registro; a versão em log é a primária).
- `fase2_sfa.R`: Frente 3, fronteira estocástica Battese e Coelli 1995 em Translog, com elasticidades, diagnósticos e cruzamento com o DEA.
- `fase2_robustez.R`: variantes transversais (sem 2020 e 2021; sem os 5 conversores; suporte comum).
- `bayes/`, `dea/`, `sfa/`: objetos de modelo (.rds) e escores para reuso.
- `figuras/`: PNG no padrão do projeto (figB, figE, figS).
- `tabelas/`: CSV com cabeçalho limpo (tabB, tabE, tabS, tabR).

## Reexecução

R 4.6 com os pacotes listados no relatório; rodar os scripts na ordem: preparo é carregado pelos demais; `fase2_dea.R` antes de `fase2_sfa.R` (o cruzamento lê os escores) e antes das segundas etapas. Sementes fixadas em 20260706; a única fonte de variação entre execuções é o bootstrap de Simar e Wilson do pacote Benchmarking quando a semente não é respeitada pelo gerador interno.

## Salvaguardas

Painel de entrada nunca é alterado; complexidade ponderada por mortalidade não entra como covariável em nenhum modelo (uso restrito ao ajuste de output do DEA, comparado com a versão estrutural); Privado (3 CNES) nunca interpretado; erros agrupados por hospital ou efeito aleatório de hospital em tudo.
