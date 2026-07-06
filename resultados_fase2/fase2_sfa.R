# fase2_sfa.R
# Frente 3 da fase 2: fronteira estocástica de produção em painel,
# especificação Battese e Coelli (1995): fronteira Translog (testada
# contra Cobb Douglas por razão de verossimilhança) com dummies de ano
# na fronteira e equação de ineficiência com categoria de gestão,
# complexidade estrutural, porte e tendência.
#
# DECISÕES DOCUMENTADAS
# Inputs em log CENTRADO (as elasticidades na média viram os próprios
# coeficientes de primeira ordem do Translog). Leitos de UTI entram
# como log(1 + UTI) porque 25,5 por cento das observações têm UTI
# zero; sensibilidade sem esse input é reportada. A variante true
# fixed/random effects de Greene não está disponível nos pacotes de R
# utilizados (frontier, sfaR sem TRE); como aproximação documentada, a
# sensibilidade inclui médias por hospital dos insumos na fronteira
# (termo de Mundlak), separando parte da heterogeneidade persistente
# da ineficiência.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(frontier))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
FIG  <- file.path(BASE, "figuras")
TAB  <- file.path(BASE, "tabelas")
SFA  <- file.path(BASE, "sfa")

CORES_CAT <- c("Direta" = "#0d366b", "OSS" = "#0f9b8e",
               "Público Municipal" = "#5598e7",
               "Filantrópico" = "#6a51c7", "Privado" = "#898781")
CORES_CLARAS <- c("Direta" = "#9ec5f4", "OSS" = "#8fd9cf",
                  "Público Municipal" = "#c4dcf9",
                  "Filantrópico" = "#cfc4f2", "Privado" = "#d6d5d1")

painel <- preparar_painel()
d <- amostra_desfecho(painel)

d$y  <- log(d$qtde)
d$lc <- log(d$total_leitos) - mean(log(d$total_leitos))
d$uc <- log1p(d$uti_total) - mean(log1p(d$uti_total))
d$vc <- log(d$valor_real) - mean(log(d$valor_real))
d$lc2 <- 0.5 * d$lc^2; d$uc2 <- 0.5 * d$uc^2; d$vc2 <- 0.5 * d$vc^2
d$lu <- d$lc * d$uc; d$lv <- d$lc * d$vc; d$uv <- d$uc * d$vc
d$d_municipal <- as.integer(d$categoria == "Público Municipal")
d$d_filantropico <- as.integer(d$categoria == "Filantrópico")
d$d_privado <- as.integer(d$categoria == "Privado")
d$d_grande <- as.integer(d$porte_fixo == "Grande Porte")
d$d_especial <- as.integer(d$porte_fixo == "Especial")

Z <- "d_oss + d_municipal + d_filantropico + d_privado + cplx_z + d_grande + d_especial + tendencia"

# ── Cobb Douglas vs Translog (BC95) ─────────────────────────────────
f_cd <- as.formula(paste("y ~ lc + uc + vc + ano_f |", Z))
f_tl <- as.formula(paste(
  "y ~ lc + uc + vc + lc2 + uc2 + vc2 + lu + lv + uv + ano_f |", Z))

cat("\n[SFA] Cobb Douglas (BC95)\n")
m_cd <- sfa(f_cd, data = d)
cat("[SFA] Translog (BC95)\n")
m_tl <- sfa(f_tl, data = d)
saveRDS(m_cd, file.path(SFA, "modS_cobbdouglas.rds"))
saveRDS(m_tl, file.path(SFA, "modS_translog.rds"))

lr <- 2 * (logLik(m_tl) - logLik(m_cd))
p_lr <- pchisq(as.numeric(lr), df = 6, lower.tail = FALSE)
cat(sprintf("  LR Translog vs Cobb Douglas: %.1f (gl 6, p = %.2g)\n",
            as.numeric(lr), p_lr))
usar_tl <- p_lr < 0.05
m <- if (usar_tl) m_tl else m_cd
cat(sprintf("  especificação adotada: %s\n",
            if (usar_tl) "Translog" else "Cobb Douglas"))

