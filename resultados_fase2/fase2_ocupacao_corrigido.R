# fase2_ocupacao_corrigido.R
# ETAPA 5 — Reestimação dos modelos de ocupação da Fase 2, com os três
# defeitos de R8 corrigidos.
#
# Não altera `fase2_hierarquico.R`, `fase2_robustez.R` nem `preparo_fase2.R`. Os
# resultados publicados continuam reproduzíveis a partir dos arquivos que os
# produziram; este script produz os corrigidos ao lado deles, para que a
# comparação seja auditável em vez de substitutiva.
#
# ESTRUTURA
# ---------
# BLOCO A  reproduz as especificações ORIGINAIS (defeituosas) sobre o mesmo
#          painel, para verificar que este script casa com o publicado antes
#          de afirmar qualquer mudança. Se não reproduzir, o script aborta.
# BLOCO B  reestima as mesmas quantidades com [R8-1], [R8-2] e [R8-3]
#          corrigidos.
# BLOCO C  variantes de robustez (sem pandemia, sem conversores, suporte
#          comum) sobre as especificações corrigidas.
#
# OS TRÊS DEFEITOS
# ----------------
# [R8-1] winsorização da UTI no p99 do painel contaminado pelos zeros
#        estruturais (171,2) em vez do p99 da subamostra válida (180,5).
# [R8-2] amostra da UTI restrita a `ocupacao_uti > 0` — condicionamento NO
#        DESFECHO. Corrigido para `uti_sus > 0`, que é CAPACIDADE. A
#        diferença são 7 observações com UTI habilitada e zero diárias no
#        ano, excluídas do publicado justamente por terem desfecho zero.
# [R8-3] internação winsorizada no p99 (125,1), o que trata como ruído de
#        cauda o excesso acima de 100% — a assinatura da superlotação
#        (R1 v4). Corrigido para modelo em duas partes (R6), sem
#        winsorização.
#
# RESTRIÇÕES DE LEITURA
# ---------------------
# Esta é a especificação hierárquica da Fase 2, sobre o painel INTEIRO e sem
# estratificação: o coeficiente de OSS é o contraste médio da rede, com
# intercepto aleatório de hospital e termo de Mundlak. A identificação
# causal continua repousando sobre os cinco conversores, dos quais só
# Sorocaba e Pérola têm pós-tratamento longo. O Privado não é interpretado.
# Sem Rtools, o backend é glmmTMB: máxima verossimilhança com efeito
# aleatório, NÃO amostragem posterior — sem priors, sem posterior, IC de
# Wald. Mesma degradação já documentada na Fase 2.
#
# Saídas
# ------
#   resultados_fase2/tabelas/tabE5_ocupacao_antes_depois.csv
#   resultados_fase2/tabelas/tabE5_ocupacao_variantes.csv

.libPaths(c(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"),
            .libPaths()))
set.seed(20260706)
suppressMessages(library(glmmTMB))

RAIZ <- "C:/Users/Pichau/Desktop/Projeto_Final/gestao-hospitalar-sus-sp-master"
PAINEL <- file.path(RAIZ, "analises", "painel_definitivo.csv")
TAB <- file.path(RAIZ, "resultados_fase2", "tabelas")
source(file.path(RAIZ, "resultados_fase2", "preparo_fase2_corrigido.R"))

# valores publicados, de tabB_modelos_hierarquicos.csv, para a checagem de
# reprodução do BLOCO A
PUB <- list(ocupacao_internacao = 0.118016, uti_parte2 = 0.265141)
TOL <- 0.002

painel <- preparar_painel_corrigido(PAINEL)
d <- amostra_desfecho_c(painel)
conversores <- attr(painel, "conversores")

TERMO_LP <- if (var(painel$longa_perm) > 0) " + longa_perm" else ""
if (TERMO_LP == "")
  cat("[especificação] longa_perm sem variação — termo excluído\n")
FX <- paste0("categoria + cplx_z + porte_fixo", TERMO_LP,
             " + media_oss + ano_f")

extrair <- function(m) {
  if (inherits(m, "try-error")) return(NULL)
  if (!isTRUE(m$fit$convergence == 0)) return(NULL)
  s <- summary(m)$coefficients$cond
  i <- grep("categoriaOSS", rownames(s))[1]
  if (is.na(i)) return(NULL)
  if (any(is.na(sqrt(diag(vcov(m)$cond))))) return(NULL)
  c(coef = s[i, 1], ep = s[i, 2],
    lo = s[i, 1] - 1.96 * s[i, 2], hi = s[i, 1] + 1.96 * s[i, 2])
}

# Sem conversor na subamostra, `media_oss` é constante (0 ou 1 por hospital,
# sem intermediário) e a coluna fica deficiente de posto. Deixar o glmmTMB
# descartá-la sozinho produz convergência singular; removê-la da fórmula
# ANTES é a mesma decisão tomada na Etapa 4, e deixa explícito que naquela
# variante não há within a separar do between.
sem_mundlak <- function(f, dados) {
  tem_switcher <- any(dados$media_oss > 0.001 & dados$media_oss < 0.999)
  if (tem_switcher) return(f)
  cat("  [Mundlak] sem conversor na subamostra — media_oss removido ",
      "(sem identificação within)\n", sep = "")
  gsub(" \\+ media_oss", "", f)
}

