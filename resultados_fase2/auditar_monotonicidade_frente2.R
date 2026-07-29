# auditar_monotonicidade_frente2.R
#
# Frente 2 da auditoria editorial: a violacao de monotonicidade da Translog
# e uniforme entre categorias ou se concentra em alguma?
#
# Reproduz o calculo de fase2_sfa.R (linhas 93-112) observacao a observacao e
# quebra o resultado por categoria de gestao, por estrato e por ter ou nao UTI
# ativa. Nao reestima nada: le modS_translog.rds e recalcula as elasticidades.
#
# Regra 7 do projeto: nenhum numero entra em relatorio sem ser reproduzido.
#
# Este script NAO usa os caminhos C:/ProjetoPosDoc dos scripts originais:
# resolve a raiz a partir da propria localizacao, para rodar no repositorio
# onde ele estiver.

.libPaths(file.path(Sys.getenv("LOCALAPPDATA"), "R", "win-library", "4.6"))
suppressMessages(library(frontier))

args <- commandArgs(trailingOnly = FALSE)
arq <- sub("^--file=", "", args[grep("^--file=", args)])
RAIZ <- normalizePath(file.path(dirname(arq), ".."))
cat("raiz:", RAIZ, "\n")

SFA <- file.path(RAIZ, "resultados_fase2", "sfa")

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
d <- painel[painel$flag_fragil == 0, ]
cat("amostra de desfecho:", nrow(d), "observacoes\n")

# ---- as mesmas transformacoes da fronteira -----------------------------
d$lc <- log(d$total_leitos) - mean(log(d$total_leitos))
d$uc <- log1p(d$uti_total)  - mean(log1p(d$uti_total))
d$vc <- log(d$valor_real)   - mean(log(d$valor_real))

m <- readRDS(file.path(SFA, "modS_translog.rds"))
b <- summary(m)$mleParam[, 1]

e_l <- b["lc"] + b["lc2"] * d$lc + b["lu"] * d$uc + b["lv"] * d$vc
e_u <- b["uc"] + b["uc2"] * d$uc + b["lu"] * d$lc + b["uv"] * d$vc
e_v <- b["vc"] + b["vc2"] * d$vc + b["lv"] * d$lc + b["uv"] * d$uc

cat("\n=== reproducao do numero publicado ===\n")
cat(sprintf("  monotonas em leitos      : %.1f%%  (documento: 99,7%%)\n",
            100 * mean(e_l > 0)))
cat(sprintf("  monotonas em UTI         : %.1f%%\n", 100 * mean(e_u > 0)))
cat(sprintf("  VIOLADAS em UTI          : %.1f%%  (documento: 94,9%%)\n",
            100 * mean(e_u <= 0)))
cat(sprintf("  monotonas em valor       : %.1f%%  (documento: 99,6%%)\n",
            100 * mean(e_v > 0)))

uti_ativa <- d$diarias_uti > 0
cat(sprintf("  VIOLADAS em UTI, so entre as de UTI ativa: %.1f%%",
            100 * mean(e_u[uti_ativa] <= 0)))
cat("  (documento: 97,8%)\n")

# O documento diz 97,8% "entre as que tem UTI ativa" e nao define o termo.
# Tres definicoes candidatas, para saber se 97,8% corresponde a alguma:
cat("\n  qual definicao de 'UTI ativa' produz o 97,8% do documento?\n")
for (nm in c("diarias_uti", "uti_total", "uti_sus")) {
  if (!nm %in% names(d)) next
  sel <- d[[nm]] > 0
  cat(sprintf("    %-12s > 0 : n = %4d | violadas = %5.1f%%\n",
              nm, sum(sel), 100 * mean(e_u[sel] <= 0)))
}

# ---- a pergunta da frente: uniforme ou concentrada? --------------------
viol <- e_u <= 0

quebra <- function(por, rot) {
  cat("\n=== violacao de monotonicidade em UTI, por", rot, "===\n")
  tb <- tapply(viol, por, function(x) c(n = length(x),
                                        violadas = sum(x),
                                        pct = 100 * mean(x)))
  for (k in names(tb)) {
    v <- tb[[k]]
    cat(sprintf("  %-20s n = %4d | violadas = %4d | %5.1f%%\n",
                k, v["n"], v["violadas"], v["pct"]))
  }
}

quebra(d$categoria, "categoria de gestao")
quebra(ifelse(uti_ativa, "com UTI ativa", "sem UTI ativa"), "UTI ativa")

seg <- read.csv(file.path(RAIZ, "analises", "painel_segmentado.csv"),
                fileEncoding = "UTF-8-BOM", stringsAsFactors = FALSE)
if ("estrato" %in% names(seg)) {
  mapa <- tapply(seg$estrato, seg$cnes, function(x) x[1])
  d$estrato <- mapa[as.character(d$cnes)]
  quebra(d$estrato, "estrato estrutural")
}

# porte, que e a outra dimensao que a equacao de ineficiencia usa
med_leitos <- tapply(painel$total_leitos, painel$cnes, median)
porte_de <- function(x) if (x <= 150) "Médio Porte" else
  if (x <= 500) "Grande Porte" else "Especial"
porte_cnes <- vapply(med_leitos, porte_de, character(1))
d$porte_fixo <- porte_cnes[as.character(d$cnes)]
quebra(d$porte_fixo, "porte fixo")

cat("\n=== leitura ===\n")
cat("Se os percentuais por categoria ficam todos proximos do agregado, a\n")
cat("violacao e defeito geral da forma Translog. Se se concentram, a tarja\n")
cat("precisa dizer onde.\n")
