# fase2_dea_leitos_boot.R
# Correção de viés (Simar e Wilson, algoritmo 1, 2.000 réplicas) para o
# DEA com insumo único de leitos totais (checagem R3), pedida para que o
# marcador de divergência financeiro x físico da seleção de entrevistas
# compare duas versões igualmente corrigidas, não uma corrigida contra
# uma crua. Espelha a chamada de bootstrap do fase2_dea.R (mesma
# semente, mesmos outputs, mesma fronteira por ano).

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(Benchmarking))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
DEA  <- file.path(BASE, "dea")
NREP_BOOT <- 2000

painel <- preparar_painel()
d <- amostra_desfecho(painel)
anos <- sort(unique(d$ano))

linhas <- list()
t0 <- Sys.time()
for (a in anos) {
  da <- d[d$ano == a, ]
  X <- as.matrix(da[, "total_leitos", drop = FALSE])
  Y <- as.matrix(da[, c("qtde", "qtde_alta_complex")])
  e <- dea(X, Y, RTS = "vrs", ORIENTATION = "out")
  bb <- dea.boot(X, Y, NREP = NREP_BOOT, RTS = "vrs", ORIENTATION = "out")
  linhas[[as.character(a)]] <- data.frame(
    cnes = da$cnes, ano = a, categoria = as.character(da$categoria),
    te_bcc_leitos = 1 / e$eff, te_bcc_leitos_vc = 1 / bb$eff.bc)
  cat(sprintf("  ano %d: n = %d, TE mediana %.3f, corrigida %.3f\n",
              a, nrow(da), median(1 / e$eff), median(1 / bb$eff.bc)))
}
cat(sprintf("[DEA leitos] bootstrap total em %.1f min\n",
            as.numeric(difftime(Sys.time(), t0, units = "mins"))))
res <- do.call(rbind, linhas)
write.csv(res, file.path(DEA, "dea_escores_so_leitos_vc.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("[DEA leitos] dea_escores_so_leitos_vc.csv gravado.\n")
