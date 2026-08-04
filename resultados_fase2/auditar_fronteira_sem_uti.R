# auditar_fronteira_sem_uti.R
#
# O teste que decide a alegacao de invalidade da SFA, aberto em 30/07/2026.
#
# A sec15 declara que "a fronteira inteira esta desqualificada como medida" e
# que a violacao de monotonicidade em 94,9% "diz que a Translog nao descreve
# bem o modo como estes hospitais transformam insumo em produto".
#
# Essa e uma afirmacao TESTAVEL, e o teste nunca foi rodado. O proprio
# fase2_sfa.R ja estima a fronteira sem o insumo de UTI (linha 159,
# m_semuti), mas:
#   - nao a salva (saveRDS cobre so cobbdouglas, translog e mundlak);
#   - nunca calcula a monotonicidade dela;
#   - so extrai dela o coeficiente das OSS (pega_oss).
#
# Este script fecha a lacuna. Reestima com a formula IDENTICA a f_sem_uti do
# original e acrescenta a variante so-leitos, que e o paralelo exato da
# checagem que a sec15 ja faz para o DEA ("DEA reestimado so com leitos como
# insumo") e que nunca foi feita para a SFA.
#
# Tres perguntas, nesta ordem:
#   A. retirado o insumo aninhado, a fronteira volta a ser monotona?
#   B. a degeneracao das OSS sobrevive ao reparo?
#   C. os ordenamentos mudam?
#
# NAO altera nenhum artefato do projeto: nao ha saveRDS nem write.csv.
# Resolve a raiz a partir da propria localizacao, como
# auditar_monotonicidade_frente2.R.
#
# Regra 7 do projeto: nenhum numero entra em relatorio sem ser reproduzido.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
set.seed(20260706)
suppressMessages(library(frontier))

args <- commandArgs(trailingOnly = FALSE)
arq <- sub("^--file=", "", args[grep("^--file=", args)])
RAIZ <- normalizePath(file.path(dirname(arq), ".."))
cat("raiz:", RAIZ, "\n")

# ---- painel, replicando preparo_fase2.R no que a SFA usa ----------------
painel <- read.csv(file.path(RAIZ, "analises", "painel_definitivo.csv"),
                   fileEncoding = "UTF-8-BOM", check.names = FALSE,
                   stringsAsFactors = FALSE)
stopifnot(length(unique(painel$cnes)) == 289, nrow(painel) == 3179)

ipca <- c("2015" = 10.67, "2016" = 6.29, "2017" = 2.95, "2018" = 3.75,
          "2019" = 4.31, "2020" = 4.52, "2021" = 10.06, "2022" = 5.79,
          "2023" = 4.62, "2024" = 4.83, "2025" = 4.26)
indice <- cumprod(1 + ipca / 100)
fator <- indice[length(indice)] / indice
painel$valor_real <- painel$valor * fator[as.character(painel$ano)]

painel$flag_fragil <- as.integer(painel$cnes == 2097613 &
                                   painel$ano %in% c(2020, 2021))
painel$categoria <- factor(painel$modelo_gestao_proxy,
                           levels = c("Direta", "OSS", "Público Municipal",
                                      "Filantrópico", "Privado"))
med <- tapply(painel$total_leitos, painel$cnes, median)
pf <- vapply(med, function(x) if (x <= 150) "Médio Porte" else
  if (x <= 500) "Grande Porte" else "Especial", character(1))
painel$porte_fixo <- pf[as.character(painel$cnes)]
painel$d_oss <- as.integer(painel$categoria == "OSS")
painel$ano_f <- factor(painel$ano)
painel$tendencia <- painel$ano - 2015
painel$cplx_z <- as.numeric(scale(painel$complexidade_estrutural))

d <- painel[painel$flag_fragil == 0, ]
cat("amostra de desfecho:", nrow(d), "observacoes\n")

d$y  <- log(d$qtde)
d$lc <- log(d$total_leitos) - mean(log(d$total_leitos))
d$uc <- log1p(d$uti_total)  - mean(log1p(d$uti_total))
d$vc <- log(d$valor_real)   - mean(log(d$valor_real))
d$lc2 <- .5 * d$lc^2; d$uc2 <- .5 * d$uc^2; d$vc2 <- .5 * d$vc^2
d$lu <- d$lc * d$uc; d$lv <- d$lc * d$vc; d$uv <- d$uc * d$vc
d$d_municipal <- as.integer(d$categoria == "Público Municipal")
d$d_filantropico <- as.integer(d$categoria == "Filantrópico")
d$d_privado <- as.integer(d$categoria == "Privado")
d$d_grande <- as.integer(d$porte_fixo == "Grande Porte")
d$d_especial <- as.integer(d$porte_fixo == "Especial")

Z <- paste("d_oss + d_municipal + d_filantropico + d_privado + cplx_z +",
           "d_grande + d_especial + tendencia")

TERMOS_Z <- c("Z_d_oss", "Z_d_municipal", "Z_d_filantropico", "Z_d_privado")

