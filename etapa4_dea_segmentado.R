# etapa4_dea_segmentado.R
# ETAPA 4 — DEA com FRONTEIRA SEPARADA POR ESTRATO.
#
# Por que fronteira por estrato
# -----------------------------
# O DEA compara cada unidade com a envoltória das demais. Misturar E1, E2 e E3
# numa fronteira só compara hospital sem UTI SUS com hospital de UTI de alta
# complexidade como se fossem a mesma tecnologia de produção — que é
# exatamente o que a segmentação existe para não fazer. A fronteira aqui é
# estimada por ESTRATO × ANO: por estrato para respeitar a tecnologia, por ano
# para não contaminar a comparação com mudança tecnológica (convenção já
# vigente em fase2_dea.R) e para manter o bootstrap tratável.
#
# O que este script NÃO faz
# -------------------------
# Não altera `preparo_fase2.R`, `fase2_dea.R` nem qualquer saída da Fase 2.
# O preparo é replicado aqui sobre `painel_segmentado.csv`, com as mesmas
# regras vigentes do projeto: IPCA por ano a preços de 2025, porte fixo pela
# mediana de leitos, exclusão do denominador frágil.
#
# Inputs e outputs do DEA — mesmas decisões documentadas de fase2_dea.R:
#   inputs  total_leitos e valor_real (recursos a preços de 2025)
#   outputs qtde e qtde_alta_complex
# Os leitos de UTI ficam fora do conjunto principal (subconjunto dos leitos
# totais, e zeros impedem o bootstrap).
#
# RESTRIÇÕES DE LEITURA
# ---------------------
# O escore de eficiência é RELATIVO À FRONTEIRA DO PRÓPRIO ESTRATO. Escores de
# estratos diferentes NÃO são comparáveis entre si: um TE de 0,90 em E1 e um
# TE de 0,90 em E3 dizem "próximo da fronteira do seu grupo", não "igualmente
# eficientes". Comparação válida é dentro do estrato, entre categorias.
# O Privado não é interpretado. Célula com menos de 10 CNES sai com tarja.
#
# Saída
# -----
#   analises/tabelas/tabSEG_11_dea_por_estrato.csv

.libPaths(c(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"),
            .libPaths()))
set.seed(20260706)
suppressMessages(library(Benchmarking))
suppressMessages(library(truncreg))

RAIZ <- "C:/Users/Pichau/Desktop/Projeto_Final/gestao-hospitalar-sus-sp-master"
PAINEL <- file.path(RAIZ, "analises", "painel_segmentado.csv")
TAB <- file.path(RAIZ, "analises", "tabelas")

NREP_BOOT <- 2000
B_SEGUNDA <- 1000
PISO_CNES <- 10

# ── preparo, replicando as regras vigentes ───────────────────────────
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
painel$fator_ipca <- fator[as.character(painel$ano)]
painel$valor_real <- painel$valor * painel$fator_ipca

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
painel$cplx_z <- as.numeric(scale(painel$complexidade_estrutural))
painel$ano_f <- factor(painel$ano)

d <- painel[painel$flag_fragil == 0, ]
estratos <- sort(unique(d$estrato))
anos <- sort(unique(d$ano))

# ── DEA por estrato × ano ────────────────────────────────────────────
rodar_estrato <- function(dd, rotulo) {
  linhas <- list()
  for (a in anos) {
    da <- dd[dd$ano == a, ]
    if (nrow(da) < 5) {
      cat(sprintf("  %s ano %d: n = %d < 5, fronteira não estimada\n",
                  rotulo, a, nrow(da)))
      next
    }
    X <- as.matrix(da[, c("total_leitos", "valor_real")])
    Y <- as.matrix(da[, c("qtde", "qtde_alta_complex")])
    e_vrs <- dea(X, Y, RTS = "vrs", ORIENTATION = "out")
    e_crs <- dea(X, Y, RTS = "crs", ORIENTATION = "out")
    te_vrs <- 1 / e_vrs$eff
    te_crs <- 1 / e_crs$eff
    bb <- dea.boot(X, Y, NREP = NREP_BOOT, RTS = "vrs", ORIENTATION = "out")
    lin <- data.frame(cnes = da$cnes, ano = a, estrato = rotulo,
                      categoria = as.character(da$categoria),
                      te_bcc = te_vrs, te_ccr = te_crs,
                      ef_escala = te_crs / te_vrs,
                      te_bcc_vc = 1 / bb$eff.bc)
    linhas[[as.character(a)]] <- lin
    cat(sprintf("  %s ano %d: n = %d, TE BCC mediana %.3f, corrigida %.3f\n",
                rotulo, a, nrow(da), median(te_vrs), median(lin$te_bcc_vc)))
  }
  do.call(rbind, linhas)
}

