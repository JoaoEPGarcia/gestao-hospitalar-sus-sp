# fase2_ocupacao_familias.R
# ETAPA 5 (adendo 2) — Sensibilidade entre famílias na intensidade de UTI.
#
# A pergunta que este script responde
# -----------------------------------
# A decomposição por defeito mostrou que a atenuação de +30,4% para +26,7%
# passa pela troca de família (Gama -> Tweedie), e não pela aritmética direta
# das 7 observações que entram. Isso levanta uma suspeita séria: Gama e
# Tweedie **não diferem apenas pelos zeros**. Diferem pela função de
# variância aplicada às 2.489 observações inteiras — V(mu) = mu^2 na Gama
# contra V(mu) = mu^p na Tweedie —, e trocar de função de variância
# repondera a amostra toda.
#
# Se for esse o caso, SETE observações estariam escolhendo a família para
# duas mil e quinhentas, e a família passaria a ser a decisão que mais move
# o resultado. Isso precisa ser medido, não suposto.
#
# O TESTE DECISIVO
# ----------------
# Rodar Tweedie EXCLUINDO os zeros, sobre exatamente a mesma amostra da Gama
# publicada (n = 2.482). Aí a única diferença entre as duas é a função de
# variância. Se Tweedie-sem-zeros ≈ Tweedie-com-zeros, a diferença frente à
# Gama é função de variância e os zeros são irrelevantes ao número.
#
# Famílias comparadas
# -------------------
#   G_semzero    Gama(log), n = 2.482      <- especificação PUBLICADA
#   LN_semzero   lognormal, n = 2.482      <- âncora clássica alternativa
#   T_semzero    Tweedie(log), n = 2.482   <- TESTE DECISIVO
#   T_comzero    Tweedie(log), n = 2.489   <- especificação ATUAL
#   ZIG_comzero  ziGamma(log), n = 2.489   <- hurdle: massa em zero separada
#   H_parte1     binomial P(y>0), n = 2.489  } as duas partes explícitas
#   H_parte2     Gama(log) em y>0, n = 2.482 }
#
# Saída
# -----
#   resultados_fase2/tabelas/tabE5_sensibilidade_familias.csv

.libPaths(c(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"),
            .libPaths()))
set.seed(20260706)
suppressMessages(library(glmmTMB))

RAIZ <- "C:/Users/Pichau/Desktop/Projeto_Final/gestao-hospitalar-sus-sp-master"
TAB <- file.path(RAIZ, "resultados_fase2", "tabelas")
source(file.path(RAIZ, "resultados_fase2", "preparo_fase2_corrigido.R"))

painel <- preparar_painel_corrigido(file.path(RAIZ, "analises",
                                              "painel_definitivo.csv"))
d <- amostra_desfecho_c(painel)

TERMO_LP <- if (var(painel$longa_perm) > 0) " + longa_perm" else ""
FX <- paste0("categoria + cplx_z + porte_fixo", TERMO_LP,
             " + media_oss + ano_f")

# limiar único da subamostra válida (R8-1 corrigido)
p99 <- quantile(painel$ocupacao_uti_valida[painel$uti_valida], .99,
                names = FALSE)
d$y <- pmin(d$ocupacao_uti, p99)

cap <- d[d$uti_valida, ]                       # amostra por CAPACIDADE
pos <- d[d$ocupacao_uti > 0, ]                 # amostra por DESFECHO

# ── 1. a massa em zero, exatamente ───────────────────────────────────
n_zero <- sum(cap$y == 0)
cat("\n", strrep("=", 76), "\n", sep = "")
cat("A MASSA EM ZERO, EXATAMENTE\n")
cat(strrep("=", 76), "\n", sep = "")
cat(sprintf("  amostra por capacidade (uti_sus > 0) ....... n = %d\n", nrow(cap)))
cat(sprintf("  amostra por desfecho  (ocupacao_uti > 0) ... n = %d\n", nrow(pos)))
cat(sprintf("  ZEROS na amostra por capacidade ............ %d  (%.3f%%)\n",
            n_zero, 100 * n_zero / nrow(cap)))
cat(sprintf("\n  Os zeros são %.3f%% da amostra. Se a troca de família mover o\n",
            100 * n_zero / nrow(cap)))
cat("  coeficiente muito mais que isto, a família NÃO está sendo escolhida\n")
cat("  pelos zeros: está sendo escolhida pela função de variância.\n")

# quem são
z <- cap[cap$y == 0, c("cnes", "ano", "uti_sus", "diarias_uti",
                       "modelo_gestao_proxy")]
cat("\n  As observações com zero:\n")
print(z, row.names = FALSE)

