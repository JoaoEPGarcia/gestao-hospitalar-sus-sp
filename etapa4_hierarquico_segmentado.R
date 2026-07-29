# etapa4_hierarquico_segmentado.R
# ETAPA 4 — MODELO HIERÁRQUICO POR MÁXIMA VEROSSIMILHANÇA, por estrato
# (intercepto aleatório de hospital, Mundlak, dummies de ano), cinco
# indicadores.
#
# O NOME DESTE ARQUIVO FOI CORRIGIDO EM 29/07/2026
# ------------------------------------------------
# Chamava-se `etapa4_bayes_segmentado.R` e produzia
# `tabSEG_12_bayes_por_estrato.csv`. Nada aqui é bayesiano, e o cabeçalho
# abaixo sempre disse isso — mas o NOME dizia o contrário, e é o nome que
# sobrevive em citação, em índice de pasta e em conversa. Rótulo que
# contradiz o próprio conteúdo é erro que um parecerista de estatística
# encontra na primeira leitura.
#
# HONESTIDADE SOBRE O BACKEND — este NÃO é um modelo bayesiano
# ------------------------------------------------------------
# A escada prevista no protocolo é brms com cmdstanr; senão rstan; senão
# glmmTMB. Este ambiente NÃO tem toolchain de compilação (Rtools), condição
# verificada e impressa abaixo. O que roda aqui é glmmTMB: máxima
# verossimilhança com efeito aleatório, NÃO amostragem posterior. Não há
# priors, não há posterior, não há diagnóstico de cadeia. Os intervalos são
# de Wald, não críveis. A degradação é a mesma já documentada na Fase 2 e é
# repetida aqui em vez de silenciada.
#
# CUIDADO AO COMPARAR COM A FASE 2: a Frente 1 da Fase 2 desceu a MESMA
# escada, pelo mesmo motivo, e também roda em glmmTMB por máxima
# verossimilhança (ver `resultados_fase2/RELATORIO_EXECUCAO.md`, seção 3).
# Os dois são o mesmo estimador. A proximidade entre eles NÃO é convergência
# entre paradigmas inferenciais, porque não há dois paradigmas envolvidos.
# O rótulo "Bayesiana hierárquica" que a Fase 2 ainda carrega em título e
# README tem o mesmo defeito que este arquivo tinha, e a decisão sobre
# renomeá-lo está pendente — ver PENDENCIAS.md.
#
# CONDICIONAL POR DESENHO: o prompt da Etapa 4 põe esta família como
# condicional — entra só onde convergir. Falha de convergência é REPORTADA na
# tabela, com a mensagem do otimizador, nunca omitida nem substituída por um
# modelo mais simples sem aviso.
#
# CORREÇÕES FRENTE AOS MODELOS DA FASE 2 (R8)
# -------------------------------------------
# Defeito 2 de R8 — `fase2_hierarquico.R` restringe a UTI a `ocupacao_uti > 0`, o
# que condiciona NO DESFECHO. Aqui a amostra de UTI é definida pela
# CAPACIDADE (`uti_sus > 0`, isto é `ocupacao_uti_valida` não faltante) e os
# zeros PERMANECEM, acomodados por família Tweedie (contínua não-negativa com
# massa em zero). Nenhuma observação é descartada por causa do seu desfecho.
#
# Defeito 1 de R8 — a winsorização usa o p99 da SUBAMOSTRA VÁLIDA, limiar
# único (180,5), e não o p99 do painel contaminado pelos zeros estruturais
# (171,2) de `preparo_fase2.R`.
#
# Defeito 3 de R8 — a ocupação de internação NÃO é winsorizada: entra em duas
# partes (R6), binário de superlotação e contínua condicional a <= 100.
#
# Este script não altera `preparo_fase2.R`, `fase2_hierarquico.R` nem qualquer saída
# da Fase 2. O preparo é replicado sobre `painel_segmentado.csv`.
#
# RESTRIÇÕES DE LEITURA
# ---------------------
# Fora de E3 não há identificação within e o coeficiente de OSS é comparação
# entre grupos. O Privado não é interpretado. Célula com menos de 10 CNES OSS
# sai com tarja. Em E1 o modelo de UTI é NÃO-APLICÁVEL.
# `complexidade_pond_mort` jamais entra como regressor.
#
# Saída
# -----
#   analises/tabelas/tabSEG_12_hierarquico_por_estrato.csv

