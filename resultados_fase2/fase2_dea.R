# fase2_dea.R
# Frente 2 da fase 2: DEA CCR e BCC com orientação a output, fronteira
# estimada POR ANO (evita contaminar a comparação com mudança
# tecnológica e torna o bootstrap tratável), correção de viés por
# bootstrap de Simar e Wilson (algoritmo 1, 2.000 réplicas) e segunda
# etapa em regressão truncada com bootstrap por hospital.
#
# DECISÕES DOCUMENTADAS
# Inputs: leitos totais e valor total real (recursos financeiros a
# preços de 2025). Os leitos de UTI, sugeridos no protocolo, ficam de
# fora do conjunto principal por dois motivos verificados no painel:
# 25,5 por cento das observações têm UTI igual a zero (o DEA exige
# inputs positivos para o bootstrap) e os leitos de UTI são
# subconjunto dos leitos totais. Uma sensibilidade com o input de UTI
# na subamostra com UTI ativa é reportada.
# Outputs: saídas totais e saídas de alta complexidade (zeros em
# output são admissíveis no DEA). Versões de produção ajustada por
# complexidade: saídas multiplicadas pelo escore normalizado (média 1),
# nas duas versões do escore (estrutural e ponderada por mortalidade;
# esta última é lícita AQUI porque é output de produção, não
# covariável de mortalidade), com comparação de rankings por Spearman.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(Benchmarking))
suppressMessages(library(truncreg))
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
FIG  <- file.path(BASE, "figuras")
TAB  <- file.path(BASE, "tabelas")
DEA  <- file.path(BASE, "dea")
NREP_BOOT <- 2000
B_SEGUNDA <- 1000

CORES_CAT <- c("Direta" = "#0d366b", "OSS" = "#0f9b8e",
               "Público Municipal" = "#5598e7",
               "Filantrópico" = "#6a51c7", "Privado" = "#898781")
CORES_CLARAS <- c("Direta" = "#9ec5f4", "OSS" = "#8fd9cf",
                  "Público Municipal" = "#c4dcf9",
                  "Filantrópico" = "#cfc4f2", "Privado" = "#d6d5d1")

painel <- preparar_painel()
d <- amostra_desfecho(painel)
med_cplx_e <- mean(d$complexidade_estrutural)
med_cplx_p <- mean(d$complexidade_pond_mort)
d$qtde_adj_estr <- d$qtde * d$complexidade_estrutural / med_cplx_e
d$qtde_adj_pond <- d$qtde * d$complexidade_pond_mort / med_cplx_p

anos <- sort(unique(d$ano))

rodar_dea_ano <- function(dd, col_out1, com_boot = FALSE,
                          sem_privado = FALSE, com_uti = FALSE) {
  # devolve, por ano, escores BCC e CCR (Farrell output, convertidos
  # para eficiência técnica em 0 a 1) e, se pedido, o viés corrigido
  linhas <- list()
  for (a in anos) {
    da <- dd[dd$ano == a, ]
    if (sem_privado) da <- da[da$categoria != "Privado", ]
    if (com_uti) da <- da[da$uti_total > 0, ]
    X <- as.matrix(da[, c("total_leitos", "valor_real")])
    if (com_uti) X <- cbind(X, uti = da$uti_total)
    Y <- as.matrix(da[, c(col_out1, "qtde_alta_complex")])
    e_vrs <- dea(X, Y, RTS = "vrs", ORIENTATION = "out")
    e_crs <- dea(X, Y, RTS = "crs", ORIENTATION = "out")
    te_vrs <- 1 / e_vrs$eff          # Farrell out >= 1 -> TE em (0,1]
    te_crs <- 1 / e_crs$eff
    lin <- data.frame(cnes = da$cnes, ano = a,
                      categoria = as.character(da$categoria),
                      te_bcc = te_vrs, te_ccr = te_crs,
                      ef_escala = te_crs / te_vrs)
    if (com_boot) {
      bb <- dea.boot(X, Y, NREP = NREP_BOOT, RTS = "vrs",
                     ORIENTATION = "out")
      lin$te_bcc_vc <- 1 / bb$eff.bc   # viés corrigido
      lin$vies <- 1 / bb$eff.bc - te_vrs
    }
    linhas[[as.character(a)]] <- lin
    cat(sprintf("  ano %d: n = %d, TE BCC mediana %.3f%s\n", a,
                nrow(da), median(te_vrs),
                if (com_boot) sprintf(", corrigida %.3f",
                                      median(lin$te_bcc_vc)) else ""))
  }
  do.call(rbind, linhas)
}