ajustar <- function(rotulo, f, familia, dados, zi = ~0, log_escala = TRUE) {
  cat(sprintf("\n[modelo] %s (n = %d)\n", rotulo, nrow(dados)))
  f <- sem_mundlak(f, dados)
  m <- try(glmmTMB(as.formula(f), family = familia, ziformula = zi,
                   data = dados), silent = TRUE)
  r <- extrair(m)
  if (is.null(r)) {
    msg <- if (inherits(m, "try-error"))
      gsub("\\s+", " ", attr(m, "condition")$message)
    else "não convergiu ou matriz singular"
    cat(sprintf("  FALHOU: %s\n", substr(msg, 1, 140)))
    return(data.frame(modelo = rotulo, n = nrow(dados),
                      situacao = paste("FALHOU:", substr(msg, 1, 140)),
                      coef_oss = NA, ep = NA, ic_lo = NA, ic_hi = NA,
                      efeito_pct = NA, stringsAsFactors = FALSE))
  }
  cat(sprintf("  OSS %+.4f (EP %.4f) IC95%% [%+.4f, %+.4f]%s\n",
              r["coef"], r["ep"], r["lo"], r["hi"],
              if (log_escala) sprintf("  = %+.1f%%",
                                      100 * (exp(r["coef"]) - 1)) else ""))
  data.frame(modelo = rotulo, n = nrow(dados), situacao = "estimado",
             coef_oss = round(r["coef"], 5), ep = round(r["ep"], 5),
             ic_lo = round(r["lo"], 5), ic_hi = round(r["hi"], 5),
             efeito_pct = if (log_escala) round(100 * (exp(r["coef"]) - 1), 2)
                          else NA,
             stringsAsFactors = FALSE, row.names = NULL)
}

# ══════════════════════════════════════════════════════════════════════
# BLOCO A — reproduzir as especificações ORIGINAIS (defeituosas)
# ══════════════════════════════════════════════════════════════════════
cat("\n", strrep("=", 70), "\n", sep = "")
cat("BLOCO A — reprodução das especificações ORIGINAIS (com os defeitos)\n")
cat("Objetivo: confirmar que este script casa com o publicado ANTES de\n")
cat("afirmar que algo mudou.\n")
cat(strrep("=", 70), "\n", sep = "")

# defeito 1 e 3 tal como no original: p99 do painel completo, ambas
d$ocup_int_w_orig <- pmin(d$ocupacao_internacao,
                          quantile(d$ocupacao_internacao, .99, names = FALSE))
d$ocup_uti_w_orig <- pmin(d$ocupacao_uti,
                          quantile(painel$ocupacao_uti, .99, names = FALSE))
# defeito 2 tal como no original: condiciona no DESFECHO
pos_uti_orig <- d[d$ocupacao_uti > 0, ]

antes <- rbind(
  ajustar("ORIG ocupacao_internacao (winsor. p99 painel)",
          paste("log(ocup_int_w_orig) ~", FX, "+ (1|cnes_f)"),
          gaussian(), d),
  ajustar("ORIG uti_parte2 (winsor. contaminada, amostra por desfecho)",
          paste("ocup_uti_w_orig ~", FX, "+ (1|cnes_f)"),
          Gamma(link = "log"), pos_uti_orig))

for (k in seq_len(nrow(antes))) {
  alvo <- if (grepl("internacao", antes$modelo[k])) PUB$ocupacao_internacao
          else PUB$uti_parte2
  dif <- abs(antes$coef_oss[k] - alvo)
  cat(sprintf("  [reprodução] %s: obtido %+.5f, publicado %+.5f, |dif| %.5f %s\n",
              if (grepl("internacao", antes$modelo[k])) "ocupacao_internacao"
              else "uti_parte2",
              antes$coef_oss[k], alvo, dif,
              if (dif < TOL) "OK" else "DIVERGE"))
  if (is.na(dif) || dif >= TOL)
    stop("BLOCO A não reproduziu o publicado — parar e reportar, ",
         "não seguir para o BLOCO B sobre base que não confere.")
}
cat("\n[reprodução] as duas especificações originais conferem com o publicado.\n")

# ══════════════════════════════════════════════════════════════════════
# BLOCO B — especificações CORRIGIDAS
# ══════════════════════════════════════════════════════════════════════
cat("\n", strrep("=", 70), "\n", sep = "")
cat("BLOCO B — especificações CORRIGIDAS (R8-1, R8-2, R8-3)\n")
cat(strrep("=", 70), "\n", sep = "")

uti_cap <- amostra_uti_capacidade(d)
cat(sprintf("\n[R8-2] amostra da UTI: %d obs por CAPACIDADE (uti_sus>0)\n",
            nrow(uti_cap)))
