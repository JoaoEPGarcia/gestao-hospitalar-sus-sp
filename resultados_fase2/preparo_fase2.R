# preparo_fase2.R
# Preparo comum da fase 2 (Bayesiana hierárquica, DEA e SFA).
# Replica as regras vigentes do projeto: verificação do painel com
# aborto, custo e valor reais pelo IPCA a preços de 2025, porte fixo
# pela mediana de leitos, flag e exclusão do denominador frágil, dummy
# de longa permanência, winsorização das ocupações no p99 e termo de
# Mundlak (média da dummy OSS por hospital).

preparar_painel <- function(caminho = "C:/ProjetoPosDoc/analises/painel_definitivo.csv") {
  painel <- read.csv(caminho, fileEncoding = "UTF-8-BOM",
                     check.names = FALSE, stringsAsFactors = FALSE)

  # verificação obrigatória: aborta se o painel não conferir
  stopifnot(length(unique(painel$cnes)) == 314,
            nrow(painel) == 3454,
            all(table(painel$cnes) == 11),
            sum(is.na(painel$modelo_gestao_proxy)) == 0,
            sum(is.na(painel$complexidade_estrutural)) == 0)
  cat("[preparo] Painel verificado: 314 CNES, 3.454 observações\n")

  # IPCA dez sobre dez (IBGE; 2025 fechado em 4,26) e fatores para 2025
  ipca <- c("2015" = 10.67, "2016" = 6.29, "2017" = 2.95, "2018" = 3.75,
            "2019" = 4.31, "2020" = 4.52, "2021" = 10.06, "2022" = 5.79,
            "2023" = 4.62, "2024" = 4.83, "2025" = 4.26)
  indice <- cumprod(1 + ipca / 100)
  fator <- indice[length(indice)] / indice
  painel$fator_ipca <- fator[as.character(painel$ano)]
  painel$custo_real <- painel$custo_saida * painel$fator_ipca
  painel$valor_real <- painel$valor * painel$fator_ipca

  # porte fixo pela mediana de leitos (cortes 50, 150 e 500)
  med_leitos <- tapply(painel$total_leitos, painel$cnes, median)
  porte_de <- function(x) {
    if (x <= 50) "HPP" else if (x <= 150) "Médio Porte"
    else if (x <= 500) "Grande Porte" else "Especial"
  }
  porte_cnes <- vapply(med_leitos, porte_de, character(1))
  painel$porte_fixo <- factor(porte_cnes[as.character(painel$cnes)],
                              levels = c("Médio Porte", "Grande Porte",
                                         "Especial"))

  # flag de denominador frágil e dummy de longa permanência
  painel$flag_fragil <- as.integer(painel$cnes == 2097613 &
                                     painel$ano %in% c(2020, 2021))
  tmp_med <- tapply(painel$tmp, painel$cnes, median)
  cnes_lp <- names(tmp_med)[tmp_med > 20]
  painel$longa_perm <- as.integer(as.character(painel$cnes) %in% cnes_lp)
  stopifnot(length(cnes_lp) == 18, sum(painel$flag_fragil) == 2)

  # winsorização das ocupações no p99 do painel completo
  for (v in c("ocupacao_internacao", "ocupacao_uti")) {
    p99 <- quantile(painel[[v]], 0.99, names = FALSE)
    painel[[paste0(v, "_w")]] <- pmin(painel[[v]], p99)
    cat(sprintf("[preparo] %s: p99 = %.1f\n", v, p99))
  }

  # categoria com Direta como referência; Mundlak da dummy OSS
  painel$categoria <- factor(painel$modelo_gestao_proxy,
                             levels = c("Direta", "OSS",
                                        "Público Municipal",
                                        "Filantrópico", "Privado"))
  painel$d_oss <- as.integer(painel$categoria == "OSS")
  painel$media_oss <- ave(painel$d_oss, painel$cnes, FUN = mean)
  painel$ano_f <- factor(painel$ano)
  painel$cnes_f <- factor(painel$cnes)
  painel$tendencia <- painel$ano - 2015

  # complexidade padronizada (escala das priors e estabilidade numérica)
  painel$cplx_z <- as.numeric(scale(painel$complexidade_estrutural))

  # conjuntos de conversores e suporte comum (regras vigentes)
  attr(painel, "conversores") <- c(2081695, 2078287, 2082225, 2091755,
                                   2750511)
  painel
}

amostra_desfecho <- function(painel) painel[painel$flag_fragil == 0, ]

amostra_suporte <- function(painel) {
  painel[painel$faixa_barcelona %in% c(3, 4) &
           painel$porte_fixo %in% c("Médio Porte", "Grande Porte"), ]
}
