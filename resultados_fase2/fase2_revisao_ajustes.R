# fase2_revisao_ajustes.R
# Ajustes pedidos pela revisão externa do pacote da fase 2:
#  R1: reajustar a variante sem conversores da mortalidade SEM o termo
#      de Mundlak na fórmula (no subconjunto sem conversores media_oss
#      é colinear com a dummy OSS e o glmmTMB descartava a coluna
#      aliased em silêncio; o coeficiente deve ser idêntico).
#  R3: sensibilidade do DEA com INSUMO ÚNICO de leitos totais (sem o
#      insumo financeiro), com Spearman contra o principal, medianas
#      por categoria e segunda etapa em log do lambda.
#  R7: Spearman DEA vs SFA excluindo as OSS (checa se a convergência
#      entre métodos não é artefato do grampo das OSS na fronteira).
#  Verificação da produção física por leito (medianas por categoria),
#      citada como atenuante do caveat do insumo valor_real.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(glmmTMB))
suppressMessages(library(Benchmarking))
suppressMessages(library(truncreg))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
TAB  <- file.path(BASE, "tabelas")
DEA  <- file.path(BASE, "dea")

painel <- preparar_painel()
d <- amostra_desfecho(painel)
conversores <- attr(painel, "conversores")

# ── R1: variante sem conversores, fórmula sem media_oss ─────────────
cat("\n[R1] mortalidade sem conversores, sem media_oss na fórmula\n")
dsw <- d[!(d$cnes %in% conversores), ]
# longa_perm só entra com variação (painel de 289: constante — ETAPA F)
TERMO_LP <- if (var(painel$longa_perm) > 0) " + longa_perm" else ""
m_r1 <- glmmTMB(as.formula(paste0(
                  "mort_all ~ categoria + cplx_z + porte_fixo",
                  TERMO_LP, " + ano_f + (1 | cnes_f)")),
                family = beta_family(),
                ziformula = ~ cplx_z + porte_fixo, data = dsw)
s <- summary(m_r1)$coefficients$cond
i <- grep("categoriaOSS", rownames(s))[1]
cat(sprintf("  coef OSS %+.4f (EP %.4f); deve coincidir com a variante sem_switchers de fase2_robustez.R (media_oss aliased)\n",
            s[i, 1], s[i, 2]))
write.csv(data.frame(especificacao = "sem_switchers_sem_mundlak",
                     coef_oss = s[i, 1], ep = s[i, 2]),
          file.path(TAB, "tabB_r1_sem_switchers.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── produção física por leito (atenuante do caveat do valor) ────────
cat("\n[verificação] produção mediana por leito, por categoria\n")
d$saidas_por_leito <- d$qtde / d$total_leitos
pl <- aggregate(saidas_por_leito ~ categoria, data = d, FUN = median)
print(pl, digits = 3)
write.csv(pl, file.path(TAB, "tabE_producao_por_leito.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── R3: DEA com insumo único de leitos ──────────────────────────────
cat("\n[R3] DEA BCC com insumo único de leitos totais\n")
anos <- sort(unique(d$ano))
linhas <- list()
for (a in anos) {
  da <- d[d$ano == a, ]
  X <- as.matrix(da[, "total_leitos", drop = FALSE])
  Y <- as.matrix(da[, c("qtde", "qtde_alta_complex")])
  e <- dea(X, Y, RTS = "vrs", ORIENTATION = "out")
  linhas[[as.character(a)]] <- data.frame(
    cnes = da$cnes, ano = a, categoria = as.character(da$categoria),
    te_bcc_leitos = 1 / e$eff)
}
so_leitos <- do.call(rbind, linhas)
esc <- read.csv(file.path(DEA, "dea_escores_principal.csv"),
                fileEncoding = "UTF-8")
m <- merge(esc[, c("cnes", "ano", "te_bcc", "te_bcc_vc")], so_leitos,
           by = c("cnes", "ano"))
sp <- cor(m$te_bcc, m$te_bcc_leitos, method = "spearman")
cat(sprintf("  Spearman com o principal (2 insumos): %.4f\n", sp))
med <- aggregate(te_bcc_leitos ~ categoria, data = so_leitos,
                 FUN = median)
print(med, digits = 3)
write.csv(so_leitos, file.path(DEA, "dea_escores_so_leitos.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# segunda etapa em log para a versão só leitos
so_leitos$log_lambda <- log(1 / so_leitos$te_bcc_leitos)
so_leitos$log_lambda <- pmax(so_leitos$log_lambda, 1e-9)
seg <- merge(so_leitos,
             unique(d[, c("cnes", "ano", "cplx_z", "porte_fixo",
                          "ano_f")]), by = c("cnes", "ano"))
seg$categoria <- factor(seg$categoria,
                        levels = c("Direta", "OSS", "Público Municipal",
                                   "Filantrópico", "Privado"))
m0 <- truncreg(log_lambda ~ categoria + cplx_z + porte_fixo + ano_f,
               data = seg, point = 0, direction = "left")
co <- coef(m0)
cn <- unique(seg$cnes)
B <- 400
bcf <- rep(NA_real_, B)
for (b in seq_len(B)) {
  am <- sample(cn, length(cn), replace = TRUE)
  db <- do.call(rbind, lapply(am, function(x) seg[seg$cnes == x, ]))
  ft <- try(truncreg(log_lambda ~ categoria + cplx_z + porte_fixo +
                       ano_f, data = db, point = 0,
                     direction = "left"), silent = TRUE)
  if (!inherits(ft, "try-error")) bcf[b] <- coef(ft)["categoriaOSS"]
}
ic <- quantile(bcf, c(.025, .975), na.rm = TRUE)
cat(sprintf("  2a etapa (log lambda, só leitos): OSS %+.4f IC [%.4f, %.4f]\n",
            co["categoriaOSS"], ic[1], ic[2]))
write.csv(data.frame(estatistica = c("spearman_vs_principal",
                                     "coef_oss_log_lambda",
                                     "ic95_lo", "ic95_hi",
                                     paste0("mediana_",
                                            gsub(" ", "_", med$categoria))),
                     valor = c(sp, co["categoriaOSS"], ic[1], ic[2],
                               med$te_bcc_leitos)),
          file.path(TAB, "tabE_sensibilidade_so_leitos.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── R7: Spearman DEA vs SFA excluindo as OSS ────────────────────────
cat("\n[R7] convergência DEA vs SFA sem as OSS\n")
sfa_te <- read.csv(file.path(BASE, "sfa", "sfa_eficiencias.csv"),
                   fileEncoding = "UTF-8")
cr <- merge(sfa_te, esc[, c("cnes", "ano", "te_bcc_vc", "categoria")],
            by = c("cnes", "ano"))
sp_todos <- cor(cr$te_sfa, cr$te_bcc_vc, method = "spearman")
sem_oss <- cr[cr$categoria != "OSS", ]
sp_semoss <- cor(sem_oss$te_sfa, sem_oss$te_bcc_vc, method = "spearman")
cat(sprintf("  Spearman com todos: %.4f | sem OSS: %.4f\n",
            sp_todos, sp_semoss))
write.csv(data.frame(amostra = c("todas_categorias", "sem_oss"),
                     spearman = c(sp_todos, sp_semoss)),
          file.path(TAB, "tabS_cruzamento_sem_oss.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

cat("\n[revisao_ajustes] Concluído.\n")
