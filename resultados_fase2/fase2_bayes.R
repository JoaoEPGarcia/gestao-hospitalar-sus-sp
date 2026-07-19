# fase2_bayes.R
# Frente 1 da fase 2: contrastes principais sob especificação
# hierárquica (efeito aleatório de intercepto por hospital, Mundlak,
# dummies de ano). Escada prevista no protocolo: brms com cmdstanr;
# senão rstan; senão glmmTMB com bootstrap paramétrico, documentando a
# degradação. Este ambiente não possui toolchain de compilação
# (Rtools), condição verificada abaixo e registrada no relatório.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
source("C:/ProjetoPosDoc/resultados_fase2/preparo_fase2.R")

BASE <- "C:/ProjetoPosDoc/resultados_fase2"
FIG  <- file.path(BASE, "figuras")
TAB  <- file.path(BASE, "tabelas")
RDS  <- file.path(BASE, "bayes")

# cores da casa (paleta fria do projeto)
COR_SERIE <- "#2a78d6"; COR_APOIO <- "#0d366b"; COR_OSS <- "#0f9b8e"
COR_MUTED <- "#898781"
CORES_CAT <- c("Direta" = "#0d366b", "OSS" = "#0f9b8e",
               "Público Municipal" = "#5598e7",
               "Filantrópico" = "#6a51c7", "Privado" = "#898781")

# ── escada de backend ────────────────────────────────────────────────
tem_cmdstan <- requireNamespace("cmdstanr", quietly = TRUE)
tem_rstan   <- requireNamespace("rstan", quietly = TRUE)
tem_rtools  <- dir.exists("C:/rtools46") || dir.exists("C:/rtools45")
cat(sprintf("[escada] cmdstanr=%s rstan=%s rtools=%s\n",
            tem_cmdstan, tem_rstan, tem_rtools))
if (!tem_rtools) {
  cat("[escada] Sem toolchain de compilação: descendo para glmmTMB\n",
      "         (degradação documentada no relatório).\n")
}
library(glmmTMB)

painel <- preparar_painel()
d  <- amostra_desfecho(painel)
dt <- d[d$longa_perm == 0, ]
pos_uti <- d[d$ocupacao_uti > 0, ]
d$uti_ativa <- as.integer(d$ocupacao_uti > 0)

# ── especificações ───────────────────────────────────────────────────
# parte fixa comum: categoria, complexidade padronizada, porte, ano;
# Mundlak = media_oss (única covariável com variação within relevante);
# efeito aleatório de intercepto por hospital em tudo.
# longa_perm entra apenas com variação: no painel de 289 (ETAPA F,
# 15/07/2026) nenhum CNES tem TMP mediano > 20 e o termo constante seria
# descartado por aliasing (linhas NA nas tabelas) — exclusão explícita.
TERMO_LP <- if (var(painel$longa_perm) > 0) " + longa_perm" else ""
if (TERMO_LP == "") cat("[especificação] longa_perm sem variação —",
                        "termo excluído das fórmulas\n")
FX <- paste0("categoria + cplx_z + porte_fixo", TERMO_LP,
             " + media_oss + ano_f")
FX_TMP <- "categoria + cplx_z + porte_fixo + media_oss + ano_f"

ajustar <- function(nome, formula, familia, dados, zi = ~0,
                    transform_y = NULL) {
  cat(sprintf("\n[modelo] %s (n = %d)\n", nome, nrow(dados)))
  t0 <- Sys.time()
  m <- glmmTMB(formula, family = familia, ziformula = zi, data = dados)
  cat(sprintf("  convergiu: %s | tempo %.1fs\n",
              m$fit$convergence == 0,
              as.numeric(difftime(Sys.time(), t0, units = "secs"))))
  saveRDS(m, file.path(RDS, paste0("modB_", nome, ".rds")))
  m
}

extrair_oss <- function(m) {
  s <- summary(m)$coefficients$cond
  linha <- grep("categoriaOSS", rownames(s), value = TRUE)[1]
  c(coef = s[linha, 1], ep = s[linha, 2],
    lo = s[linha, 1] - 1.96 * s[linha, 2],
    hi = s[linha, 1] + 1.96 * s[linha, 2])
}

