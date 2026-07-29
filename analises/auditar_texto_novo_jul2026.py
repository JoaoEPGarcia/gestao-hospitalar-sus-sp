# auditar_texto_novo_jul2026.py
# BLOCO 5 — varredura de consistência numérica do texto escrito em 29/07/2026.
#
# Confere cada número afirmado nas seções novas ou alteradas contra a saída
# que o produz. Não corrige nada: reporta.
#
# Seções cobertas: sec02 (linha de UTI), sec04 (coluna e prosa da inversão),
# sec08 (correlação e variância), sec13b (segmentação, nova), sec15
# (subseção da Etapa 5, nova), apendiceA (notas de reestimação), sec17.

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
TAB = RAIZ / "tabelas"
F2 = RAIZ.parent / "resultados_fase2" / "tabelas"

falhas, ok = [], 0


def conf(rotulo, afirmado, fonte, tol=0.051):
    """Compara valor afirmado no texto com o valor da fonte."""
    global ok
    if fonte is None:
        falhas.append(f"{rotulo}: FONTE AUSENTE (texto afirma {afirmado})")
        return
    if abs(float(afirmado) - float(fonte)) <= tol:
        ok += 1
    else:
        falhas.append(f"{rotulo}: texto {afirmado} x fonte {fonte:.5f}")


# ── fontes ───────────────────────────────────────────────────────────
seg01 = pd.read_csv(TAB / "tabSEG_01_funil_estratos.csv")
seg01.columns = [c.lstrip("﻿") for c in seg01.columns]
seg05 = pd.read_csv(TAB / "tabSEG_05_antes_depois_segmentacao.csv")
seg05.columns = [c.lstrip("﻿") for c in seg05.columns]
seg10 = pd.read_csv(TAB / "tabSEG_10_cre_mundlak_por_estrato.csv")
seg10.columns = [c.lstrip("﻿") for c in seg10.columns]
seg11 = pd.read_csv(TAB / "tabSEG_11_dea_por_estrato.csv")
seg14 = pd.read_csv(TAB / "tabSEG_14_sobrecarga_binario.csv")
seg15 = pd.read_csv(TAB / "tabSEG_15_ocupacao_condicional.csv")
seg00 = pd.read_csv(TAB / "tabSEG_00_impacto_correcao_uti.csv")
seg00.columns = [c.lstrip("﻿") for c in seg00.columns]
uni = pd.read_csv(TAB / "tab_ae_univariada.csv")
cat = pd.read_csv(TAB / "tab_ae_por_categoria.csv")
var = pd.read_csv(TAB / "tab_ae_variancia_within_between.csv")
cor = pd.read_csv(TAB / "tab_ae_correlacao_spearman.csv", index_col=0)
fam = pd.read_csv(F2 / "tabE5_sensibilidade_familias.csv")
dec = pd.read_csv(F2 / "tabE5_decomposicao_defeitos.csv")
ant = pd.read_csv(F2 / "tabE5_ocupacao_antes_depois.csv")
varr = pd.read_csv(F2 / "tabE5_ocupacao_variantes.csv")

print("=" * 78)
print("SEÇÃO 2 — linha da ocupação de UTI")
print("=" * 78)
u = uni[uni["indicador"] == "ocupacao_uti"].iloc[0]
for rot, af, col in [("média", 76.36, "media"), ("DP", 36.18, "dp"),
                     ("mediana", 76.50, "p50"), ("p90", 98.68, "p90"),
                     ("máximo", 875.21, "max"),
                     ("assimetria", 6.98, "assimetria")]:
    conf(f"sec02 {rot}", af, u[col])
conf("sec02 zeros %", 0.3, u["frac_zero"] * 100, tol=0.05)
conf("sec02 n válido", 2491, u["n"], tol=0.5)

print("=" * 78)
print("SEÇÃO 4 — coluna de UTI e a prosa da inversão")
print("=" * 78)
for c, af in [("Direta", 61.3), ("OSS", 76.1), ("Público Municipal", 73.9),
              ("Filantrópico", 80.2), ("Privado", 4.8)]:
    v = cat[cat["modelo_gestao_proxy"] == c]["ocupacao_uti_mediana"].iloc[0]
    conf(f"sec04 mediana {c}", af, v)