# cache dos escores: o bootstrap de Simar e Wilson é a parte cara (33
# fronteiras × 2.000 réplicas) e não muda enquanto o painel não mudar.
CACHE <- file.path(RAIZ, "analises", "dea_escores_segmentado.rds")
if (file.exists(CACHE)) {
  esc <- readRDS(CACHE)
  cat(sprintf("\n[DEA] escores lidos do cache (%s), %d linhas\n",
              basename(CACHE), nrow(esc)))
} else {
  cat(sprintf("\n[DEA] fronteira por ESTRATO × ANO, bootstrap de Simar e Wilson (%d réplicas)\n",
              NREP_BOOT))
  t0 <- Sys.time()
  esc <- do.call(rbind, lapply(estratos, function(e)
    rodar_estrato(d[d$estrato == e, ], e)))
  cat(sprintf("[DEA] concluído em %.1f min\n",
              as.numeric(difftime(Sys.time(), t0, units = "mins"))))
  saveRDS(esc, CACHE)
}

# ── medianas por estrato e categoria, com tarja ──────────────────────
agg <- aggregate(cbind(te_bcc, te_bcc_vc, te_ccr, ef_escala) ~
                   estrato + categoria, data = esc, FUN = median)
n_obs <- aggregate(cnes ~ estrato + categoria, data = esc, FUN = length)
n_cnes <- aggregate(cnes ~ estrato + categoria, data = esc,
                    FUN = function(x) length(unique(x)))
names(n_obs)[3] <- "n_obs"; names(n_cnes)[3] <- "n_cnes"
agg <- merge(merge(agg, n_obs), n_cnes)
agg$tarja <- ifelse(agg$n_cnes < PISO_CNES, "[n<10]", "")
agg <- agg[order(agg$estrato, agg$categoria), ]

cat("\n[DEA] medianas por estrato e categoria (TE corrigido de viés):\n")
print(agg[, c("estrato", "categoria", "n_obs", "n_cnes", "tarja",
              "te_bcc", "te_bcc_vc", "ef_escala")], digits = 3,
      row.names = FALSE)

# ── segunda etapa: truncada com bootstrap por hospital, DENTRO de cada estrato
# lambda = 1/TE corrigido (Farrell >= 1). Coeficiente NEGATIVO em categoria
# indica MAIS eficiente que a Direta. Nunca Tobit nem MQO.
cat("\n[DEA] segunda etapa: truncada por estrato, bootstrap por hospital\n")
seg <- merge(esc, unique(d[, c("cnes", "ano", "cplx_z", "porte_fixo",
                               "ano_f")]), by = c("cnes", "ano"))
seg$lambda_vc <- 1 / seg$te_bcc_vc
seg$categoria <- factor(seg$categoria,
                        levels = c("Direta", "OSS", "Público Municipal",
                                   "Filantrópico", "Privado"))

