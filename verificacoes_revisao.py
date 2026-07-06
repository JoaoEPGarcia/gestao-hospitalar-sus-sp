# -*- coding: utf-8 -*-
"""
verificacoes_revisao.py
=======================
Verificações numéricas da rodada de correção do relatório (revisão
externa de jul/2026). Cada bloco imprime o valor encontrado no dado
antes de a edição correspondente ser aplicada nos arquivos .tex.
"""
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
painel = pd.read_csv(r"C:\ProjetoPosDoc\analises\painel_definitivo.csv",
                     encoding="utf-8-sig")

print("=" * 66)
print("A1. Categoria modal por CNES (atribuição única do heatmap)")
print("=" * 66)


def modal(s):
    return s.value_counts().idxmax()


cat_modal = painel.groupby("cnes")["modelo_gestao_proxy"].agg(modal)
print(cat_modal.value_counts().to_string())
for cnes in [2081695, 2078287, 2082225, 2091755, 2750511]:
    print(f"  conversor {cnes}: modal = {cat_modal[cnes]}")

med = painel.groupby("cnes")["total_leitos"].median()
porte = med.apply(lambda x: "Médio" if x <= 150
                  else ("Grande" if x <= 500 else "Especial"))
priv = cat_modal[cat_modal == "Privado"].index
print("\nPorte fixo dos 3 CNES Privados:")
for c in priv:
    print(f"  {c}: mediana de leitos {med[c]:.0f} -> {porte[c]}")

print("\n" + "=" * 66)
print("A2. CNES 2022648 em 2021: denominador da ocupação de UTI")
print("=" * 66)
r = painel[(painel["cnes"] == 2022648) & (painel["ano"] == 2021)].iloc[0]
for c in ["ocupacao_uti", "diarias_uti", "uti_total", "uti_sus",
          "total_leitos"]:
    print(f"  {c}: {r[c]}")
for nome, leitos in [("uti_total", r["uti_total"]),
                     ("uti_sus", r["uti_sus"])]:
    if leitos and leitos > 0:
        print(f"  diarias/({nome} x 365) = "
              f"{100 * r['diarias_uti'] / (leitos * 365):.1f}%")
den = r["diarias_uti"] / (r["ocupacao_uti"] / 100) / 365
print(f"  denominador implícito da ocupação registrada: {den:.2f} leitos")

print("\n" + "=" * 66)
print("A5 e C10. Correlações de Spearman com 4 casas")
print("=" * 66)
oc = stats.spearmanr(painel["ocupacao_internacao"],
                     painel["ocupacao_uti"]).statistic
mm = stats.spearmanr(painel["mort_all"], painel["mort_sem_excl"]).statistic
print(f"  ocupação internação x ocupação UTI: {oc:.4f}")
print(f"  mort_all x mort_sem_excl:           {mm:.6f}")

print("\n" + "=" * 66)
print("C2. Os quatro N diferentes de 3.454")
print("=" * 66)
n_tmp0 = int((painel["tmp"] == 0).sum())
fragil = (painel["cnes"] == 2097613) & painel["ano"].isin([2020, 2021])
tmp_med = painel.groupby("cnes")["tmp"].median()
lp = set(tmp_med[tmp_med > 20].index)
obs_lp = int(painel["cnes"].isin(lp).sum())
uti_pos = int((painel["ocupacao_uti"] > 0).sum())
uti_pos_fragil = int(((painel["ocupacao_uti"] > 0) & fragil).sum())
print(f"  observações com tmp = 0: {n_tmp0} -> 3.454 - {n_tmp0} = "
      f"{3454 - n_tmp0}")
print(f"  frágeis: {int(fragil.sum())} -> 3.454 - 2 = {3454 - 2}")
print(f"  obs de longa permanência: {obs_lp}; "
      f"3.454 - {obs_lp} - {n_tmp0} = {3454 - obs_lp - n_tmp0}")
print(f"  UTI ativa no painel: {uti_pos}; frágeis com UTI ativa: "
      f"{uti_pos_fragil} -> {uti_pos} - {uti_pos_fragil} = "
      f"{uti_pos - uti_pos_fragil}")

print("\n" + "=" * 66)
print("C9. Assimetrias da mortalidade: bruta vs logito")
print("=" * 66)
m = painel["mort_all"]
interior = m[(m > 0) & (m < 1)]
print(f"  assimetria escala original (Tabela 1): "
      f"{stats.skew(m):.2f}")
print(f"  assimetria do logito (interior): "
      f"{stats.skew(np.log(interior / (1 - interior))):.2f}")

print("\n" + "=" * 66)
print("F. Tabela 5 (variância) e Sorocaba 14,8 vs 14,9")
print("=" * 66)
for col in ["mort_all", "mort_sem_excl"]:
    media_i = painel.groupby("cnes")[col].transform("mean")
    var_within = ((painel[col] - media_i) ** 2).sum()
    var_total = ((painel[col] - painel[col].mean()) ** 2).sum()
    w = 100 * var_within / var_total
    print(f"  {col}: within {w:.2f}% -> between {100 - w:.2f}%")
conv = pd.read_csv(r"C:\ProjetoPosDoc\analises\tabelas\tab_ae_conversores_pre_pos.csv",
                   encoding="utf-8-sig")
s = conv[(conv["cnes"] == 2081695) & (conv["indicador"] == "mort_all")].iloc[0]
q = 100 * (s["mediana_pre"] - s["mediana_pos"]) / s["mediana_pre"]
print(f"  Sorocaba mort: pre {s['mediana_pre']:.4f}, pos "
      f"{s['mediana_pos']:.4f}, queda {q:.2f}%")

print("\n" + "=" * 66)
print("B1 (prévia). n_linhas_resumo como contagem de competências")
print("=" * 66)
print(painel["n_linhas_resumo"].describe().to_string())
print("  distribuição de n_linhas_resumo:")
print(painel["n_linhas_resumo"].value_counts().sort_index().to_string())
r2 = painel[(painel["cnes"] == 2022648) & (painel["ano"] == 2021)].iloc[0]
print(f"  CNES 2022648 em 2021: n_linhas_resumo = {r2['n_linhas_resumo']}")