g = seg00.set_index("modelo_gestao_proxy")
conf("sec04 média Filantrópico antes", 57.1, g.loc["Filantrópico", "ocup_media_todos"])
conf("sec04 média Filantrópico depois", 80.9, g.loc["Filantrópico", "ocup_media_valida"])
conf("sec04 média Direta antes", 58.8, g.loc["Direta", "ocup_media_todos"])
conf("sec04 média Direta depois", 61.6, g.loc["Direta", "ocup_media_valida"])
conf("sec04 % sem UTI Filantrópico", 29.4, g.loc["Filantrópico", "pct_sem_uti_sus"])
conf("sec04 % sem UTI Direta", 4.6, g.loc["Direta", "pct_sem_uti_sus"])
conf("sec04 total sem UTI", 688, g.loc["TOTAL", "n_obs_sem_uti_sus"], tol=0.5)
conf("sec04 % sem UTI total", 21.6, g.loc["TOTAL", "pct_sem_uti_sus"])
conf("sec04 correção em pp", -23.7, g.loc["Filantrópico", "vies_pp"])

print("=" * 78)
print("SEÇÃO 8 — correlação e decomposição de variância")
print("=" * 78)
conf("sec08 corr mort x UTI", 0.26, cor.loc["mort_all", "ocupacao_uti"], tol=0.005)
conf("sec08 corr mort x internação", 0.22,
     cor.loc["mort_all", "ocupacao_internacao"], tol=0.005)
v = var.set_index("indicador")["pct_within"] * 100
for rot, af, ind in [("alta complex", 4.5, "pct_alta_complex"),
                     ("faturamento", 8.3, "custo_saida"),
                     ("TMP", 13.1, "tmp"), ("mort geral", 16.0, "mort_all"),
                     ("mort ajustada", 16.0, "mort_sem_excl"),
                     ("ocup internação", 16.7, "ocupacao_internacao"),
                     ("ocup UTI", 66.3, "ocupacao_uti")]:
    conf(f"sec08 within {rot}", af, v[ind])
conf("sec08 between UTI", 33.7,
     var.set_index("indicador").loc["ocupacao_uti", "icc_between"] * 100)

print("=" * 78)
print("SEÇÃO 13b — segmentação")
print("=" * 78)
f = seg01[seg01["modelo_gestao_proxy"] == "TOTAL"].set_index("estrato")
for e, af in [("E1", 67), ("E2", 97), ("E3", 125), ("TOTAL", 289)]:
    conf(f"sec13b funil {e}", af, f.loc[e, "n_cnes"], tol=0.5)
fc = seg01.set_index(["estrato", "modelo_gestao_proxy"])["n_cnes"]
for (e, c), af in {("E1", "Direta"): 1, ("E2", "Direta"): 6,
                   ("E3", "Direta"): 20, ("E1", "OSS"): 2,
                   ("E2", "OSS"): 7, ("E3", "OSS"): 28,
                   ("E3", "Filantrópico"): 50, ("E3", "Privado"): 0}.items():
    conf(f"sec13b funil {e}/{c}", af, fc.loc[(e, c)], tol=0.5)

t = seg05[seg05["modelo_gestao_proxy"] == "TODAS"].set_index(
    ["indicador", "estrato_rotulo"])["mediana"]
grad = {("ocupacao_internacao", "sem_uti_sus"): 41.0,
        ("ocupacao_internacao", "uti_baixa_complex"): 66.1,
        ("ocupacao_internacao", "uti_alta_complex"): 90.2,
        ("tmp", "sem_uti_sus"): 3.19, ("tmp", "uti_baixa_complex"): 3.84,
        ("tmp", "uti_alta_complex"): 5.25,
        ("mort_all", "sem_uti_sus"): 0.0438,
        ("mort_all", "uti_baixa_complex"): 0.0585,
        ("mort_all", "uti_alta_complex"): 0.0587,
        ("ocupacao_uti_valida", "uti_baixa_complex"): 76.1,
        ("ocupacao_uti_valida", "uti_alta_complex"): 77.3}
for k, af in grad.items():
    tol = 0.0005 if k[0] == "mort_all" else 0.051
    conf(f"sec13b gradiente {k[0]}/{k[1]}", af, t.loc[k], tol=tol)
conf("sec13b custo E1", 658, t.loc[("custo_real", "sem_uti_sus")], tol=0.6)
conf("sec13b custo E2", 1294, t.loc[("custo_real", "uti_baixa_complex")], tol=0.6)
conf("sec13b custo E3", 1821, t.loc[("custo_real", "uti_alta_complex")], tol=0.6)

e3 = seg10[(seg10["recorte"] == "principal") &
           (seg10["estrato"] == "E3")].set_index("indicador")
res = {"Mortalidade geral": (-0.281, -0.442, -0.121, 0.001),
       "TMP (dias)": (-11.79, -17.6, -5.6, 0.0003),
       "Faturamento real/saída": (-9.24, -25.4, 10.4, 0.332),
       "Ocupação UTI (winsor.)": (25.52, -18.4, 93.0, 0.300),
       "Ocupação intern. ≤100 (B)": (27.01, -1.8, 64.3, 0.068)}
