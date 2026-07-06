# fase2_robustez.R
# Robustez transversal da fase 2: reestima o contraste OSS vs Direta
# das três frentes em três variantes de amostra: (a) sem 2020 e 2021;
# (b) sem os 5 conversores (efeito puro between); (c) região de
# suporte comum (faixas Barcelona 3 e 4, portes médio e grande).
# O Privado nunca é interpretado em nenhuma variante.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(glmmTMB))
suppressMessages(library(truncreg))
suppressMessages(library(frontier))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
TAB  <- file.path(BASE, "tabelas")
B_DEA <- 400   # bootstrap reduzido nas variantes (documentado)

painel <- preparar_painel()
d0 <- amostra_desfecho(painel)
conversores <- attr(painel, "conversores")

variantes <- list(
  principal    = function(x) x,
  sem_pandemia = function(x) x[!(x$ano %in% c(2020, 2021)), ],
  sem_switchers = function(x) x[!(x$cnes %in% conversores), ],
  suporte_comum = function(x) amostra_suporte(x))

# ── Frente 1: modelos hierárquicos ───────────────────────────────────
cat("\n[robustez] Frente 1 (hierárquicos)\n")
FX <- "categoria + cplx_z + porte_fixo + longa_perm + media_oss + ano_f"
FX_TMP <- "categoria + cplx_z + porte_fixo + media_oss + ano_f"
especs <- list(
  mortalidade = list(f = paste("mort_all ~", FX, "+ (1|cnes_f)"),
                     fam = beta_family(), zi = ~ cplx_z + porte_fixo,
                     prep = function(x) x),
  tmp = list(f = paste("log(tmp) ~", FX_TMP, "+ (1|cnes_f)"),
             fam = gaussian(), zi = ~0,
             prep = function(x) x[x$longa_perm == 0, ]),
  custo = list(f = paste("log(custo_real) ~", FX, "+ (1|cnes_f)"),
               fam = gaussian(), zi = ~0, prep = function(x) x),
  producao = list(f = paste("qtde ~", FX,
                            "+ log(total_leitos) + (1|cnes_f)"),
                  fam = nbinom2(), zi = ~0, prep = function(x) x),
  ocupacao = list(f = paste("log(ocupacao_internacao_w) ~", FX,
                            "+ (1|cnes_f)"),
                  fam = gaussian(), zi = ~0, prep = function(x) x),
  uti_intensidade = list(f = paste("ocupacao_uti_w ~", FX,
                                   "+ (1|cnes_f)"),
                         fam = Gamma(link = "log"), zi = ~0,
                         prep = function(x) x[x$ocupacao_uti > 0, ]))