.libPaths(c(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"),
            .libPaths()))
set.seed(20260706)

RAIZ <- "C:/Users/Pichau/Desktop/Projeto_Final/gestao-hospitalar-sus-sp-master"
PAINEL <- file.path(RAIZ, "analises", "painel_segmentado.csv")
TAB <- file.path(RAIZ, "analises", "tabelas")
PISO_CNES <- 10

tem_cmdstan <- requireNamespace("cmdstanr", quietly = TRUE)
tem_rstan   <- requireNamespace("rstan", quietly = TRUE)
tem_rtools  <- dir.exists("C:/rtools46") || dir.exists("C:/rtools45")
cat(sprintf("[escada] cmdstanr=%s rstan=%s rtools=%s\n",
            tem_cmdstan, tem_rstan, tem_rtools))
if (!tem_rtools) {
  cat("[escada] Sem toolchain de compilação: descendo para glmmTMB.\n")
  cat("[escada] ATENÇÃO: máxima verossimilhança com efeito aleatório, NÃO\n")
  cat("[escada] amostragem posterior. Sem priors, sem posterior, IC de Wald.\n")
}
suppressMessages(library(glmmTMB))

# ── preparo ──────────────────────────────────────────────────────────
painel <- read.csv(PAINEL, fileEncoding = "UTF-8", check.names = FALSE,
                   stringsAsFactors = FALSE)
stopifnot(length(unique(painel$cnes)) == 289, nrow(painel) == 3179,
          all(table(painel$cnes) == 11))
cat("[preparo] painel verificado: 289 CNES, 3.179 observações\n")

ipca <- c("2015" = 10.67, "2016" = 6.29, "2017" = 2.95, "2018" = 3.75,
          "2019" = 4.31, "2020" = 4.52, "2021" = 10.06, "2022" = 5.79,
          "2023" = 4.62, "2024" = 4.83, "2025" = 4.26)
indice <- cumprod(1 + ipca / 100)
fator <- indice[length(indice)] / indice
painel$custo_real <- painel$custo_saida * fator[as.character(painel$ano)]

med_leitos <- tapply(painel$total_leitos, painel$cnes, median)
porte_de <- function(x) {
  if (x <= 50) "HPP" else if (x <= 150) "Médio Porte"
  else if (x <= 500) "Grande Porte" else "Especial"
}
painel$porte_fixo <- factor(
  vapply(med_leitos, porte_de, character(1))[as.character(painel$cnes)],
  levels = c("HPP", "Médio Porte", "Grande Porte", "Especial"))

painel$flag_fragil <- as.integer(painel$cnes == 2097613 &
                                   painel$ano %in% c(2020, 2021))
painel$categoria <- factor(painel$modelo_gestao_proxy,
                           levels = c("Direta", "OSS", "Público Municipal",
                                      "Filantrópico", "Privado"))
painel$d_oss <- as.integer(painel$categoria == "OSS")
painel$media_oss <- ave(painel$d_oss, painel$cnes, FUN = mean)
painel$cplx_z <- as.numeric(scale(painel$complexidade_estrutural))
painel$ano_f <- factor(painel$ano)
painel$cnes_f <- factor(painel$cnes)

# duas partes da ocupação de internação (R6) — sem winsorização
painel$sobrecarga <- as.integer(painel$ocupacao_internacao > 100)
painel$ocup_int_cond <- ifelse(painel$ocupacao_internacao <= 100,
                               painel$ocupacao_internacao, NA)

# winsorização da UTI: p99 da SUBAMOSTRA VÁLIDA, limiar único (R8 defeito 1)
valida <- painel$ocupacao_uti_valida[!is.na(painel$ocupacao_uti_valida)]
P99 <- as.numeric(quantile(valida, 0.99, names = FALSE))
painel$ocup_uti_w <- pmin(painel$ocupacao_uti_valida, P99)
cat(sprintf("[preparo] winsorização UTI: limiar único %.1f (p99 da subamostra válida, n=%d)\n",
            P99, length(valida)))
