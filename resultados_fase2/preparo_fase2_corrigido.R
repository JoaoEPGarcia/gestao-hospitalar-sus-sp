# preparo_fase2_corrigido.R
# ETAPA 5 — Preparo da Fase 2 com os defeitos de R8 corrigidos.
#
# O ORIGINAL `preparo_fase2.R` NÃO É ALTERADO. Este arquivo é uma cópia
# corrigida, com outro nome, para que os resultados publicados continuem
# reproduzíveis a partir do arquivo que os produziu. Toda divergência frente
# ao original está marcada com [R8-n] abaixo.
#
# [R8-1] WINSORIZAÇÃO CONTAMINADA — corrigido
# -------------------------------------------
# O original winsoriza AMBAS as ocupações no p99 do PAINEL COMPLETO, o que
# para a UTI inclui os 688 zeros estruturais (hospitais sem UTI SUS, onde a
# razão é indefinida e não zero). O limiar resultante é ele próprio artefato
# do bug corrigido na Etapa 1.
#   painel completo ....... p99 = 171,2
#   subamostra válida ..... p99 = 180,5   <- adotado aqui
# A winsorização da UTI passa a usar o p99 da SUBAMOSTRA VÁLIDA (uti_sus > 0),
# mesmo limiar único da Etapa 4.
#
# [R8-3] SINAL APAGADO POR WINSORIZAÇÃO — corrigido
# --------------------------------------------------
# O original winsoriza `ocupacao_internacao` no p99 (125,1), tratando como
# ruído de cauda o excesso acima de 100% — que é a assinatura aritmética da
# superlotação (R1 v4): o CNES registra capacidade habilitada e exclui leito
# extra, o SIH fatura diária para maca e leito de observação acima de 24
# horas. Winsorizar apaga o achado.
# Aqui `ocupacao_internacao` NÃO é winsorizada. Entra em DUAS PARTES (R6):
#   sobrecarga      binário, 1 se ocupacao_internacao > 100
#   ocup_int_cond   contínua restrita a <= 100 (teto por construção, sem
#                   winsorização)
#
# [R8-2] é corrigido nos scripts de modelo, não aqui: é a amostra da UTI que
# muda, de `ocupacao_uti > 0` (desfecho) para `uti_sus > 0` (capacidade).
# Este preparo fornece a marca `uti_valida` para isso.
#
# Tudo o mais é idêntico ao original: verificação do painel com aborto, IPCA
# a preços de 2025, porte fixo pela mediana de leitos, flag e exclusão do
# denominador frágil, dummy de longa permanência, termo de Mundlak.

