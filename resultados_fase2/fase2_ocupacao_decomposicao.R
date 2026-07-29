# fase2_ocupacao_decomposicao.R
# ETAPA 5 (adendo) — Efeito ISOLADO de cada defeito de R8.
#
# Por que este script existe
# --------------------------
# O primeiro fechamento da Etapa 5 disse "moveu pouco" a partir do resultado
# CONJUNTO das três correções. Isso estabelece o ponto para o defeito 2, cuja
# aritmética é visível (7 observações em 2.489), e apenas PRESUME para os
# defeitos 1 e 3, que não mudam inclusão e sim limiar, atingindo a cauda
# superior. Presunção não é medida. Aqui cada defeito é corrigido
# isoladamente.
#
# Quantas observações cada defeito toca
# -------------------------------------
#   [R8-1] limiar da UTI 171,3 -> 180,5: 32 observações mudam de VALOR
#          (as 32 aparadas pelo limiar antigo); 7 delas deixam de ser aparadas
#   [R8-2] amostra da UTI 2.482 -> 2.489: 7 observações ENTRAM
#   [R8-3] limiar da internação 125,1: 32 observações aparadas — mas a
#          reorganização em duas partes toca as 492 acima de 100
#
# Desenho da decomposição
# -----------------------
# UTI: fatorial 2x2 (limiar x amostra) com a FAMÍLIA MANTIDA FIXA em Tweedie.
# Manter a família fixa é o ponto: a Gama do original não admite zero, então
# trocar a amostra para capacidade obrigaria a trocar de família junto, e o
# efeito do defeito 2 ficaria confundido com o da família. A Gama entra à
# parte, como âncora que reproduz o publicado.
#
# Internação: três formas, para separar "tirar a winsorização" de "mudar a
# forma funcional" — são coisas diferentes e R8 pede as duas.
#   I0  log winsorizado em 125,1        (original)
#   I1  log SEM winsorização, modelo único   <- isola a winsorização
#   I2  duas partes (R6)                     <- isola a forma funcional
#
# Saída
# -----
#   resultados_fase2/tabelas/tabE5_decomposicao_defeitos.csv

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

p99_contaminado <- quantile(painel$ocupacao_uti, .99, names = FALSE)
p99_valido <- quantile(painel$ocupacao_uti_valida[painel$uti_valida], .99,
                       names = FALSE)
p99_int <- quantile(d$ocupacao_internacao, .99, names = FALSE)

ajustar <- function(rotulo, f, familia, dados, log_escala = TRUE, nota = "") {
  m <- try(glmmTMB(as.formula(f), family = familia, data = dados),
           silent = TRUE)
  ok <- !inherits(m, "try-error") && isTRUE(m$fit$convergence == 0) &&
    !any(is.na(sqrt(diag(vcov(m)$cond))))
  if (!ok) {
    cat(sprintf("  %-52s FALHOU\n", rotulo))
    return(data.frame(modelo = rotulo, nota = nota, n = nrow(dados),
                      situacao = "FALHOU", coef_oss = NA, ep = NA,
                      ic_lo = NA, ic_hi = NA, efeito_pct = NA,
                      stringsAsFactors = FALSE))
  }
  s <- summary(m)$coefficients$cond
  i <- grep("categoriaOSS", rownames(s))[1]
  co <- s[i, 1]; ep <- s[i, 2]
  cat(sprintf("  %-52s %+.5f (EP %.4f) IC [%+.4f, %+.4f]%s\n", rotulo, co, ep,
              co - 1.96 * ep, co + 1.96 * ep,
              if (log_escala) sprintf(" = %+.1f%%", 100 * (exp(co) - 1)) else ""))
  data.frame(modelo = rotulo, nota = nota, n = nrow(dados),
             situacao = "estimado", coef_oss = round(co, 5),
             ep = round(ep, 5), ic_lo = round(co - 1.96 * ep, 5),
             ic_hi = round(co + 1.96 * ep, 5),
             efeito_pct = if (log_escala) round(100 * (exp(co) - 1), 2) else NA,
             stringsAsFactors = FALSE, row.names = NULL)
}

linhas <- list()

# ══════════════════════════════════════════════════════════════════════
# UTI — fatorial 2x2, família FIXA em Tweedie
# ══════════════════════════════════════════════════════════════════════
cat("\n", strrep("=", 76), "\n", sep = "")
cat("UTI — limiar x amostra, família FIXA em Tweedie\n")
cat(strrep("=", 76), "\n", sep = "")

d$uti_w_contaminado <- pmin(d$ocupacao_uti, p99_contaminado)
d$uti_w_valido <- pmin(d$ocupacao_uti, p99_valido)
am_desfecho <- d[d$ocupacao_uti > 0, ]          # defeituoso: condiciona no y
am_capacidade <- d[d$uti_valida, ]              # correto: capacidade