ajustar <- function(rot, f, familia, dados, zi = ~0, nota = "") {
  m <- try(glmmTMB(as.formula(f), family = familia, ziformula = zi,
                   data = dados), silent = TRUE)
  ok <- !inherits(m, "try-error") && isTRUE(m$fit$convergence == 0) &&
    !any(is.na(sqrt(diag(vcov(m)$cond))))
  if (!ok) {
    cat(sprintf("  %-42s n=%4d  FALHOU\n", rot, nrow(dados)))
    return(data.frame(especificacao = rot, nota = nota, n = nrow(dados),
                      situacao = "FALHOU", coef_oss = NA, ep = NA,
                      ic_lo = NA, ic_hi = NA, efeito_pct = NA,
                      aic = NA, stringsAsFactors = FALSE))
  }
  s <- summary(m)$coefficients$cond
  i <- grep("categoriaOSS", rownames(s))[1]
  co <- s[i, 1]; ep <- s[i, 2]
  cat(sprintf("  %-42s n=%4d  %+.5f (EP %.4f) IC [%+.4f, %+.4f] = %+.1f%%\n",
              rot, nrow(dados), co, ep, co - 1.96 * ep, co + 1.96 * ep,
              100 * (exp(co) - 1)))
  data.frame(especificacao = rot, nota = nota, n = nrow(dados),
             situacao = "estimado", coef_oss = round(co, 5),
             ep = round(ep, 5), ic_lo = round(co - 1.96 * ep, 5),
             ic_hi = round(co + 1.96 * ep, 5),
             efeito_pct = round(100 * (exp(co) - 1), 2),
             aic = round(AIC(m), 1), stringsAsFactors = FALSE,
             row.names = NULL)
}

f_base <- paste("y ~", FX, "+ (1|cnes_f)")

cat("\n", strrep("=", 76), "\n", sep = "")
cat("SENSIBILIDADE ENTRE FAMÍLIAS\n")
cat(strrep("=", 76), "\n", sep = "")

L <- list()
L$g <- ajustar("G_semzero  Gama(log)", f_base, Gamma(link = "log"), pos,
               nota = "especificação PUBLICADA (n exclui os 7 zeros)")
L$ln <- ajustar("LN_semzero lognormal", paste("log(y) ~", FX, "+ (1|cnes_f)"),
                gaussian(), pos, nota = "âncora clássica alternativa")
L$ts <- ajustar("T_semzero  Tweedie(log)", f_base, tweedie(), pos,
                nota = "TESTE DECISIVO: mesma amostra da Gama, só muda V(mu)")
L$tc <- ajustar("T_comzero  Tweedie(log)", f_base, tweedie(), cap,
                nota = "especificação ATUAL da Etapa 5")
L$zig <- ajustar("ZIG_comzero ziGamma(log), zi=~1", f_base,
                 ziGamma(link = "log"), cap, zi = ~1,
                 nota = "hurdle: massa em zero modelada à parte")

cat("\n  duas partes explícitas (a forma usada na internação):\n")
L$h1 <- ajustar("H_parte1   binomial P(y>0)",
                paste("I(y > 0) ~", FX, "+ (1|cnes_f)"), binomial(), cap,
                nota = "parte 1: opera, dado que tem capacidade")
L$h2 <- ajustar("H_parte2   Gama(log) em y>0", f_base, Gamma(link = "log"),
                pos, nota = "parte 2: intensidade condicional (= G_semzero)")

tab <- do.call(rbind, L)
write.csv(tab, file.path(TAB, "tabE5_sensibilidade_familias.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("\n[TAB] tabE5_sensibilidade_familias.csv\n")

# ── amplitude e veredito ─────────────────────────────────────────────
cont <- tab[tab$situacao == "estimado" &
              !grepl("H_parte1", tab$especificacao), ]
cat("\n", strrep("=", 76), "\n", sep = "")
cat("AMPLITUDE ENTRE FAMÍLIAS (intensidade de UTI)\n")
cat(strrep("=", 76), "\n", sep = "")
cat(sprintf("  efeito mínimo ... %+.1f%%   (%s)\n", min(cont$efeito_pct),
            cont$especificacao[which.min(cont$efeito_pct)]))
cat(sprintf("  efeito máximo ... %+.1f%%   (%s)\n", max(cont$efeito_pct),
            cont$especificacao[which.max(cont$efeito_pct)]))
cat(sprintf("  amplitude ....... %.1f pontos percentuais\n",
            max(cont$efeito_pct) - min(cont$efeito_pct)))
todas_excluem_zero <- all(cont$ic_lo > 0)
cat(sprintf("  todas as famílias excluem o zero no IC95%%: %s\n",
            if (todas_excluem_zero) "SIM" else "NÃO"))

g <- function(k) tab[k, "coef_oss"]
cat("\n  TESTE DECISIVO — os zeros ou a função de variância?\n")
cat(sprintf("    Tweedie com zeros − Tweedie sem zeros ... %+.5f  (efeito dos ZEROS)\n",
            g("tc") - g("ts")))
cat(sprintf("    Tweedie sem zeros − Gama sem zeros ...... %+.5f  (efeito da V(mu))\n",
            g("ts") - g("g")))
cat(sprintf("    Gama publicada − Tweedie atual .......... %+.5f  (a atenuação total)\n",
            g("g") - g("tc")))
cat("\n[famílias] Concluída.\n")