cat(sprintf("[preparo] zeros preservados na UTI: %d obs (R8 defeito 2)\n",
            sum(valida == 0)))

d <- painel[painel$flag_fragil == 0, ]
estratos <- c("E1", "E2", "E3")

# ── especificação ────────────────────────────────────────────────────
# O termo de Mundlak só entra se houver conversor na subamostra: sem
# switcher, media_oss é colinear com a própria dummy de categoria.
montar_fx <- function(dd, com_ano = TRUE) {
  termos <- c("categoria", "cplx_z")
  if (nlevels(droplevels(dd$porte_fixo)) > 1) termos <- c(termos, "porte_fixo")
  if (any(dd$media_oss > 0.001 & dd$media_oss < 0.999))
    termos <- c(termos, "media_oss")
  if (com_ano && nlevels(droplevels(dd$ano_f)) > 1) termos <- c(termos, "ano_f")
  paste(termos, collapse = " + ")
}

resultados <- list()

ajustar <- function(rotulo, estrato, y, dd, familia, zi = ~0,
                    escala_log = FALSE) {
  dd <- dd[!is.na(dd[[y]]), ]
  dd$cnes_f <- droplevels(dd$cnes_f)
  n_oss <- length(unique(dd$cnes[dd$categoria == "OSS"]))
  base <- data.frame(
    indicador = rotulo, estrato = estrato, n_obs = nrow(dd),
    n_cnes = length(unique(dd$cnes)), n_cnes_oss = n_oss,
    tarja = if (n_oss < PISO_CNES) "[n<10]" else "",
    identificacao = if (estrato == "E3") "within (4 conversores)"
                    else if (any(dd$media_oss > 0.001 & dd$media_oss < 0.999))
                      "within FRACA — NÃO CAUSAL"
                    else "ENTRE GRUPOS — NÃO É EFEITO CAUSAL",
    stringsAsFactors = FALSE)

  f <- as.formula(paste(y, "~", montar_fx(dd), "+ (1 | cnes_f)"))
  cat(sprintf("\n[modelo] %s | %s (n = %d)\n", rotulo, estrato, nrow(dd)))
  t0 <- Sys.time()
  m <- try(glmmTMB(f, family = familia, ziformula = zi, data = dd),
           silent = TRUE)
  if (inherits(m, "try-error")) {
    msg <- gsub("\\s+", " ", attr(m, "condition")$message)
    cat(sprintf("  FALHOU: %s\n", msg))
    return(cbind(base, situacao = paste("FALHOU:", substr(msg, 1, 160)),
                 coef_oss = NA, ep = NA, ic95_lo = NA, ic95_hi = NA,
                 efeito_pct = NA))
  }
  conv <- isTRUE(m$fit$convergence == 0)
  sing <- any(is.na(sqrt(diag(vcov(m)$cond))))
  cat(sprintf("  convergiu: %s | tempo %.1fs\n", conv,
              as.numeric(difftime(Sys.time(), t0, units = "secs"))))
  if (!conv || sing) {
    cat("  NÃO CONVERGIU ou matriz singular — coeficiente NÃO reportado\n")
    return(cbind(base, situacao = "NÃO CONVERGIU — não reportado",
                 coef_oss = NA, ep = NA, ic95_lo = NA, ic95_hi = NA,
                 efeito_pct = NA))
  }
  s <- summary(m)$coefficients$cond
  linha <- grep("categoriaOSS", rownames(s), value = TRUE)[1]
  if (is.na(linha)) {
    return(cbind(base, situacao = "dummy OSS ausente do desenho",
                 coef_oss = NA, ep = NA, ic95_lo = NA, ic95_hi = NA,
                 efeito_pct = NA))
  }
  co <- s[linha, 1]; ep <- s[linha, 2]
  # a escala é declarada na chamada: gaussian sobre y JÁ logado tem link
  # identidade, então inferi-la do link da família daria identidade e
  # perderia o efeito percentual. Tweedie usa link log direto.
  log_escala <- escala_log || identical(familia()$link, "log")
  cat(sprintf("  OSS: %+.4f (EP %.4f) IC95%% [%+.4f, %+.4f]\n",
              co, ep, co - 1.96 * ep, co + 1.96 * ep))
  cbind(base, situacao = "estimado", coef_oss = round(co, 5),
        ep = round(ep, 5), ic95_lo = round(co - 1.96 * ep, 5),
        ic95_hi = round(co + 1.96 * ep, 5),
        efeito_pct = if (log_escala) round(100 * (exp(co) - 1), 2) else NA)
}