linhas$t00 <- ajustar("T00 limiar contaminado + amostra por DESFECHO",
                      paste("uti_w_contaminado ~", FX, "+ (1|cnes_f)"),
                      tweedie(), am_desfecho,
                      nota = "os dois defeitos presentes (referência Tweedie)")
linhas$t10 <- ajustar("T10 limiar CORRIGIDO + amostra por desfecho",
                      paste("uti_w_valido ~", FX, "+ (1|cnes_f)"),
                      tweedie(), am_desfecho,
                      nota = "isola R8-1 (limiar): 32 obs mudam de valor")
linhas$t01 <- ajustar("T01 limiar contaminado + amostra por CAPACIDADE",
                      paste("uti_w_contaminado ~", FX, "+ (1|cnes_f)"),
                      tweedie(), am_capacidade,
                      nota = "isola R8-2 (amostra): 7 obs entram")
linhas$t11 <- ajustar("T11 limiar CORRIGIDO + amostra por CAPACIDADE",
                      paste("uti_w_valido ~", FX, "+ (1|cnes_f)"),
                      tweedie(), am_capacidade,
                      nota = "os dois corrigidos")

cat("\n  âncora na família original (Gama, só admite y > 0):\n")
linhas$g00 <- ajustar("G00 Gama, limiar contaminado, amostra por desfecho",
                      paste("uti_w_contaminado ~", FX, "+ (1|cnes_f)"),
                      Gamma(link = "log"), am_desfecho,
                      nota = "reproduz o publicado (+0,26514)")

# ══════════════════════════════════════════════════════════════════════
# INTERNAÇÃO — winsorização vs forma funcional
# ══════════════════════════════════════════════════════════════════════
cat("\n", strrep("=", 76), "\n", sep = "")
cat("INTERNAÇÃO — separar 'tirar a winsorização' de 'mudar a forma'\n")
cat(strrep("=", 76), "\n", sep = "")

d$int_w <- pmin(d$ocupacao_internacao, p99_int)
linhas$i0 <- ajustar("I0 log winsorizado em 125,1 (original)",
                     paste("log(int_w) ~", FX, "+ (1|cnes_f)"),
                     gaussian(), d, nota = "reproduz o publicado (+0,11802)")
linhas$i1 <- ajustar("I1 log SEM winsorização, modelo único",
                     paste("log(ocupacao_internacao) ~", FX, "+ (1|cnes_f)"),
                     gaussian(), d,
                     nota = "isola R8-3a: só tira o corte, mantém a forma")
linhas$i2a <- ajustar("I2a duas partes — A: binário de superlotação",
                      paste("sobrecarga ~", FX, "+ (1|cnes_f)"),
                      binomial(), d, log_escala = FALSE,
                      nota = "isola R8-3b: a forma nova, parte A")
linhas$i2b <- ajustar("I2b duas partes — B: contínua <= 100",
                      paste("log(ocup_int_cond) ~", FX, "+ (1|cnes_f)"),
                      gaussian(), d[!is.na(d$ocup_int_cond), ],
                      nota = "isola R8-3b: a forma nova, parte B")

tab <- do.call(rbind, linhas)
write.csv(tab, file.path(TAB, "tabE5_decomposicao_defeitos.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("\n[TAB] tabE5_decomposicao_defeitos.csv\n")

# ── deltas isolados ──────────────────────────────────────────────────
cat("\n", strrep("=", 76), "\n", sep = "")
cat("EFEITO ISOLADO DE CADA DEFEITO (em pontos de log)\n")
cat(strrep("=", 76), "\n", sep = "")
g <- function(k) tab[k, "coef_oss"]
cat(sprintf("  R8-1 limiar   (T00->T10, amostra fixa) .......... %+.5f\n",
            g("t10") - g("t00")))
cat(sprintf("  R8-1 limiar   (T01->T11, amostra fixa) .......... %+.5f\n",
            g("t11") - g("t01")))
cat(sprintf("  R8-2 amostra  (T00->T01, limiar fixo) ........... %+.5f\n",
            g("t01") - g("t00")))
cat(sprintf("  R8-2 amostra  (T10->T11, limiar fixo) ........... %+.5f\n",
            g("t11") - g("t10")))
cat(sprintf("  R8-1+R8-2 conjunto (T00->T11) ................... %+.5f\n",
            g("t11") - g("t00")))
cat(sprintf("\n  R8-3a tirar a winsorização (I0->I1) ............. %+.5f\n",
            g("i1") - g("i0")))
cat(sprintf("  R8-3b mudar a forma (I1 -> parte B) ............. %+.5f\n",
            g("i2b") - g("i1")))
cat("\n  R8-3 não se resume a delta de coeficiente: a forma em duas partes\n")
cat("  RESPONDE OUTRA PERGUNTA. Ver a parte A, que não existe no original.\n")
cat("\n[decomposição] Concluída.\n")