relatar <- function(mm, rot, elast) {
  cc <- summary(mm)$mleParam
  b <- cc[, 1]
  cat("\n", strrep("-", 70), "\n", rot, "\n", strrep("-", 70), "\n", sep = "")

  cat("A. monotonicidade\n")
  for (nm in names(elast)) {
    e <- elast[[nm]](b)
    cat(sprintf("   %-12s monotonas %6.2f%%  violadas %5.2f%%  "
                , nm, 100 * mean(e > 0), 100 * mean(e <= 0)))
    cat(sprintf("(elast. na media %+.4f)\n", b[nm]))
  }
  cat(sprintf("   gamma = %.4f\n", b["gamma"]))

  cat("B. equacao de ineficiencia (negativo = MENOS ineficiente)\n")
  for (nm in TERMOS_Z) {
    if (!nm %in% rownames(cc)) next
    cat(sprintf("   %-18s coef %12.4f  EP %10.4f  p %.3g\n",
                nm, cc[nm, 1], cc[nm, 2], cc[nm, 4]))
  }

  te <- as.numeric(efficiencies(mm))
  cat("C. eficiencia tecnica por categoria\n")
  for (k in levels(d$categoria)) {
    v <- te[d$categoria == k]
    if (!length(v)) next
    cat(sprintf("   %-20s n=%4d  media %.4f  mediana %.4f  DP %.6f  "
                , k, length(v), mean(v), median(v), sd(v)))
    cat(sprintf("amplitude %.2e\n", max(v) - min(v)))
  }
  invisible(te)
}

# ── 0. Principal, para servir de referencia na mesma execucao ────────────
cat("\n[SFA] reestimando a especificacao PRINCIPAL (3 insumos)...\n")
f_prin <- as.formula(paste(
  "y ~ lc + uc + vc + lc2 + uc2 + vc2 + lu + lv + uv + ano_f |", Z))
m1 <- sfa(f_prin, data = d)
te1 <- relatar(m1, "PRINCIPAL: leitos + UTI + valor (o que a sec15 julga)",
  list(lc = function(b) b["lc"] + b["lc2"]*d$lc + b["lu"]*d$uc + b["lv"]*d$vc,
       uc = function(b) b["uc"] + b["uc2"]*d$uc + b["lu"]*d$lc + b["uv"]*d$vc,
       vc = function(b) b["vc"] + b["vc2"]*d$vc + b["lv"]*d$lc + b["uv"]*d$uc))

# ── 1. Sem o insumo de UTI (formula identica a fase2_sfa.R linha 157) ────
cat("\n[SFA] reestimando SEM o insumo de UTI...\n")
m2 <- sfa(as.formula(paste("y ~ lc + vc + lc2 + vc2 + lv + ano_f |", Z)),
          data = d)
te2 <- relatar(m2, "SEM UTI: retirado o insumo aninhado",
  list(lc = function(b) b["lc"] + b["lc2"] * d$lc + b["lv"] * d$vc,
       vc = function(b) b["vc"] + b["vc2"] * d$vc + b["lv"] * d$lc))

# ── 2. So leitos: o paralelo do "DEA so com leitos" da sec15 ─────────────
cat("\n[SFA] reestimando SO COM LEITOS (sem o insumo financeiro)...\n")
m3 <- sfa(as.formula(paste("y ~ lc + lc2 + ano_f |", Z)), data = d)
te3 <- relatar(m3, "SO LEITOS: sem dinheiro nenhum, como o DEA so-leitos",
  list(lc = function(b) b["lc"] + b["lc2"] * d$lc))

# ── 3. Os ordenamentos mudam? ────────────────────────────────────────────
cat("\n", strrep("=", 70), "\n", sep = "")
cat("D. ESTABILIDADE DOS ORDENAMENTOS\n")
cat(strrep("=", 70), "\n")
cat(sprintf("   Spearman principal x sem UTI    = %.4f\n",
            cor(te1, te2, method = "spearman")))
cat(sprintf("   Spearman principal x so leitos  = %.4f\n",
            cor(te1, te3, method = "spearman")))

dea <- read.csv(file.path(RAIZ, "resultados_fase2", "dea",
                          "dea_escores_principal.csv"), fileEncoding = "UTF-8")
for (nm in c("principal", "sem UTI", "so leitos")) {
  tt <- switch(nm, "principal" = te1, "sem UTI" = te2, "so leitos" = te3)
  cr <- merge(data.frame(cnes = d$cnes, ano = d$ano, te = tt),
              dea[, c("cnes", "ano", "te_bcc_vc")], by = c("cnes", "ano"))
  cat(sprintf("   Spearman %-10s x DEA corrigido = %.4f\n",
              nm, cor(cr$te, cr$te_bcc_vc, method = "spearman")))
}

cat("\n", strrep("=", 70), "\n", sep = "")
cat("LEITURA\n")
cat(strrep("=", 70), "\n")
cat("Se a monotonicidade volta ao normal ao retirar o insumo de UTI e os\n")
cat("ordenamentos nao se movem, entao os 94,9% sao propriedade do INSUMO\n")
cat("ANINHADO, nao da forma Translog nem da tecnologia hospitalar --- e a\n")
cat("frase da sec15 que atribui a violacao a Translog nao se sustenta.\n\n")
cat("Se a degeneracao das OSS sobrevive aos dois reparos, entao ELA e o\n")
cat("defeito real da frente, e o veredito de nao-citabilidade precisa ser\n")
cat("fundado nela --- que alcanca as OSS com folga, mas cuja extensao as\n")
cat("outras quatro categorias e uma decisao a ser argumentada, nao herdada\n")
cat("da monotonicidade.\n")