import math
for ind, (efeito, lo, hi, p) in res.items():
    r = e3.loc[ind]
    if ind == "Mortalidade geral":
        conf(f"sec13b E3 {ind} coef", efeito, r["coef_oss"], tol=0.001)
        conf(f"sec13b E3 {ind} lo", lo, r["ic95_lo"], tol=0.001)
        conf(f"sec13b E3 {ind} hi", hi, r["ic95_hi"], tol=0.001)
    else:
        conf(f"sec13b E3 {ind} efeito", efeito, r["efeito_pct"], tol=0.06)
        conf(f"sec13b E3 {ind} lo%", lo, (math.exp(r["ic95_lo"]) - 1) * 100, tol=0.06)
        conf(f"sec13b E3 {ind} hi%", hi, (math.exp(r["ic95_hi"]) - 1) * 100, tol=0.06)
    conf(f"sec13b E3 {ind} p", p, r["p_valor"], tol=0.001)
r = e3.loc["Superlot. internação (A)"]
conf("sec13b E3 binário coef", 0.74, r["coef_oss"], tol=0.005)
conf("sec13b E3 binário lo", -1.17, r["ic95_lo"], tol=0.005)
conf("sec13b E3 binário hi", 2.64, r["ic95_hi"], tol=0.005)

d3 = seg11[(seg11["bloco"] == "escores_medianos") &
           (seg11["estrato"] == "E3")].set_index("categoria")
conf("sec13b DEA OSS", 0.747, d3.loc["OSS", "te_bcc_corrigido"], tol=0.0005)
conf("sec13b DEA Direta", 0.687, d3.loc["Direta", "te_bcc_corrigido"], tol=0.0005)
s2 = seg11[(seg11["bloco"] == "segunda_etapa_truncada") &
           (seg11["estrato"] == "E3") &
           (seg11["termo"] == "categoriaOSS")].iloc[0]
conf("sec13b DEA 2a etapa coef", -0.601, s2["coef"], tol=0.001)
conf("sec13b DEA 2a etapa lo", -1.065, s2["ic95_lo"], tol=0.001)
conf("sec13b DEA 2a etapa hi", -0.169, s2["ic95_hi"], tol=0.001)

b3 = seg14[seg14["estrato"] == "E3"].set_index("categoria")
for c, af in [("Direta", 2.9), ("Filantrópico", 28.7), ("OSS", 35.5),
              ("Público Municipal", 36.4)]:
    conf(f"sec13b superlotação {c}", af, b3.loc[c, "pct_superlotacao"])
c3 = seg15[seg15["estrato"] == "E3"].set_index("categoria")
for c, cond, bruta in [("Direta", 67.9, 68.5), ("Filantrópico", 83.6, 89.9),
                       ("OSS", 89.0, 95.9), ("Público Municipal", 86.5, 94.5)]:
    conf(f"sec13b condicional {c}", cond, c3.loc[c, "mediana_condicional"])
    conf(f"sec13b bruta {c}", bruta, c3.loc[c, "mediana_bruta_conflaciona"])
e1t = seg10[(seg10["recorte"] == "principal") & (seg10["estrato"] == "E1") &
            (seg10["indicador"] == "TMP (dias)")].iloc[0]
conf("sec13b E1 TMP (exemplo de ruído)", -72.9, e1t["efeito_pct"])

print("=" * 78)
print("SEÇÃO 15 e APÊNDICE — Etapa 5")
print("=" * 78)
fi = fam.set_index("especificacao")
famrows = {"ZIG_comzero ziGamma(log), zi=~1": (30.4, 5.7, 60.8, 2489),
           "G_semzero  Gama(log)": (30.4, 5.7, 60.8, 2482),
           "T_semzero  Tweedie(log)": (27.0, 7.6, 49.8, 2482),
           "T_comzero  Tweedie(log)": (26.7, 6.7, 50.4, 2489),
           "LN_semzero lognormal": (25.9, -0.3, 59.0, 2482)}
for k, (ef, lo, hi, n) in famrows.items():
    r = fi.loc[k]
    conf(f"sec15 família {k[:12]} efeito", ef, r["efeito_pct"], tol=0.06)
    conf(f"sec15 família {k[:12]} lo%", lo, (math.exp(r["ic_lo"]) - 1) * 100, tol=0.06)
    conf(f"sec15 família {k[:12]} hi%", hi, (math.exp(r["ic_hi"]) - 1) * 100, tol=0.06)
    conf(f"sec15 família {k[:12]} n", n, r["n"], tol=0.5)