for (e in estratos) {
  de <- d[d$estrato == e, ]
  cat(sprintf("\n%s\n%s — %s: %d obs, %d CNES\n%s\n", strrep("=", 68), e,
              de$estrato_rotulo[1], nrow(de), length(unique(de$cnes)),
              strrep("=", 68)))

  # 1. mortalidade: Beta; inflação em zero só onde há zeros
  tem_zero <- any(de$mort_all == 0)
  resultados[[length(resultados) + 1]] <- ajustar(
    "Mortalidade geral", e, "mort_all", de, beta_family,
    zi = if (tem_zero) ~ cplx_z else ~0)

  # 2. TMP: lognormal
  de$log_tmp <- ifelse(de$tmp > 0, log(de$tmp), NA)
  resultados[[length(resultados) + 1]] <- ajustar(
    "TMP (log)", e, "log_tmp", de, gaussian, escala_log = TRUE)

  # 3. faturamento real: lognormal
  de$log_custo <- log(de$custo_real)
  resultados[[length(resultados) + 1]] <- ajustar(
    "Faturamento real (log)", e, "log_custo", de, gaussian, escala_log = TRUE)

  # 4. ocupação de UTI: Tweedie, zeros PRESERVADOS (R8 defeito 2)
  if (e == "E1") {
    cat("\n[modelo] Ocupação UTI | E1: NÃO-APLICÁVEL\n")
    cat("  E1 é 'sem UTI SUS' pela mediana; as observações com UTI ativa\n")
    cat("  são piscar cadastral (R7). Não se estima sobre o artefato.\n")
    resultados[[length(resultados) + 1]] <- data.frame(
      indicador = "Ocupação UTI (winsor.)", estrato = e, n_obs = NA,
      n_cnes = NA, n_cnes_oss = NA, tarja = "", identificacao = NA,
      situacao = "NÃO-APLICÁVEL (E1 sem UTI SUS)", coef_oss = NA, ep = NA,
      ic95_lo = NA, ic95_hi = NA, efeito_pct = NA, stringsAsFactors = FALSE)
  } else {
    resultados[[length(resultados) + 1]] <- ajustar(
      "Ocupação UTI (winsor.)", e, "ocup_uti_w", de, tweedie)
  }

  # 5a. superlotação: binário (R6 parte A)
  resultados[[length(resultados) + 1]] <- ajustar(
    "Superlot. internação (A)", e, "sobrecarga", de, binomial)

  # 5b. ocupação condicional a <= 100 (R6 parte B), sem winsorização
  de$log_ocup_cond <- log(de$ocup_int_cond)
  resultados[[length(resultados) + 1]] <- ajustar(
    "Ocupação intern. <=100 (B)", e, "log_ocup_cond", de, gaussian, escala_log = TRUE)
}

tab <- do.call(rbind, resultados)
tab$backend <- if (tem_rtools) "stan" else "glmmTMB (ML, NÃO posterior)"
write.csv(tab, file.path(TAB, "tabSEG_12_hierarquico_por_estrato.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat(sprintf("\n[TAB] tabSEG_12_hierarquico_por_estrato.csv (%d linhas)\n", nrow(tab)))
cat(sprintf("  estimados: %d | falhas/não convergiu: %d | não-aplicável: %d\n",
            sum(tab$situacao == "estimado"),
            sum(grepl("FALHOU|NÃO CONVERGIU", tab$situacao)),
            sum(grepl("NÃO-APLICÁVEL", tab$situacao))))
print(tab[, c("indicador", "estrato", "n_obs", "tarja", "situacao",
              "coef_oss", "efeito_pct")], row.names = FALSE)
cat("\n[etapa4-hierarquico] Concluída.\n")