ppcheck <- function(m, y_obs, nome, rotulo, log_x = FALSE) {
  ok <- try({
    sims <- simulate(m, nsim = 30, seed = 20260706)
    png(file.path(FIG, paste0("figB01_ppcheck_", nome, ".png")),
        width = 1120, height = 660, res = 150)
    par(mar = c(4, 4, 3, 1))
    tr <- if (log_x) function(x) log(x[x > 0]) else function(x) x
    dy <- density(tr(y_obs))
    plot(dy, main = paste0("Checagem preditiva: ", rotulo),
         xlab = if (log_x) "Escala log" else "Escala original",
         ylab = "Densidade", col = NA)
    for (j in seq_len(ncol(sims))) {
      lines(density(tr(sims[[j]])), col = adjustcolor(COR_SERIE, 0.15))
    }
    lines(dy, col = COR_APOIO, lwd = 2.2)
    legend("topright", c("observado", "30 simulações do modelo"),
           col = c(COR_APOIO, COR_SERIE), lwd = c(2.2, 1), bty = "n",
           cex = .85)
    dev.off()
    cat("  [FIG] figB01_ppcheck_", nome, ".png\n", sep = "")
  }, silent = TRUE)
  if (inherits(ok, "try-error")) {
    cat("  [aviso] ppcheck indisponível para ", nome, ": ",
        attr(ok, "condition")$message, "\n", sep = "")
  }
}

resultados <- list()

# 1. mortalidade geral: Beta com inflação em zero
#    (no componente zi entram complexidade e porte; a categoria fica de
#    fora do zi por separação perfeita: OSS e Municipal não têm zeros)
f_mort <- as.formula(paste("mort_all ~", FX, "+ (1 | cnes_f)"))
m_mort <- ajustar("mortalidade", f_mort, beta_family(), d,
                  zi = ~ cplx_z + porte_fixo)
resultados$mortalidade <- extrair_oss(m_mort)
ppcheck(m_mort, d$mort_all, "mortalidade", "Mortalidade geral (ZIB)")

# 2. mortalidade ajustada (verificação)
f_morta <- as.formula(paste("mort_sem_excl ~", FX, "+ (1 | cnes_f)"))
m_morta <- ajustar("mortalidade_ajustada", f_morta, beta_family(), d,
                   zi = ~ cplx_z + porte_fixo)
resultados$mortalidade_ajustada <- extrair_oss(m_morta)

# 3. TMP sem longa permanência: lognormal vs Gama por AIC
dt$log_tmp <- log(dt$tmp)
f_tmp_ln <- as.formula(paste("log_tmp ~", FX_TMP, "+ (1 | cnes_f)"))
m_tmp <- ajustar("tmp_lognormal", f_tmp_ln, gaussian(), dt)
f_tmp_g <- as.formula(paste("tmp ~", FX_TMP, "+ (1 | cnes_f)"))
m_tmp_g <- ajustar("tmp_gama", f_tmp_g, Gamma(link = "log"), dt)
cat(sprintf("  comparação TMP: AIC lognormal (no log) %.0f vs Gama %.0f\n",
            AIC(m_tmp) + 2 * sum(dt$log_tmp), AIC(m_tmp_g)))
resultados$tmp <- extrair_oss(m_tmp)
ppcheck(m_tmp, dt$log_tmp, "tmp", "TMP no log (hierárquico)")

# 4. faturamento real: lognormal vs Gama
d$log_custo <- log(d$custo_real)
f_cus_ln <- as.formula(paste("log_custo ~", FX, "+ (1 | cnes_f)"))
m_cus <- ajustar("custo_lognormal", f_cus_ln, gaussian(), d)
f_cus_g <- as.formula(paste("custo_real ~", FX, "+ (1 | cnes_f)"))
m_cus_g <- ajustar("custo_gama", f_cus_g, Gamma(link = "log"), d)
cat(sprintf("  comparação custo: AIC lognormal (no log) %.0f vs Gama %.0f\n",
            AIC(m_cus) + 2 * sum(d$log_custo), AIC(m_cus_g)))
resultados$custo <- extrair_oss(m_cus)
ppcheck(m_cus, d$log_custo, "custo", "Faturamento real no log (hierárquico)")