conf("sec15 coef ziGamma", 0.26548, fi.loc["ZIG_comzero ziGamma(log), zi=~1", "coef_oss"], tol=1e-5)
conf("sec15 coef Gama publicada", 0.26541, fi.loc["G_semzero  Gama(log)", "coef_oss"], tol=1e-5)
dist = fi.loc["T_semzero  Tweedie(log)", "coef_oss"] - fi.loc["LN_semzero lognormal", "coef_oss"]
conf("sec15 distância lognormal-Tweedie", 0.0087, dist, tol=0.0002)
ep_ln = fi.loc["LN_semzero lognormal", "ep"]
conf("sec15 EP lognormal vs Tweedie (%)", 41,
     (ep_ln / fi.loc["T_semzero  Tweedie(log)", "ep"] - 1) * 100, tol=0.6)
conf("sec15 EP lognormal vs Gama (%)", 11,
     (ep_ln / fi.loc["G_semzero  Gama(log)", "ep"] - 1) * 100, tol=0.6)
conf("sec15 amplitude entre famílias", 4.5, 30.41 - 25.89, tol=0.06)
conf("sec15 AIC lognormal", 2135.4, fi.loc["LN_semzero lognormal", "aic"], tol=0.1)

a = ant.set_index("modelo")
conf("sec15 ocupação publicada %", 12.53,
     a.loc["ORIG ocupacao_internacao (winsor. p99 painel)", "efeito_pct"])
conf("sec15 ocupação corrigida %", 11.46,
     a.loc["CORR internacao parte B (contínua <=100, sem winsor.)", "efeito_pct"])
conf("sec15 ocupação corrigida coef", 0.108,
     a.loc["CORR internacao parte B (contínua <=100, sem winsor.)", "coef_oss"], tol=0.001)
sw = varr[(varr["variante"] == "sem_switchers") &
          (varr["modelo_base"] == "int_parteB")].iloc[0]
conf("sec15 sem switchers corrigido", 0.218, sw["coef_oss"], tol=0.001)

de = dec.set_index("modelo")
conf("apA defeito limiar", 0.0005,
     de.loc["T10 limiar CORRIGIDO + amostra por desfecho", "coef_oss"] -
     de.loc["T00 limiar contaminado + amostra por DESFECHO", "coef_oss"], tol=5e-5)
conf("apA defeito amostra", -0.0026,
     de.loc["T01 limiar contaminado + amostra por CAPACIDADE", "coef_oss"] -
     de.loc["T00 limiar contaminado + amostra por DESFECHO", "coef_oss"], tol=5e-5)
conf("apA defeito winsor internação", -0.0002,
     de.loc["I1 log SEM winsorização, modelo único", "coef_oss"] -
     de.loc["I0 log winsorizado em 125,1 (original)", "coef_oss"], tol=5e-5)
# CUIDADO: existem DOIS efeitos de família no registro, e eles não são o
# mesmo número. O do arranjo 2x2 (T00 contra G00, limiar contaminado dos dois
# lados) dá -0,02676; o do "teste decisivo" (T_semzero contra G_semzero,
# limiar corrigido) dá -0,02649. O Apêndice cita os outros três defeitos pelo
# 2x2, então o par coerente ali é o 2x2. Conferir contra o outro faz o texto
# parecer errado quando é a checagem que compara peras com maçãs.
conf("apA efeito da família (2x2, coerente com os outros três)", -0.0268,
     de.loc["T00 limiar contaminado + amostra por DESFECHO", "coef_oss"] -
     de.loc["G00 Gama, limiar contaminado, amostra por desfecho", "coef_oss"],
     tol=5e-5)
conf("R10 efeito da família (teste decisivo, limiar corrigido)", -0.02649,
     fi.loc["T_semzero  Tweedie(log)", "coef_oss"] -
     fi.loc["G_semzero  Gama(log)", "coef_oss"], tol=5e-5)
zeros = fi.loc["T_comzero  Tweedie(log)", "coef_oss"] - fi.loc["T_semzero  Tweedie(log)", "coef_oss"]
fvar = fi.loc["T_semzero  Tweedie(log)", "coef_oss"] - fi.loc["G_semzero  Gama(log)", "coef_oss"]
conf("apA participação dos zeros (%)", 9, 100 * zeros / (zeros + fvar), tol=0.6)
conf("apA participação da variância (%)", 91, 100 * fvar / (zeros + fvar), tol=0.6)
conf("apA 7 zeros em 2489 (%)", 0.28, 100 * 7 / 2489, tol=0.006)

print()
print("=" * 78)
print(f"RESULTADO: {ok} conferências OK, {len(falhas)} divergências")
print("=" * 78)
for f_ in falhas:
    print(f"  [DIVERGE] {f_}")
if not falhas:
    print("  Nenhuma divergência entre texto e fonte.")
