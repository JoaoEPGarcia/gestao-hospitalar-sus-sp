# fase2_dea_2etapa_log.R
# Segunda etapa do DEA na escala LOG do lambda corrigido, truncada em
# zero. Motivo documentado: na escala de nível a normal truncada
# degenera (a massa dos escores se amontoa logo acima de 1 com cauda
# longa à direita, e a máxima verossimilhança empurra a média latente
# para longe abaixo do ponto de truncagem, inflando todos os
# coeficientes em uma ordem de grandeza; ver tabE_segunda_etapa
# _truncada.csv, mantida no pacote como registro). No log a resposta é
# aproximadamente normal e o modelo é estável. Bootstrap reamostrando
# hospitais inteiros; inclui as variantes de robustez transversal.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(truncreg))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
TAB  <- file.path(BASE, "tabelas")
DEA  <- file.path(BASE, "dea")
B_PRINCIPAL <- 1000
B_VARIANTE  <- 400

painel <- preparar_painel()
d <- amostra_desfecho(painel)
conversores <- attr(painel, "conversores")

esc <- read.csv(file.path(DEA, "dea_escores_principal.csv"),
                fileEncoding = "UTF-8")
esc$log_lambda <- log(1 / esc$te_bcc_vc)
esc <- merge(esc, unique(d[, c("cnes", "ano", "cplx_z", "porte_fixo",
                               "ano_f", "faixa_barcelona")]),
             by = c("cnes", "ano"))
esc$categoria <- factor(esc$categoria,
                        levels = c("Direta", "OSS", "Público Municipal",
                                   "Filantrópico", "Privado"))
cat(sprintf("[2a etapa log] log lambda: min %.4f, mediana %.3f, max %.3f\n",
            min(esc$log_lambda), median(esc$log_lambda),
            max(esc$log_lambda)))

ajustar <- function(dd) {
  truncreg(log_lambda ~ categoria + cplx_z + porte_fixo + ano_f,
           data = dd, point = 0, direction = "left")
}

rodar <- function(dd, B, rotulo) {
  m0 <- ajustar(dd)
  co <- coef(m0)
  cn <- unique(dd$cnes)
  bcf <- matrix(NA_real_, B, length(co),
                dimnames = list(NULL, names(co)))
  for (b in seq_len(B)) {
    am <- sample(cn, length(cn), replace = TRUE)
    db <- do.call(rbind, lapply(am, function(x) dd[dd$cnes == x, ]))
    ft <- try(ajustar(db), silent = TRUE)
    if (inherits(ft, "try-error")) next
    cf <- coef(ft)
    if (!all(names(co) %in% names(cf))) next
    bcf[b, names(cf)] <- cf
  }
  ic <- t(apply(bcf, 2, quantile, c(.025, .975), na.rm = TRUE))
  list(m0 = m0, tab = data.frame(variante = rotulo, termo = names(co),
                                 coef = co, ic95_lo = ic[, 1],
                                 ic95_hi = ic[, 2],
                                 replicas_validas = sum(!is.na(bcf[, 1])),
                                 n = nrow(dd), row.names = NULL))
}

filtros <- list(
  principal    = function(x) x,
  sem_pandemia = function(x) x[!(x$ano %in% c(2020, 2021)), ],
  sem_switchers = function(x) x[!(x$cnes %in% conversores), ],
  suporte_comum = function(x)
    x[x$faixa_barcelona %in% c(3, 4) &
        x$porte_fixo %in% c("Médio Porte", "Grande Porte"), ])

todas <- list()
for (v in names(filtros)) {
  dv <- droplevels(filtros[[v]](esc))
  B <- if (v == "principal") B_PRINCIPAL else B_VARIANTE
  t0 <- Sys.time()
  r <- rodar(dv, B, v)
  todas[[v]] <- r$tab
  i <- grep("categoriaOSS", r$tab$termo)
  cat(sprintf("  %s: OSS (log lambda) %+.4f IC [%.4f, %.4f] n %d (%.1f min)\n",
              v, r$tab$coef[i], r$tab$ic95_lo[i], r$tab$ic95_hi[i],
              nrow(dv),
              as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  if (v == "principal") {
    saveRDS(r, file.path(DEA, "dea_segunda_etapa_log.rds"))
  }
}
tab <- do.call(rbind, todas)
write.csv(tab, file.path(TAB, "tabE_segunda_etapa_log.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("[TAB] tabE_segunda_etapa_log.csv\n")
print(tab[grep("categoria|cplx", tab$termo), ], digits = 3)
cat("  leitura: log lambda maior = menos eficiente; coeficiente negativo",
    "em categoria = mais eficiente que a Direta; o efeito percentual",
    "aproximado no lambda é exp(coef) menos 1\n")
cat("\n[2a etapa log] Concluída.\n")