preparar_painel_corrigido <- function(caminho) {
  painel <- read.csv(caminho, fileEncoding = "UTF-8", check.names = FALSE,
                     stringsAsFactors = FALSE)

  # verificação obrigatória: aborta se o painel não conferir
  stopifnot(length(unique(painel$cnes)) == 289,
            nrow(painel) == 3179,
            all(table(painel$cnes) == 11),
            sum(is.na(painel$modelo_gestao_proxy)) == 0,
            sum(is.na(painel$complexidade_estrutural)) == 0)
  cat("[preparo-c] Painel verificado: 289 CNES, 3.179 observações\n")

  ipca <- c("2015" = 10.67, "2016" = 6.29, "2017" = 2.95, "2018" = 3.75,
            "2019" = 4.31, "2020" = 4.52, "2021" = 10.06, "2022" = 5.79,
            "2023" = 4.62, "2024" = 4.83, "2025" = 4.26)
  indice <- cumprod(1 + ipca / 100)
  fator <- indice[length(indice)] / indice
  painel$fator_ipca <- fator[as.character(painel$ano)]
  painel$custo_real <- painel$custo_saida * painel$fator_ipca
  painel$valor_real <- painel$valor * painel$fator_ipca

  med_leitos <- tapply(painel$total_leitos, painel$cnes, median)
  porte_de <- function(x) {
    if (x <= 50) "HPP" else if (x <= 150) "Médio Porte"
    else if (x <= 500) "Grande Porte" else "Especial"
  }
  porte_cnes <- vapply(med_leitos, porte_de, character(1))
  painel$porte_fixo <- factor(porte_cnes[as.character(painel$cnes)],
                              levels = c("Médio Porte", "Grande Porte",
                                         "Especial"))

  painel$flag_fragil <- as.integer(painel$cnes == 2097613 &
                                     painel$ano %in% c(2020, 2021))
  tmp_med <- tapply(painel$tmp, painel$cnes, median)
  cnes_lp <- names(tmp_med)[tmp_med > 20]
  painel$longa_perm <- as.integer(as.character(painel$cnes) %in% cnes_lp)
  stopifnot(length(cnes_lp) == 0, sum(painel$flag_fragil) == 2)

  # ── [R8-1] winsorização da UTI na SUBAMOSTRA VÁLIDA ────────────────
  # `uti_valida` marca CAPACIDADE, não desfecho: uti_sus > 0. É a marca que
  # [R8-2] usa nos scripts de modelo.
  painel$uti_valida <- painel$uti_sus > 0
  painel$ocupacao_uti_valida <- ifelse(painel$uti_valida,
                                       painel$ocupacao_uti, NA)
  v <- painel$ocupacao_uti_valida[painel$uti_valida]
  p99_valida <- quantile(v, 0.99, names = FALSE)
  p99_contaminado <- quantile(painel$ocupacao_uti, 0.99, names = FALSE)
  painel$ocupacao_uti_w <- pmin(painel$ocupacao_uti_valida, p99_valida)
  cat(sprintf("[preparo-c][R8-1] ocupacao_uti: p99 da subamostra válida = %.1f (n=%d)\n",
              p99_valida, length(v)))
  cat(sprintf("[preparo-c][R8-1]   (o original usaria %.1f, do painel contaminado pelos %d zeros estruturais)\n",
              p99_contaminado, sum(!painel$uti_valida)))
  cat(sprintf("[preparo-c][R8-2] zeros preservados na subamostra válida: %d obs\n",
              sum(v == 0)))

  # ── [R8-3] internação em duas partes, SEM winsorização ─────────────
  painel$sobrecarga <- as.integer(painel$ocupacao_internacao > 100)
  painel$ocup_int_cond <- ifelse(painel$ocupacao_internacao <= 100,
                                 painel$ocupacao_internacao, NA)
  cat(sprintf("[preparo-c][R8-3] internação NÃO winsorizada; %d obs acima de 100%% (%.1f%%) entram como binário\n",
              sum(painel$sobrecarga), 100 * mean(painel$sobrecarga)))

  painel$categoria <- factor(painel$modelo_gestao_proxy,
                             levels = c("Direta", "OSS",
                                        "Público Municipal",
                                        "Filantrópico", "Privado"))
  painel$d_oss <- as.integer(painel$categoria == "OSS")
  painel$media_oss <- ave(painel$d_oss, painel$cnes, FUN = mean)
  painel$ano_f <- factor(painel$ano)
  painel$cnes_f <- factor(painel$cnes)
  painel$tendencia <- painel$ano - 2015
  painel$cplx_z <- as.numeric(scale(painel$complexidade_estrutural))

  attr(painel, "conversores") <- c(2081695, 2078287, 2082225, 2091755,
                                   2750511)
  painel
}

amostra_desfecho_c <- function(painel) painel[painel$flag_fragil == 0, ]

amostra_suporte_c <- function(painel) {
  painel[painel$faixa_barcelona %in% c(3, 4) &
           painel$porte_fixo %in% c("Médio Porte", "Grande Porte"), ]
}

# amostra da UTI: CAPACIDADE, não desfecho. É esta função que corrige [R8-2].
# O original usa `x[x$ocupacao_uti > 0, ]`, que remove 695 observações — as
# 688 sem UTI cadastrada MAIS 7 com UTI habilitada e zero diárias no ano.
# Essas 7 são excluídas pelo VALOR DO DESFECHO, e é isso que enviesa.
amostra_uti_capacidade <- function(painel) painel[painel$uti_valida, ]