# 5. produção: Binomial Negativa com log de leitos
d$log_leitos <- log(d$total_leitos)
f_prod <- as.formula(paste("qtde ~", FX, "+ log_leitos + (1 | cnes_f)"))
m_prod <- ajustar("producao", f_prod, nbinom2(), d)
resultados$producao <- extrair_oss(m_prod)
ppcheck(m_prod, d$qtde, "producao", "Produção (BN hierárquica)",
        log_x = TRUE)

# 6. ocupação de internação: lognormal na razão winsorizada
d$log_ocup <- log(d$ocupacao_internacao_w)
f_oc <- as.formula(paste("log_ocup ~", FX, "+ (1 | cnes_f)"))
m_oc <- ajustar("ocupacao_internacao", f_oc, gaussian(), d)
resultados$ocupacao_internacao <- extrair_oss(m_oc)
ppcheck(m_oc, d$log_ocup, "ocup_internacao",
        "Ocupação internação no log")

# 7. UTI em duas partes: Bernoulli e Gama nos positivos
f_uti1 <- as.formula(paste("uti_ativa ~ categoria + cplx_z + porte_fixo",
                           "+ ano_f + (1 | cnes_f)"))
m_uti1 <- ajustar("uti_parte1", f_uti1, binomial(), d)
f_uti2 <- as.formula(paste("ocupacao_uti_w ~", FX, "+ (1 | cnes_f)"))
m_uti2 <- ajustar("uti_parte2_gama", f_uti2, Gamma(link = "log"),
                  pos_uti)
resultados$uti_parte1 <- extrair_oss(m_uti1)
resultados$uti_parte2 <- extrair_oss(m_uti2)
ppcheck(m_uti2, pos_uti$ocupacao_uti_w, "uti_positivos",
        "Ocupação UTI positivos (Gama)")

# ── tabela dos contrastes hierárquicos ───────────────────────────────
tab <- do.call(rbind, resultados)
tab <- data.frame(modelo = rownames(tab), tab, row.names = NULL)
tab$efeito_pct <- ifelse(tab$modelo %in% c("mortalidade",
                                           "mortalidade_ajustada",
                                           "uti_parte1"),
                         NA, 100 * (exp(tab$coef) - 1))