s <- summary(m)
co <- s$mleParam
tabS <- data.frame(termo = rownames(co), coef = co[, 1], ep = co[, 2],
                   z = co[, 3], p = co[, 4], row.names = NULL)
write.csv(tabS, file.path(TAB, "tabS_fronteira_bc95.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("[TAB] tabS_fronteira_bc95.csv\n")

gama <- co["gamma", 1]
cat(sprintf("  gamma = %.3f (EP %.3f): parcela da variância composta\n",
            gama, co["gamma", 2]))
# teste LR de ausência de ineficiência (contra OLS; mistura de qui
# quadrados, valor crítico de Kodde e Palm reportado no relatório)
ll_ols <- logLik(lm(as.formula(paste(
  "y ~ lc + uc + vc + lc2 + uc2 + vc2 + lu + lv + uv + ano_f")),
  data = d))
lr_inef <- 2 * (as.numeric(logLik(m)) - as.numeric(ll_ols))
cat(sprintf("  LR de ausência de ineficiência: %.1f\n", lr_inef))

# ── elasticidades e monotonicidade ───────────────────────────────────
b <- co[, 1]
if (usar_tl) {
  # derivadas do Translog (termos quadráticos entram como 0,5 x²)
  e_l <- b["lc"] + b["lc2"] * d$lc + b["lu"] * d$uc + b["lv"] * d$vc
  e_u <- b["uc"] + b["uc2"] * d$uc + b["lu"] * d$lc + b["uv"] * d$vc
  e_v <- b["vc"] + b["vc2"] * d$vc + b["lv"] * d$lc + b["uv"] * d$uc
} else {
  e_l <- rep(b["lc"], nrow(d)); e_u <- rep(b["uc"], nrow(d))
  e_v <- rep(b["vc"], nrow(d))
}
mono <- data.frame(
  insumo = c("leitos", "uti (log1p)", "valor real"),
  elasticidade_na_media = c(b["lc"], b["uc"], b["vc"]),
  pct_obs_monotonas = c(mean(e_l > 0), mean(e_u > 0), mean(e_v > 0)),
  retornos_escala_na_media = rep(b["lc"] + b["uc"] + b["vc"], 3))
write.csv(mono, file.path(TAB, "tabS_elasticidades.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("[TAB] tabS_elasticidades.csv\n")
print(mono, digits = 3)

# ── eficiências técnicas ─────────────────────────────────────────────
d$te_sfa <- as.numeric(efficiencies(m))
agg <- aggregate(te_sfa ~ categoria + ano, data = d, FUN = mean)
write.csv(agg, file.path(TAB, "tabS_te_categoria_ano.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
agg_cat <- aggregate(te_sfa ~ categoria, data = d, FUN = mean)
cat("\n[SFA] eficiência técnica média por categoria:\n")
print(agg_cat, digits = 3)
write.csv(d[, c("cnes", "ano", "te_sfa")],
          file.path(SFA, "sfa_eficiencias.csv"), row.names = FALSE,
          fileEncoding = "UTF-8")

# violinos das TE por categoria
violino <- function(valores, at, cor_clara, cor_escura, larg = .42) {
  dd <- density(valores)
  esc_y <- larg * dd$y / max(dd$y)
  polygon(c(at - esc_y, rev(at + esc_y)), c(dd$x, rev(dd$x)),
          col = cor_clara, border = cor_escura, lwd = 1.2)
  segments(at - .12, median(valores), at + .12, median(valores),
           col = "#0b0b0b", lwd = 2)
  text(at, median(valores), sprintf("%.2f", median(valores)),
       pos = 4, offset = .8, cex = .8, col = "#0b0b0b")
}
png(file.path(FIG, "figS01_te_categoria.png"),
    width = 1350, height = 760, res = 150)
par(mar = c(6.5, 4.2, 3, 1))
ordem <- names(CORES_CAT)
plot(NA, xlim = c(.5, 5.5), ylim = c(0, 1.02), xaxt = "n", xlab = "",
     ylab = "Eficiência técnica SFA (BC95)",
     main = "Eficiência técnica da fronteira estocástica por categoria")
axis(1, at = 1:5, labels = FALSE)
text(1:5, par("usr")[3] - .06, ordem, srt = 25, adj = 1, xpd = TRUE,
     cex = .9)
for (i in seq_along(ordem)) {
  violino(d$te_sfa[d$categoria == ordem[i]], i,
          CORES_CLARAS[ordem[i]], CORES_CAT[ordem[i]])
}
mtext("O Privado (3 CNES) aparece apenas como registro, sem leitura",
      side = 1, line = 5, cex = .8, col = "#898781")
dev.off()
cat("[FIG] figS01_te_categoria.png\n")

# ── sensibilidades: sem input de UTI e quase TRE (Mundlak) ───────────
f_sem_uti <- as.formula(paste(
  "y ~ lc + vc + lc2 + vc2 + lv + ano_f |", Z))
m_semuti <- sfa(f_sem_uti, data = d)
d$m_lc <- ave(d$lc, d$cnes); d$m_uc <- ave(d$uc, d$cnes)
d$m_vc <- ave(d$vc, d$cnes)
f_mundlak <- as.formula(paste(
  "y ~ lc + uc + vc + lc2 + uc2 + vc2 + lu + lv + uv + m_lc + m_uc +",
  "m_vc + ano_f |", Z))
m_mundlak <- sfa(f_mundlak, data = d)
saveRDS(m_mundlak, file.path(SFA, "modS_mundlak.rds"))
pega_oss <- function(mm) {
  cc <- summary(mm)$mleParam
  i <- grep("d_oss", rownames(cc))
  c(coef = cc[i, 1], ep = cc[i, 2])
}
sens <- rbind(principal = pega_oss(m),
              sem_input_uti = pega_oss(m_semuti),
              quase_tre_mundlak = pega_oss(m_mundlak))
sens <- data.frame(especificacao = rownames(sens), sens,
                   row.names = NULL)
write.csv(sens, file.path(TAB, "tabS_sensibilidade.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("[TAB] tabS_sensibilidade.csv (z de ineficiência: OSS)\n")
print(sens, digits = 3)
cat("  lembrete: coeficiente NEGATIVO na equação de ineficiência",
    "significa MENOS ineficiência (mais eficiente que a Direta)\n")

# ── cruzamento com o DEA ─────────────────────────────────────────────
dea_esc <- read.csv(file.path(BASE, "dea", "dea_escores_principal.csv"),
                    fileEncoding = "UTF-8")
cr <- merge(d[, c("cnes", "ano", "te_sfa", "categoria")],
            dea_esc[, c("cnes", "ano", "te_bcc_vc")],
            by = c("cnes", "ano"))
sp_geral <- cor(cr$te_sfa, cr$te_bcc_vc, method = "spearman")
sp_ano <- sapply(split(cr, cr$ano), function(g)
  cor(g$te_sfa, g$te_bcc_vc, method = "spearman"))
cat(sprintf("\n[SFA x DEA] Spearman agregado: %.4f\n", sp_geral))
print(round(sp_ano, 3))
write.csv(data.frame(ano = c(names(sp_ano), "agregado"),
                     spearman = c(as.numeric(sp_ano), sp_geral)),
          file.path(TAB, "tabS_cruzamento_dea.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

png(file.path(FIG, "figS02_dispersao_sfa_dea.png"),
    width = 1180, height = 900, res = 150)
par(mar = c(4.4, 4.4, 3, 1))
plot(cr$te_bcc_vc, cr$te_sfa, pch = 19, cex = .45,
     col = adjustcolor(CORES_CAT[as.character(cr$categoria)], .55),
     xlab = "Eficiência DEA BCC corrigida de viés",
     ylab = "Eficiência técnica SFA (BC95)",
     main = sprintf(
       "Convergência entre métodos (Spearman %.2f)", sp_geral))
abline(0, 1, col = "#52514e", lty = 2)
legend("topleft", names(CORES_CAT), col = CORES_CAT, pch = 19,
       cex = .8, bty = "n")
dev.off()
cat("[FIG] figS02_dispersao_sfa_dea.png\n")

cat("\n[frente3] Concluída.\n")
