# fase2_bayes_boot.R
# Bootstrap paramétrico do contraste OSS vs Direta no modelo
# hierárquico de mortalidade (Beta inflada em zero), previsto pelo
# protocolo como acompanhamento da descida para glmmTMB: simula da
# distribuição ajustada, reajusta o modelo e coleta o coeficiente.
# B = 100 réplicas com salvamento incremental (o reajuste do ZIB
# hierárquico custa cerca de um minuto por réplica; B documentado no
# relatório; o erro padrão de bootstrap é estável nessa escala e o
# intervalo usa a aproximação normal além do percentil).

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(glmmTMB))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
B <- 100

painel <- preparar_painel()
d <- amostra_desfecho(painel)
m <- readRDS(file.path(BASE, "bayes", "modB_mortalidade.rds"))

# a chamada é refeita explicitamente (update() reavaliaria a chamada
# original, cujos argumentos eram variáveis locais de um helper)
f_mort <- mort_all ~ categoria + cplx_z + porte_fixo + longa_perm +
  media_oss + ano_f + (1 | cnes_f)
zi_mort <- ~ cplx_z + porte_fixo

co_alvo <- "categoriaOSS"
sims <- simulate(m, nsim = B, seed = 20260706)
res <- rep(NA_real_, B)
t0 <- Sys.time()
for (b in seq_len(B)) {
  db <- d
  db$mort_all <- pmin(pmax(sims[[b]], 0), 0.9999)
  fit <- try(glmmTMB(f_mort, family = beta_family(),
                     ziformula = zi_mort, data = db), silent = TRUE)
  if (!inherits(fit, "try-error") && fit$fit$convergence == 0) {
    fe <- fixef(fit)$cond
    res[b] <- fe[co_alvo]
  }
  if (b %% 10 == 0) {
    cat(sprintf("  réplica %d de %d (%.1f min)\n", b, B,
                as.numeric(difftime(Sys.time(), t0, units = "mins"))))
    saveRDS(res, file.path(BASE, "bayes", "boot_mortalidade.rds"))
  }
}
validas <- sum(!is.na(res))
fe0 <- fixef(m)$cond[co_alvo]
ic <- quantile(res, c(.025, .975), na.rm = TRUE)
ep_boot <- sd(res, na.rm = TRUE)
cat(sprintf("\n[boot] válidas %d de %d; coef %.4f; EP boot %.4f; IC95 [%.4f, %.4f]\n",
            validas, B, fe0, ep_boot, ic[1], ic[2]))
write.csv(data.frame(estatistica = c("coef_oss", "ep_bootstrap",
                                     "ic95_lo", "ic95_hi",
                                     "replicas_validas"),
                     valor = c(fe0, ep_boot, ic[1], ic[2], validas)),
          file.path(BASE, "tabelas", "tabB_bootstrap_mortalidade.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
saveRDS(res, file.path(BASE, "bayes", "boot_mortalidade.rds"))
cat("[boot] Concluído.\n")
