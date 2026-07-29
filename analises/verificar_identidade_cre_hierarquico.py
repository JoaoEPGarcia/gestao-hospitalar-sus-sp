# verificar_identidade_cre_hierarquico.py
# ITENS 1.2 e 1.3 do fechamento de 29/07/2026.
#
# Por que este script existe
# --------------------------
# R9 apresentava a concordância entre CRE/Mundlak e o hierárquico como se
# fossem duas estimativas próximas ("TMP -0,1254 no CRE/Mundlak contra -0,1255
# no hierárquico"). Não são duas estimativas: é o MESMO número, -0,12545,
# arredondado para lados diferentes. Este script mede a distância entre os dois
# estimadores em TODOS os indicadores de E3, para que a afirmação que vai ao
# registro seja verificada e não asserida.
#
# O que se esperava e o que os dados mostram
# ------------------------------------------
# A hipótese inicial era "nos indicadores log-lineares os dois coincidem por
# construção". Ela é BOA DEMAIS e os dados a recusam: a ocupação de internação
# parte B também é log-linear e NÃO coincide (0,23910 contra 0,21112).
#
# A condição correta é mais estreita. Incluir as médias por hospital (Mundlak)
# num modelo de efeitos aleatórios torna o estimador de EA numericamente igual
# ao within/efeitos fixos — resultado algébrico clássico — mas a igualdade é
# EXATA apenas em painel LINEAR e BALANCEADO. Este script testa as duas
# condições juntas, que é o que distingue identidade algébrica de concordância
# empírica.
#
# Saída: console + analises/tabelas/tabSEG_16_identidade_estimadores.csv

import math
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
TAB = RAIZ / "tabelas"

cre = pd.read_csv(TAB / "tabSEG_10_cre_mundlak_por_estrato.csv")
cre.columns = [c.lstrip("﻿") for c in cre.columns]
cre = cre[(cre["recorte"] == "principal") & (cre["estrato"] == "E3")]

hie = pd.read_csv(TAB / "tabSEG_12_bayes_por_estrato.csv")
hie = hie[hie["estrato"] == "E3"]

# o rótulo difere entre as duas tabelas em três dos seis indicadores
PARES = [
    ("Mortalidade geral", "Mortalidade geral"),
    ("TMP (dias)", "TMP (log)"),
    ("Faturamento real/saída", "Faturamento real (log)"),
    ("Ocupação UTI (winsor.)", "Ocupação UTI (winsor.)"),
    ("Superlot. internação (A)", "Superlot. internação (A)"),
    ("Ocupação intern. ≤100 (B)", "Ocupação intern. <=100 (B)"),
]

ANOS = 11  # o painel tem 11 anos por CNES; balanceado ⇔ n_obs == n_cnes × 11

print("=" * 92)
print("ITEM 1.2 — quando os dois estimadores coincidem, e por quê. Estrato E3.")
print("=" * 92)
print(f"{'indicador':<27}{'escala':<12}{'painel':<14}"
      f"{'CRE/Mundlak':>12}{'hierárq.':>12}{'|dif|':>10}")
print("-" * 92)

linhas = []
for nome_cre, nome_hie in PARES:
    lc = cre[cre["indicador"] == nome_cre]
    lh = hie[hie["indicador"] == nome_hie]
    if lc.empty or lh.empty:
        print(f"{nome_cre:<27}{'—':<12}{'—':<14}{'ausente':>34}")
        continue

    escala = str(lc["escala"].iloc[0])
    n_obs = float(lc["n_obs"].iloc[0])
    n_cnes = float(lc["n_cnes"].iloc[0])
    balanceado = abs(n_obs - n_cnes * ANOS) < 0.5
    rotulo_painel = ("balanceado" if balanceado
                     else f"desbal. {n_obs:.0f}/{n_cnes:.0f}")

    c = float(lc["coef_oss"].iloc[0])
    h = float(lh["coef_oss"].iloc[0])
    dif = abs(c - h)
    # CUIDADO: "logito" também começa com "log". Linear no link é a escala
    # `log` EXATA; `logito` e `log (PPML)` são links não-lineares.
    linear = escala.strip() == "log"

    print(f"{nome_cre:<27}{escala:<12}{rotulo_painel:<14}"
          f"{c:>12.5f}{h:>12.5f}{dif:>10.5f}")

    linhas.append({
        "indicador": nome_cre,
        "escala": escala,
        "linear_no_link": linear,
        "painel_balanceado": balanceado,
        "n_obs": int(n_obs), "n_cnes": int(n_cnes),
        "coef_cre_mundlak": round(c, 5),
        "coef_hierarquico": round(h, 5),
        "dif_absoluta": round(dif, 5),
        "identicos_5_casas": bool(dif < 1e-5),
        "ep_cluster_robusto": round(float(lc["ep_cluster"].iloc[0]), 5),
        "ep_baseado_no_modelo": round(float(lh["ep"].iloc[0]), 5),
    })

