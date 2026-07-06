# fase2_dea_2etapa.R
# Segunda etapa do DEA, reexecutada a partir dos escores corrigidos já
# salvos por fase2_dea.R (o bootstrap de Simar e Wilson dos escores não
# é repetido). Correção em relação à primeira execução: nas réplicas
# de bootstrap em que a reamostra de hospitais perde algum nível de
# fator, os coeficientes são alinhados POR NOME e a réplica só é
# aproveitada se contiver todos os níveis (contagem reportada).

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(truncreg))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
TAB  <- file.path(BASE, "tabelas")
DEA  <- file.path(BASE, "dea")
B_SEGUNDA <- 1000

painel <- preparar_painel()
d <- amostra_desfecho(painel)

esc <- read.csv(file.path(DEA, "dea_escores_principal.csv"),
                fileEncoding = "UTF-8")
esc$lambda_vc <- 1 / esc$te_bcc_vc
esc <- merge(esc, unique(d[, c("cnes", "ano", "cplx_z", "porte_fixo",
                               "ano_f", "faixa_barcelona")]),
             by = c("cnes", "ano"))
esc$categoria <- factor(esc$categoria,
                        levels = c("Direta", "OSS", "Público Municipal",
                                   "Filantrópico", "Privado"))

ajustar_truncada <- function(dd) {
  truncreg(lambda_vc ~ categoria + cplx_z + porte_fixo + ano_f,
           data = dd, point = 1, direction = "left")
}
m0 <- ajustar_truncada(esc)
co <- coef(m0)
cat(sprintf("[2a etapa] modelo pontual ok (%d termos, n = %d)\n",
            length(co), nrow(esc)))

cn_unicos <- unique(esc$cnes)
boot_cf <- matrix(NA_real_, B_SEGUNDA, length(co),
                  dimnames = list(NULL, names(co)))
descartadas <- 0
set.seed(20260706)
t0 <- Sys.time()
for (b in seq_len(B_SEGUNDA)) {
  amostra <- sample(cn_unicos, length(cn_unicos), replace = TRUE)
  db <- do.call(rbind, lapply(amostra, function(cn)
    esc[esc$cnes == cn, ]))
  fit <- try(ajustar_truncada(db), silent = TRUE)
  if (inherits(fit, "try-error")) { descartadas <- descartadas + 1; next }
  cf <- coef(fit)
  if (!all(names(co) %in% names(cf))) { descartadas <- descartadas + 1; next }
  boot_cf[b, names(cf)] <- cf[names(cf)]
  if (b %% 200 == 0) {
    cat(sprintf("  réplica %d de %d (%.1f min)\n", b, B_SEGUNDA,
                as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  }
}
validas <- sum(!is.na(boot_cf[, 1]))
cat(sprintf("  réplicas válidas: %d de %d (descartadas por nível de "
            , validas, B_SEGUNDA),
    sprintf("fator ausente ou falha: %d)\n", descartadas))
ic <- t(apply(boot_cf, 2, quantile, c(.025, .975), na.rm = TRUE))
tab2 <- data.frame(termo = names(co), coef = co,
                   ic95_lo = ic[, 1], ic95_hi = ic[, 2],
                   row.names = NULL)
write.csv(tab2, file.path(TAB, "tabE_segunda_etapa_truncada.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
saveRDS(list(modelo = m0, boot = boot_cf),
        file.path(DEA, "dea_segunda_etapa.rds"))
cat("[TAB] tabE_segunda_etapa_truncada.csv\n")
print(tab2[grep("categoria|cplx|porte", tab2$termo), ], digits = 3)
cat("  lembrete de leitura: lambda maior = MENOS eficiente; coeficiente",
    "negativo em categoria indica mais eficiência que a Direta\n")
cat("\n[2a etapa] Concluída.\n")