linhas1 <- list()
for (v in names(variantes)) {
  dv <- variantes[[v]](d0)
  for (e in names(especs)) {
    sp <- especs[[e]]
    dd <- sp$prep(dv)
    fit <- try(glmmTMB(as.formula(sp$f), family = sp$fam,
                       ziformula = sp$zi, data = dd), silent = TRUE)
    if (inherits(fit, "try-error")) {
      cat(sprintf("  %s | %s: FALHOU\n", v, e))
      next
    }
    s <- summary(fit)$coefficients$cond
    i <- grep("categoriaOSS", rownames(s))[1]
    linhas1[[paste(v, e)]] <- data.frame(
      variante = v, modelo = e, n = nrow(dd),
      coef_oss = s[i, 1], ep = s[i, 2],
      ic_lo = s[i, 1] - 1.96 * s[i, 2],
      ic_hi = s[i, 1] + 1.96 * s[i, 2])
    cat(sprintf("  %s | %-16s coef %+.4f (EP %.4f, n %d)\n",
                v, e, s[i, 1], s[i, 2], nrow(dd)))
  }
}
t1 <- do.call(rbind, linhas1)
write.csv(t1, file.path(TAB, "tabR_frente1_variantes.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── Frente 2: segunda etapa do DEA nas variantes ─────────────────────
# a fronteira por ano permanece a principal (corrigida de viés); as
# variantes filtram as observações da SEGUNDA etapa; no caso sem
# switchers os 5 hospitais também saem da regressão (a fronteira os
# mantém como pares, decisão documentada).
cat("\n[robustez] Frente 2 (segunda etapa do DEA)\n")
esc <- read.csv(file.path(BASE, "dea", "dea_escores_principal.csv"),
                fileEncoding = "UTF-8")
esc$lambda_vc <- 1 / esc$te_bcc_vc
esc <- merge(esc, unique(d0[, c("cnes", "ano", "cplx_z", "porte_fixo",
                                "ano_f", "faixa_barcelona")]),
             by = c("cnes", "ano"))
esc$categoria <- factor(esc$categoria,
                        levels = c("Direta", "OSS", "Público Municipal",
                                   "Filantrópico", "Privado"))
filtros2 <- list(
  principal    = function(x) x,
  sem_pandemia = function(x) x[!(x$ano %in% c(2020, 2021)), ],
  sem_switchers = function(x) x[!(x$cnes %in% conversores), ],
  suporte_comum = function(x)
    x[x$faixa_barcelona %in% c(3, 4) &
        x$porte_fixo %in% c("Médio Porte", "Grande Porte"), ])
linhas2 <- list()
for (v in names(filtros2)) {
  dv <- droplevels(filtros2[[v]](esc))
  m0 <- try(truncreg(lambda_vc ~ categoria + cplx_z + porte_fixo +
                       ano_f, data = dv, point = 1,
                     direction = "left"), silent = TRUE)
  if (inherits(m0, "try-error")) { cat("  ", v, ": FALHOU\n"); next }
  co <- coef(m0)
  cn <- unique(dv$cnes)
  bcf <- rep(NA_real_, B_DEA)
  for (b in seq_len(B_DEA)) {
    am <- sample(cn, length(cn), replace = TRUE)
    db <- do.call(rbind, lapply(am, function(x) dv[dv$cnes == x, ]))
    ft <- try(truncreg(lambda_vc ~ categoria + cplx_z + porte_fixo +
                         ano_f, data = db, point = 1,
                       direction = "left"), silent = TRUE)
    if (!inherits(ft, "try-error")) bcf[b] <- coef(ft)["categoriaOSS"]
  }
  ic <- quantile(bcf, c(.025, .975), na.rm = TRUE)
  linhas2[[v]] <- data.frame(variante = v, n = nrow(dv),
                             coef_oss_lambda = co["categoriaOSS"],
                             ic_lo = ic[1], ic_hi = ic[2],
                             replicas = sum(!is.na(bcf)))
  cat(sprintf("  %s: coef OSS (lambda) %+.4f IC [%.4f, %.4f] n %d\n",
              v, co["categoriaOSS"], ic[1], ic[2], nrow(dv)))
}
t2 <- do.call(rbind, linhas2)
write.csv(t2, file.path(TAB, "tabR_frente2_variantes.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── Frente 3: equação de ineficiência do SFA nas variantes ───────────
cat("\n[robustez] Frente 3 (SFA BC95)\n")
prep_sfa <- function(dd) {
  dd$y <- log(dd$qtde)
  dd$lc <- log(dd$total_leitos) - mean(log(dd$total_leitos))
  dd$uc <- log1p(dd$uti_total) - mean(log1p(dd$uti_total))
  dd$vc <- log(dd$valor_real) - mean(log(dd$valor_real))
  dd$lc2 <- .5 * dd$lc^2; dd$uc2 <- .5 * dd$uc^2; dd$vc2 <- .5 * dd$vc^2
  dd$lu <- dd$lc * dd$uc; dd$lv <- dd$lc * dd$vc; dd$uv <- dd$uc * dd$vc
  dd$d_municipal <- as.integer(dd$categoria == "Público Municipal")
  dd$d_filantropico <- as.integer(dd$categoria == "Filantrópico")
  dd$d_privado <- as.integer(dd$categoria == "Privado")
  dd$d_grande <- as.integer(dd$porte_fixo == "Grande Porte")
  dd$d_especial <- as.integer(dd$porte_fixo == "Especial")
  dd
}
f_tl <- y ~ lc + uc + vc + lc2 + uc2 + vc2 + lu + lv + uv + ano_f |
  d_oss + d_municipal + d_filantropico + d_privado + cplx_z +
  d_grande + d_especial + tendencia
linhas3 <- list()
for (v in names(variantes)) {
  dv <- prep_sfa(droplevels(variantes[[v]](d0)))
  fit <- try(sfa(f_tl, data = dv), silent = TRUE)
  if (inherits(fit, "try-error")) { cat("  ", v, ": FALHOU\n"); next }
  cc <- summary(fit)$mleParam
  i <- grep("d_oss", rownames(cc))
  linhas3[[v]] <- data.frame(variante = v, n = nrow(dv),
                             coef_oss_inef = cc[i, 1], ep = cc[i, 2],
                             p = cc[i, 4])
  cat(sprintf("  %s: OSS na ineficiência %+.3f (EP %.3f, p %.3g, n %d)\n",
              v, cc[i, 1], cc[i, 2], cc[i, 4], nrow(dv)))
}
t3 <- do.call(rbind, linhas3)
write.csv(t3, file.path(TAB, "tabR_frente3_variantes.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

cat("\n[robustez] Concluída.\n")