df = pd.DataFrame(linhas)

print()
print("As duas condições, testadas juntas:")
for _, r in df.iterrows():
    cond = r["linear_no_link"] and r["painel_balanceado"]
    print(f"  {r['indicador']:<27} linear={str(r['linear_no_link']):<5} "
          f"balanceado={str(r['painel_balanceado']):<5} "
          f"→ esperado idêntico={str(cond):<5} "
          f"observado idêntico={str(r['identicos_5_casas'])}")

acerto = (df["linear_no_link"] & df["painel_balanceado"]) == df["identicos_5_casas"]
print()
print(f"A regra 'linear E balanceado ⇔ idêntico' acerta em "
      f"{int(acerto.sum())} dos {len(df)} indicadores.")
print()
print("Leitura: a identidade NÃO é propriedade de 'ser log-linear'. A parte B")
print("é log-linear e não coincide, porque o painel dela é desbalanceado — a")
print("equivalência Mundlak/within é exata só em painel linear e balanceado.")

print()
print("=" * 92)
print("ITEM 1.3 — mesmo coeficiente, vereditos opostos: faturamento em E3")
print("=" * 92)

lc = cre[cre["indicador"] == "Faturamento real/saída"]
lh = hie[hie["indicador"] == "Faturamento real (log)"]

coef = float(lc["coef_oss"].iloc[0])
ep_c = float(lc["ep_cluster"].iloc[0])
lo_c, hi_c = float(lc["ic95_lo"].iloc[0]), float(lc["ic95_hi"].iloc[0])
ep_h = float(lh["ep"].iloc[0])
lo_h, hi_h = float(lh["ic95_lo"].iloc[0]), float(lh["ic95_hi"].iloc[0])

print(f"coeficiente, idêntico nos dois: {coef:+.5f}   "
      f"({int(lc['n_cnes'].iloc[0])} CNES em E3)")
print()
print(f"CRE/Mundlak  EP cluster-robusto {ep_c:.5f}   "
      f"IC95% log [{lo_c:+.5f}, {hi_c:+.5f}]")
print(f"             em percentual                "
      f"[{(math.exp(lo_c) - 1) * 100:+.2f}%, {(math.exp(hi_c) - 1) * 100:+.2f}%]"
      f"   cruza o zero: {lo_c < 0 < hi_c}")
print()
print(f"hierárquico  EP do modelo       {ep_h:.5f}   "
      f"IC95% log [{lo_h:+.5f}, {hi_h:+.5f}]")
print(f"             em percentual                "
      f"[{(math.exp(lo_h) - 1) * 100:+.2f}%, {(math.exp(hi_h) - 1) * 100:+.2f}%]"
      f"   cruza o zero: {lo_h < 0 < hi_h}")
print()
print(f"razão entre os erros-padrão: {ep_c / ep_h:.3f}× — o cluster-robusto é o maior")
print()
print("CORREÇÃO DE R9: o limite inferior consta como -25,2%; o correto é")
print(f"exp({lo_c:.5f}) - 1 = {(math.exp(lo_c) - 1) * 100:.2f}%, isto é -25,4%.")
print(f"O limite superior consta como +10,4% e confere: "
      f"{(math.exp(hi_c) - 1) * 100:.2f}%.")

df["ic95_lo_pct"] = None
df["ic95_hi_pct"] = None
idx = df.index[df["indicador"] == "Faturamento real/saída"]
df.loc[idx, "ic95_lo_pct"] = round((math.exp(lo_c) - 1) * 100, 2)
df.loc[idx, "ic95_hi_pct"] = round((math.exp(hi_c) - 1) * 100, 2)

df.to_csv(TAB / "tabSEG_16_identidade_estimadores.csv",
          index=False, encoding="utf-8")
print()
print("[TAB] tabSEG_16_identidade_estimadores.csv")
