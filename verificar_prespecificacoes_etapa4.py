# -*- coding: utf-8 -*-
"""
ETAPA 4 (Parte B) — Verificação das regras pré-especificadas, ANTES de estimar.

As regras 1, 2 e 3 da Etapa 4 foram fixadas sobre uma base de referência de
314 CNES (pré-ETAPA F). O painel definitivo tem 289 CNES × 11 anos = 3.179
obs. Este script confirma cada regra no painel definitivo e ABORTA quando a
premissa cai — é a condição de parar-e-reportar do prompt, executável.

O que cada verificação decide
-----------------------------
REGRA 1 (modelo em duas partes, R6) — a parte A é um binário estimado com
efeito de hospital. Sem variação WITHIN do binário não há desenho causal, só
comparação entre grupos. Aborta se a variação within colapsar em E3, ou se os
switchers de E3 não a apresentarem.

REGRA 2 (winsorização da UTI) — limiar p99 ÚNICO, calculado na subamostra
VÁLIDA (uti_sus > 0), para o painel inteiro. Por estrato os limiares divergem
muito e tornariam o desfecho incomparável entre estratos. O script reporta os
três para deixar a divergência auditável.

REGRA 3 (assimetria UTI × internação) — a justificativa de tratar internação
em duas partes e UTI como contínua é empírica: em internação o excesso acima
de 100% é fortemente diferencial entre OSS e Direta; em UTI é não-diferencial.
ABORTA se o diferencial aparecer em UTI, porque aí a assimetria cai.

Referências (base de 314 CNES) — ordem de grandeza, NÃO valores a reproduzir:
  R1: E3 binário OSS 34,1% × Direta 2,9%; 78 CNES com variação within
      (OSS 18, Direta 6, Filantrópico 28, Público Municipal 26);
      3 dos 4 switchers de E3 com variação within; contínua OSS 85,1 ×
      Direta 68,5; gap bruto ~27,4 e gap contínuo ~16,6.
  R2: p99 da subamostra válida ~179,3; por estrato ~223 (E2) e ~153 (E3).
  R3: internação OSS 27,6% × Direta 3,2% (razão 8,6); UTI ~4,8% em ambas.

Saída
-----
  Somente console. Não grava tabela e não toca o painel.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
PAINEL = RAIZ / "analises" / "painel_segmentado.csv"

# switchers Direta -> OSS alocados em E3 (Odilo Antunes 2750511 está em E2)
SWITCHERS_E3 = {2081695: "Sorocaba", 2078287: "Pérola",
                2082225: "Taipas", 2091755: "Vila Penteado"}

falhas: list[str] = []


def aborta(msg: str) -> None:
    falhas.append(msg)
    print(f"    >>> FALHA: {msg}")


def regra1(df: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("REGRA 1 — ocupação de internação em duas partes (R6)")
    print("=" * 72)

    df = df.copy()
    df["sobrecarga"] = (df["ocupacao_internacao"] > 100).astype(int)
    e3 = df[df["estrato"] == "E3"]

    print("\n  Parte A — binário de superlotação, dentro de E3")
    a = e3.groupby("modelo_gestao_proxy")["sobrecarga"].agg(
        n="size", n_cnes=lambda s: e3.loc[s.index, "cnes"].nunique(),
        pct=lambda s: 100 * s.mean())
    print(a.round(2).to_string())

    oss = float(a.loc["OSS", "pct"]) if "OSS" in a.index else np.nan
    direta = float(a.loc["Direta", "pct"]) if "Direta" in a.index else np.nan
    print(f"\n    OSS {oss:.1f}% × Direta {direta:.1f}% "
          f"(referência 34,1% × 2,9%)")
    if not (oss > direta):
        aborta("o diferencial OSS>Direta no binário de E3 não se confirma")

    print("\n  Variação WITHIN do binário em E3 (condição do desenho causal)")
    var_within = (e3.groupby(["modelo_gestao_proxy", "cnes"])["sobrecarga"]
                  .nunique().gt(1).groupby(level=0).sum())
    total_cnes = e3.groupby("modelo_gestao_proxy")["cnes"].nunique()
    comp = pd.DataFrame({"cnes_em_e3": total_cnes,
                         "com_variacao_within": var_within}).fillna(0).astype(int)
    print(comp.to_string())
    n_within = int(comp["com_variacao_within"].sum())
    print(f"\n    total com variação within: {n_within} CNES (referência 78)")
    if n_within == 0:
        aborta("variação within do binário colapsou em E3")
    for cat in ("OSS", "Direta"):
        if comp.get("com_variacao_within", {}).get(cat, 0) == 0:
            aborta(f"nenhum CNES {cat} com variação within do binário em E3")

    print("\n  Switchers de E3 — variação within do binário")
    ok_sw = 0
    for cnes, nome in SWITCHERS_E3.items():
        sub = e3[e3["cnes"] == cnes]
        if sub.empty:
            print(f"    {cnes} {nome:<15} AUSENTE de E3")
            continue
        varia = sub["sobrecarga"].nunique() > 1
        ok_sw += int(varia)
        print(f"    {cnes} {nome:<15} anos acima: "
              f"{int(sub['sobrecarga'].sum())}/{len(sub)}  "
              f"variação within: {'SIM' if varia else 'não'}")
    print(f"\n    switchers com variação within: {ok_sw}/4 (referência 3/4)")
    if ok_sw == 0:
        aborta("nenhum switcher de E3 tem variação within no binário")

    print("\n  Parte B — contínua condicional (<= 100), dentro de E3")
    cond = e3[e3["ocupacao_internacao"] <= 100]
    b = cond.groupby("modelo_gestao_proxy")["ocupacao_internacao"].agg(
        n="size", mediana="median", media="mean")
    print(b.round(1).to_string())

    print("\n  Decomposição do gap OSS − Direta em E3 (mediana, bruto)")
    bruto = e3.groupby("modelo_gestao_proxy")["ocupacao_internacao"].median()
    gap_bruto = float(bruto.get("OSS", np.nan) - bruto.get("Direta", np.nan))
    gap_cond = float(b["mediana"].get("OSS", np.nan)
                     - b["mediana"].get("Direta", np.nan))
    print(f"    gap bruto (conflaciona as duas partes) .. {gap_bruto:+.1f} pontos")
    print(f"    gap da parte contínua ................... {gap_cond:+.1f} pontos")
    if np.isfinite(gap_bruto) and abs(gap_bruto) > 1e-9:
        share = 100 * (1 - gap_cond / gap_bruto)
        print(f"    fração do gap que era FREQUÊNCIA de superlotação: "
              f"{share:.0f}%  (referência ~40%)")


def regra2(df: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("REGRA 2 — winsorização da ocupação de UTI, limiar ÚNICO")
    print("=" * 72)

    valida = df[df["ocupacao_uti_valida"].notna()]
    p99 = float(np.percentile(valida["ocupacao_uti_valida"], 99))
    print(f"\n  subamostra válida (uti_sus > 0): {len(valida)} obs, "
          f"{valida['cnes'].nunique()} CNES")
    print(f"  p99 da subamostra válida — LIMIAR ADOTADO: {p99:.1f} "
          f"(referência ~179,3)")

    p99_cont = float(np.percentile(df["ocupacao_uti"].dropna(), 99))
    print(f"\n  divergência deliberada de preparo_fase2.R, que usa o p99 do "
          f"painel\n  contaminado pelos zeros estruturais: {p99_cont:.1f}")

    print("\n  Por que NÃO por estrato (limiares incomparáveis):")
    for est in sorted(valida["estrato"].unique()):
        sub = valida[valida["estrato"] == est]
        print(f"    {est}: p99 = {np.percentile(sub['ocupacao_uti_valida'], 99):7.1f}"
              f"   (n = {len(sub)})")

    print("\n  Observações winsorizadas pelo limiar único, por estrato e categoria")
    w = valida[valida["ocupacao_uti_valida"] > p99]
    if w.empty:
        print("    (nenhuma)")
    else:
        print(pd.crosstab(w["estrato"], w["modelo_gestao_proxy"]).to_string())
        print(f"    total: {len(w)} obs "
              f"({100 * len(w) / len(valida):.1f}% da subamostra válida)")


def regra3(df: pd.DataFrame) -> None:
    print("\n" + "=" * 72)
    print("REGRA 3 — assimetria entre UTI e internação (justifica R6)")
    print("=" * 72)

    print("\n  Excesso acima de 100% — INTERNAÇÃO (painel inteiro)")
    ints = df.groupby("modelo_gestao_proxy")["ocupacao_internacao"].agg(
        n="size", pct_acima=lambda s: 100 * (s > 100).mean())
    print(ints.round(2).to_string())
    i_oss = float(ints.loc["OSS", "pct_acima"])
    i_dir = float(ints.loc["Direta", "pct_acima"])
    razao_int = i_oss / i_dir if i_dir > 0 else np.inf
    print(f"    OSS {i_oss:.1f}% / Direta {i_dir:.1f}% = razão {razao_int:.1f}"
          f"   (referência 27,6 / 3,2 = 8,6)")

    print("\n  Excesso acima de 100% — UTI (subamostra válida)")
    valida = df[df["ocupacao_uti_valida"].notna()]
    utis = valida.groupby("modelo_gestao_proxy")["ocupacao_uti_valida"].agg(
        n="size", pct_acima=lambda s: 100 * (s > 100).mean())
    print(utis.round(2).to_string())
    u_oss = float(utis.loc["OSS", "pct_acima"])
    u_dir = float(utis.loc["Direta", "pct_acima"])
    razao_uti = u_oss / u_dir if u_dir > 0 else np.inf
    print(f"    OSS {u_oss:.1f}% / Direta {u_dir:.1f}% = razão {razao_uti:.1f}"
          f"   (referência ~4,8 / ~4,8 = ~1,0)")

    print(f"\n  Assimetria: razão em internação {razao_int:.1f} contra "
          f"{razao_uti:.1f} em UTI.")
    if not np.isfinite(razao_uti):
        aborta("razão de UTI não é finita — Direta sem excesso; inspecionar")
    elif razao_uti >= razao_int / 2:
        aborta(f"o diferencial APARECEU em UTI (razão {razao_uti:.1f} contra "
               f"{razao_int:.1f} em internação): a justificativa da "
               f"assimetria cai e R6 precisa ser reaberta")
    else:
        print("    Assimetria confirmada: internação é diferencial, UTI não.")


def main() -> None:
    if not PAINEL.exists():
        sys.exit(f"painel não encontrado: {PAINEL}")
    df = pd.read_csv(PAINEL)
    n_cnes, n_anos = df["cnes"].nunique(), df["ano"].nunique()
    print(f"painel: {len(df)} obs, {n_cnes} CNES, {n_anos} anos")
    if len(df) != n_cnes * n_anos:
        sys.exit("painel não balanceado — abortando")

    regra1(df)
    regra2(df)
    regra3(df)

    print("\n" + "=" * 72)
    if falhas:
        print(f"VERIFICAÇÃO FALHOU — {len(falhas)} premissa(s) caíram:")
        for f in falhas:
            print(f"  - {f}")
        print("PARAR E REPORTAR. Não estimar sobre premissa caída.")
        sys.exit(1)
    print("TODAS AS PREMISSAS PRÉ-ESPECIFICADAS CONFIRMADAS. Liberado estimar.")
    print("=" * 72)


if __name__ == "__main__":
    main()