cat(sprintf("[R8-2]   contra %d obs do original, que condiciona no desfecho\n",
            nrow(pos_uti_orig)))
cat(sprintf("[R8-2]   diferença: %d obs com UTI habilitada e ZERO diárias\n",
            nrow(uti_cap) - nrow(pos_uti_orig)))

depois <- rbind(
  # [R8-3] internação em duas partes, sem winsorização
  ajustar("CORR internacao parte A (binário de superlotação)",
          paste("sobrecarga ~", FX, "+ (1|cnes_f)"),
          binomial(), d, log_escala = FALSE),
  ajustar("CORR internacao parte B (contínua <=100, sem winsor.)",
          paste("log(ocup_int_cond) ~", FX, "+ (1|cnes_f)"),
          gaussian(), d[!is.na(d$ocup_int_cond), ]),
  # [R8-1] + [R8-2] UTI: limiar da subamostra válida, amostra por capacidade,
  # zeros preservados via Tweedie
  ajustar("CORR uti intensidade (Tweedie, zeros preservados)",
          paste("ocupacao_uti_w ~", FX, "+ (1|cnes_f)"),
          tweedie(), uti_cap),
  # parte 1 com sentido: dado que TEM UTI habilitada, opera no ano?
  ajustar("CORR uti parte 1 (opera | tem capacidade)",
          paste("I(ocupacao_uti_w > 0) ~", FX, "+ (1|cnes_f)"),
          binomial(), uti_cap, log_escala = FALSE))

comp <- rbind(cbind(bloco = "A_original_defeituoso", antes),
              cbind(bloco = "B_corrigido", depois))
write.csv(comp, file.path(TAB, "tabE5_ocupacao_antes_depois.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("\n[TAB] tabE5_ocupacao_antes_depois.csv\n")

# ══════════════════════════════════════════════════════════════════════
# BLOCO C — variantes de robustez sobre as especificações CORRIGIDAS
# ══════════════════════════════════════════════════════════════════════
cat("\n", strrep("=", 70), "\n", sep = "")
cat("BLOCO C — robustez das especificações corrigidas\n")
cat(strrep("=", 70), "\n", sep = "")

variantes <- list(
  principal     = function(x) x,
  sem_pandemia  = function(x) x[!(x$ano %in% c(2020, 2021)), ],
  sem_switchers = function(x) x[!(x$cnes %in% conversores), ],
  suporte_comum = function(x) amostra_suporte_c(x))

# As especificações ORIGINAIS entram aqui também, variante a variante: a
# afirmação publicada que mais depende de robustez é justamente a de
# `sem_switchers` ("a ocupação vai de 0,118 para 0,235, passando a excluir o
# zero"), e ela só pode ser avaliada comparando original e corrigido DENTRO
# de cada variante, não só no principal.
especs <- list(
  ORIG_ocupacao = list(f = paste("log(ocup_int_w_orig) ~", FX, "+ (1|cnes_f)"),
                       fam = gaussian(), prep = function(x) x, log = TRUE),
  ORIG_uti = list(f = paste("ocup_uti_w_orig ~", FX, "+ (1|cnes_f)"),
                  fam = Gamma(link = "log"),
                  prep = function(x) x[x$ocupacao_uti > 0, ], log = TRUE),
  int_parteA = list(f = paste("sobrecarga ~", FX, "+ (1|cnes_f)"),
                    fam = binomial(), prep = function(x) x, log = FALSE),
  int_parteB = list(f = paste("log(ocup_int_cond) ~", FX, "+ (1|cnes_f)"),
                    fam = gaussian(),
                    prep = function(x) x[!is.na(x$ocup_int_cond), ],
                    log = TRUE),
  uti_intensidade = list(f = paste("ocupacao_uti_w ~", FX, "+ (1|cnes_f)"),
                         fam = tweedie(),
                         prep = amostra_uti_capacidade, log = TRUE))

linhas <- list()
for (v in names(variantes)) {
  dv <- variantes[[v]](d)
  for (e in names(especs)) {
    sp <- especs[[e]]
    dd <- sp$prep(dv)
    r <- ajustar(sprintf("%s | %s", v, e), sp$f, sp$fam, dd,
                 log_escala = sp$log)
    linhas[[paste(v, e)]] <- cbind(
      variante = v, modelo_base = e,
      versao = if (grepl("^ORIG", e)) "original" else "corrigido", r)
  }
}
tabv <- do.call(rbind, linhas)
write.csv(tabv, file.path(TAB, "tabE5_ocupacao_variantes.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("\n[TAB] tabE5_ocupacao_variantes.csv\n")

cat("\n", strrep("=", 70), "\n", sep = "")
cat("RESUMO ANTES × DEPOIS\n")
cat(strrep("=", 70), "\n", sep = "")
print(comp[, c("bloco", "modelo", "n", "situacao", "coef_oss", "ic_lo",
               "ic_hi", "efeito_pct")], row.names = FALSE)
cat("\n[etapa5] Concluída.\n")