# ── principal: com bootstrap de vies (BCC) ───────────────────────────
cat("\n[DEA] principal (outputs sem ajuste), com bootstrap",
    NREP_BOOT, "réplicas por ano\n")
t0 <- Sys.time()
esc <- rodar_dea_ano(d, "qtde", com_boot = TRUE)
cat(sprintf("[DEA] bootstrap total em %.1f min\n",
            as.numeric(difftime(Sys.time(), t0, units = "mins"))))
saveRDS(esc, file.path(DEA, "dea_escores_principal.rds"))
write.csv(esc, file.path(DEA, "dea_escores_principal.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── versões de output ajustado por complexidade (sem bootstrap) ─────
cat("\n[DEA] outputs ajustados por complexidade\n")
esc_estr <- rodar_dea_ano(d, "qtde_adj_estr")
esc_pond <- rodar_dea_ano(d, "qtde_adj_pond")
sp_estr <- cor(esc$te_bcc, esc_estr$te_bcc, method = "spearman")
sp_pond <- cor(esc$te_bcc, esc_pond$te_bcc, method = "spearman")
sp_entre <- cor(esc_estr$te_bcc, esc_pond$te_bcc, method = "spearman")
cat(sprintf("  Spearman sem ajuste vs estrutural: %.4f\n", sp_estr))
cat(sprintf("  Spearman sem ajuste vs ponderada:  %.4f\n", sp_pond))
cat(sprintf("  Spearman estrutural vs ponderada:  %.4f\n", sp_entre))
write.csv(data.frame(par = c("sem_ajuste_vs_estrutural",
                             "sem_ajuste_vs_ponderada",
                             "estrutural_vs_ponderada"),
                     spearman = c(sp_estr, sp_pond, sp_entre)),
          file.path(TAB, "tabE_spearman_ajuste_output.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── sensibilidade: sem os 3 CNES Privados e com input de UTI ─────────
cat("\n[DEA] sensibilidade sem Privados\n")
esc_sp <- rodar_dea_ano(d, "qtde", sem_privado = FALSE)
esc_semp <- rodar_dea_ano(d, "qtde", sem_privado = TRUE)
base_np <- esc[esc$categoria != "Privado", c("cnes", "ano", "te_bcc")]
names(base_np)[3] <- "te_com_privado"
m <- merge(base_np, esc_semp[, c("cnes", "ano", "te_bcc")],
           by = c("cnes", "ano"))
delta <- m$te_bcc - m$te_com_privado
cat(sprintf("  fronteira sem Privados: TE médio sobe %.4f (máximo %.4f);",
            mean(delta), max(delta)),
    sprintf("Spearman %.4f\n",
            cor(m$te_com_privado, m$te_bcc, method = "spearman")))
write.csv(data.frame(medida = c("delta_medio_te", "delta_maximo_te",
                                "spearman_rankings",
                                "obs_afetadas_acima_001"),
                     valor = c(mean(delta), max(delta),
                               cor(m$te_com_privado, m$te_bcc,
                                   method = "spearman"),
                               mean(delta > 0.01))),
          file.path(TAB, "tabE_sensibilidade_sem_privado.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

cat("\n[DEA] sensibilidade com input de UTI (subamostra UTI ativa)\n")
esc_uti <- rodar_dea_ano(d, "qtde", com_uti = TRUE)
m2 <- merge(esc[, c("cnes", "ano", "te_bcc")],
            esc_uti[, c("cnes", "ano", "te_bcc")],
            by = c("cnes", "ano"), suffixes = c("", "_uti"))
cat(sprintf("  Spearman com vs sem input de UTI (subamostra): %.4f\n",
            cor(m2$te_bcc, m2$te_bcc_uti, method = "spearman")))

# ── medianas por categoria e ano ─────────────────────────────────────
agg <- aggregate(cbind(te_bcc, te_bcc_vc, te_ccr, ef_escala) ~
                   categoria + ano, data = esc, FUN = median)
write.csv(agg, file.path(TAB, "tabE_eficiencia_categoria_ano.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
agg_cat <- aggregate(cbind(te_bcc, te_bcc_vc, te_ccr, ef_escala) ~
                       categoria, data = esc, FUN = median)
cat("\n[DEA] medianas por categoria (período completo):\n")
print(agg_cat, digits = 3)

# ── violinos dos escores corrigidos por categoria ────────────────────
violino <- function(valores, at, cor_clara, cor_escura, larg = .42) {
  dd <- density(valores, from = min(valores), to = max(valores))
  esc_y <- larg * dd$y / max(dd$y)
  polygon(c(at - esc_y, rev(at + esc_y)), c(dd$x, rev(dd$x)),
          col = cor_clara, border = cor_escura, lwd = 1.2)
  segments(at - .12, median(valores), at + .12, median(valores),
           col = "#0b0b0b", lwd = 2)
  text(at, median(valores), sprintf("%.2f", median(valores)),
       pos = 4, offset = .8, cex = .8, col = "#0b0b0b")
}
png(file.path(FIG, "figE01_violino_te_categoria.png"),
    width = 1350, height = 760, res = 150)
par(mar = c(6.5, 4.2, 3, 1))
ordem <- names(CORES_CAT)
plot(NA, xlim = c(.5, 5.5), ylim = c(0, 1.02), xaxt = "n",
     xlab = "", ylab = "Eficiência técnica BCC corrigida de viés",
     main = "Eficiência DEA corrigida (Simar e Wilson) por categoria")
axis(1, at = 1:5, labels = FALSE)
text(1:5, par("usr")[3] - .06, ordem, srt = 25, adj = 1, xpd = TRUE,
     cex = .9)
for (i in seq_along(ordem)) {
  v <- esc$te_bcc_vc[esc$categoria == ordem[i]]
  violino(v, i, CORES_CLARAS[ordem[i]], CORES_CAT[ordem[i]])
}
mtext("O Privado (3 CNES) aparece apenas como registro, sem leitura",
      side = 1, line = 5, cex = .8, col = "#898781")
dev.off()
cat("[FIG] figE01_violino_te_categoria.png\n")

# ── segunda etapa: regressão truncada com bootstrap por hospital ─────
# Nota metodológica registrada: o algoritmo 2 completo de Simar e
# Wilson reestima o DEA em cada réplica; aqui a fronteira por ano já é
# corrigida de viés pelo algoritmo 1 e a segunda etapa usa regressão
# truncada sobre a medida de Farrell corrigida (lambda >= 1) com
# bootstrap reamostrando HOSPITAIS inteiros (1.000 réplicas), o que
# preserva a dependência intra hospital. Nunca Tobit nem OLS.
cat("\n[DEA] segunda etapa: truncada com bootstrap por hospital\n")
seg <- esc
seg$lambda_vc <- 1 / seg$te_bcc_vc          # Farrell corrigido >= 1
seg <- merge(seg, unique(d[, c("cnes", "ano", "cplx_z", "porte_fixo",
                               "ano_f", "faixa_barcelona")]),
             by = c("cnes", "ano"))
seg$categoria <- factor(seg$categoria, levels = names(CORES_CAT))

ajustar_truncada <- function(dd) {
  truncreg(lambda_vc ~ categoria + cplx_z + porte_fixo + ano_f,
           data = dd, point = 1, direction = "left")
}
m0 <- ajustar_truncada(seg)
co <- coef(m0)

cn_unicos <- unique(seg$cnes)
boot_cf <- matrix(NA_real_, B_SEGUNDA, length(co),
                  dimnames = list(NULL, names(co)))
set.seed(20260706)
for (b in seq_len(B_SEGUNDA)) {
  amostra <- sample(cn_unicos, length(cn_unicos), replace = TRUE)
  db <- do.call(rbind, lapply(amostra, function(cn)
    seg[seg$cnes == cn, ]))
  fit <- try(ajustar_truncada(db), silent = TRUE)
  if (!inherits(fit, "try-error")) boot_cf[b, ] <- coef(fit)
}
validas <- sum(!is.na(boot_cf[, 1]))
cat(sprintf("  réplicas válidas: %d de %d\n", validas, B_SEGUNDA))
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

cat("\n[frente2] Concluída.\n")