write.csv(tab, file.path(TAB, "tabB_modelos_hierarquicos.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("\n[TAB] tabB_modelos_hierarquicos.csv\n")
print(tab, digits = 3)

# ── comparação com os resultados frequentistas do relatório ─────────
freq <- read.csv("C:/ProjetoPosDoc/analises/tabelas/tab_est_resumo_oss.csv",
                 fileEncoding = "UTF-8-BOM")
mapa <- c("Mortalidade (geral)" = "mortalidade",
          "Fração alta complexidade" = NA,
          "Faturamento real por saída (log)" = "custo",
          "TMP (log, sem longa perm.)" = "tmp",
          "Produção (saídas)" = "producao",
          "Ocupação internação" = "ocupacao_internacao",
          "Ocupação UTI (intensidade)" = "uti_parte2")
freq$chave <- mapa[freq$modelo]
comp <- merge(freq[!is.na(freq$chave),
                   c("modelo", "chave", "coef_oss", "ep_cluster")],
              tab, by.x = "chave", by.y = "modelo")
names(comp) <- c("chave", "modelo_relatorio", "coef_freq", "ep_freq",
                 "coef_hier", "ep_hier", "ic95_lo_hier", "ic95_hi_hier",
                 "efeito_pct_hier")
comp$ic95_lo_freq <- comp$coef_freq - 1.96 * comp$ep_freq
comp$ic95_hi_freq <- comp$coef_freq + 1.96 * comp$ep_freq
write.csv(comp, file.path(TAB, "tabB_comparacao_freq_bayes.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("[TAB] tabB_comparacao_freq_bayes.csv\n")

# ── encolhimento: categoria como efeito aleatório (partial pooling) ──
# sem pooling: dummies fixas de categoria; com pooling: (1|categoria).
# O Privado (3 CNES) é o caso de demonstração, nunca resultado.
m_fixo <- glmmTMB(as.formula(paste0(
                    "mort_all ~ 0 + categoria + cplx_z + porte_fixo",
                    TERMO_LP, " + ano_f + (1 | cnes_f)")),
                  family = beta_family(), ziformula = ~ cplx_z,
                  data = d)
m_rand <- glmmTMB(as.formula(paste0(
                    "mort_all ~ cplx_z + porte_fixo", TERMO_LP,
                    " + ano_f + (1 | categoria) + (1 | cnes_f)")),
                  family = beta_family(), ziformula = ~ cplx_z,
                  data = d)
saveRDS(m_fixo, file.path(RDS, "modB_encolhimento_fixo.rds"))
saveRDS(m_rand, file.path(RDS, "modB_encolhimento_aleatorio.rds"))
fe <- fixef(m_fixo)$cond
ef_fixo <- fe[grep("^categoria", names(fe))]
names(ef_fixo) <- sub("^categoria", "", names(ef_fixo))
ef_fixo_c <- ef_fixo - mean(ef_fixo)
re <- ranef(m_rand)$cond$categoria
ef_rand <- setNames(re[["(Intercept)"]], rownames(re))
ordem <- names(CORES_CAT)
png(file.path(FIG, "figB02_encolhimento_categorias.png"),
    width = 1180, height = 700, res = 150)
par(mar = c(4.2, 11, 3, 2))
ys <- rev(seq_along(ordem))
plot(NA, xlim = range(c(ef_fixo_c, ef_rand)) * 1.25,
     ylim = c(.5, length(ordem) + .5), yaxt = "n",
     xlab = "Efeito de categoria no logito da mortalidade (centrado)",
     ylab = "", main = "Encolhimento por partial pooling: efeitos de categoria")
axis(2, at = ys, labels = ordem, las = 1, cex.axis = .95)
abline(v = 0, col = COR_MUTED, lty = 2)
for (i in seq_along(ordem)) {
  cat_i <- ordem[i]
  segments(ef_fixo_c[cat_i], ys[i], ef_rand[cat_i], ys[i],
           col = "#e1e0d9", lwd = 3)
  points(ef_fixo_c[cat_i], ys[i], pch = 19, col = COR_APOIO, cex = 1.4)
  points(ef_rand[cat_i], ys[i], pch = 15, col = COR_OSS, cex = 1.4)
}
legend("bottomright", c("sem pooling (dummies fixas)",
                        "com pooling (efeito aleatório)"),
       pch = c(19, 15), col = c(COR_APOIO, COR_OSS), bty = "n", cex = .9)
dev.off()
cat("[FIG] figB02_encolhimento_categorias.png\n")
enc <- data.frame(categoria = ordem,
                  sem_pooling = as.numeric(ef_fixo_c[ordem]),
                  com_pooling = as.numeric(ef_rand[ordem]))
enc$encolhimento_pct <- 100 * (1 - abs(enc$com_pooling) /
                                 abs(enc$sem_pooling))
write.csv(enc, file.path(TAB, "tabB_encolhimento.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

# ── sensibilidade da mortalidade (substituto documentado das priors) ─
# sem priors no glmmTMB, a sensibilidade testa a especificação:
# (a) sem o termo de Mundlak; (b) com efeito aleatório de ano;
# o bootstrap paramétrico roda em script próprio (fase2_bayes_boot.R).
m_sem_mundlak <- glmmTMB(as.formula(paste0(
                           "mort_all ~ categoria + cplx_z + porte_fixo",
                           TERMO_LP, " + ano_f + (1 | cnes_f)")),
                         family = beta_family(),
                         ziformula = ~ cplx_z + porte_fixo, data = d)
m_re_ano <- glmmTMB(as.formula(paste0(
                      "mort_all ~ categoria + cplx_z + porte_fixo",
                      TERMO_LP,
                      " + media_oss + (1 | ano_f) + (1 | cnes_f)")),
                    family = beta_family(),
                    ziformula = ~ cplx_z + porte_fixo, data = d)
sens <- rbind(principal = resultados$mortalidade,
              sem_mundlak = extrair_oss(m_sem_mundlak),
              re_de_ano = extrair_oss(m_re_ano))
sens <- data.frame(especificacao = rownames(sens), sens,
                   row.names = NULL)
write.csv(sens, file.path(TAB, "tabB_sensibilidade_mortalidade.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("[TAB] tabB_sensibilidade_mortalidade.csv\n")
print(sens, digits = 3)

cat("\n[frente1] Concluída.\n")