linhas_seg <- list()
for (e in estratos) {
  se <- droplevels(seg[seg$estrato == e, ])
  # porte e ano só entram com variação dentro do estrato
  termos <- c("categoria", "cplx_z")
  if (nlevels(se$porte_fixo) > 1) termos <- c(termos, "porte_fixo")
  if (nlevels(droplevels(se$ano_f)) > 1) termos <- c(termos, "ano_f")
  f <- as.formula(paste("lambda_vc ~", paste(termos, collapse = " + ")))
  ajustar <- function(dd) truncreg(f, data = dd, point = 1, direction = "left")
  m0 <- try(ajustar(se), silent = TRUE)
  if (inherits(m0, "try-error")) {
    cat(sprintf("  %s: truncada FALHOU — %s\n", e,
                attr(m0, "condition")$message))
    next
  }
  co <- coef(m0)
  cn <- unique(se$cnes)
  boot_cf <- matrix(NA_real_, B_SEGUNDA, length(co),
                    dimnames = list(NULL, names(co)))
  set.seed(20260706)
  for (b in seq_len(B_SEGUNDA)) {
    am <- sample(cn, length(cn), replace = TRUE)
    db <- do.call(rbind, lapply(am, function(x) se[se$cnes == x, ]))
    fit <- try(ajustar(db), silent = TRUE)
    if (inherits(fit, "try-error")) next
    # a reamostragem pode não sortear nenhum hospital de alguma categoria,
    # e aí a réplica devolve MENOS coeficientes que o modelo original.
    # Casar por NOME; o que faltar fica NA naquela réplica.
    cf <- coef(fit)
    comuns <- intersect(names(cf), colnames(boot_cf))
    boot_cf[b, comuns] <- cf[comuns]
  }
  # réplicas válidas contadas POR TERMO: um termo cuja categoria não foi
  # sorteada em parte das réplicas tem IC apoiado em menos réplicas, e isso
  # precisa aparecer na tabela em vez de ficar escondido num número só.
  validas <- colSums(!is.na(boot_cf))
  ic <- t(apply(boot_cf, 2, quantile, c(.025, .975), na.rm = TRUE))
  alvo <- grep("categoriaOSS", names(co))
  cat(sprintf("  %s: réplicas válidas (OSS) %d/%d | OSS %+.4f IC95%% [%+.4f, %+.4f]\n",
              e, validas[alvo], B_SEGUNDA, co[alvo], ic[alvo, 1], ic[alvo, 2]))
  linhas_seg[[e]] <- data.frame(
    estrato = e, termo = names(co), coef = co,
    ic95_lo = ic[, 1], ic95_hi = ic[, 2],
    replicas_validas = as.integer(validas), row.names = NULL)
}
tab_seg <- do.call(rbind, linhas_seg)

# ── tabela única de saída ────────────────────────────────────────────
bloco_esc <- data.frame(
  bloco = "escores_medianos", estrato = agg$estrato,
  categoria = as.character(agg$categoria), termo = NA_character_,
  n_obs = agg$n_obs, n_cnes = agg$n_cnes, tarja = agg$tarja,
  te_bcc = round(agg$te_bcc, 4), te_bcc_corrigido = round(agg$te_bcc_vc, 4),
  ef_escala = round(agg$ef_escala, 4),
  coef = NA_real_, ic95_lo = NA_real_, ic95_hi = NA_real_)

bloco_seg <- data.frame(
  bloco = "segunda_etapa_truncada", estrato = tab_seg$estrato,
  categoria = NA_character_, termo = tab_seg$termo,
  n_obs = NA_integer_, n_cnes = NA_integer_, tarja = NA_character_,
  te_bcc = NA_real_, te_bcc_corrigido = NA_real_, ef_escala = NA_real_,
  coef = round(tab_seg$coef, 5), ic95_lo = round(tab_seg$ic95_lo, 5),
  ic95_hi = round(tab_seg$ic95_hi, 5))

saida <- rbind(bloco_esc, bloco_seg)
write.csv(saida, file.path(TAB, "tabSEG_11_dea_por_estrato.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")
cat("\n[TAB] tabSEG_11_dea_por_estrato.csv\n")
cat("  lembrete: lambda maior = MENOS eficiente; coeficiente negativo em\n",
    "  categoria indica mais eficiência que a Direta. Escores de estratos\n",
    "  diferentes NÃO são comparáveis entre si.\n")
cat("\n[etapa4-dea] Concluída.\n")
