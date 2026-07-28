# -*- coding: utf-8 -*-
"""
ETAPA 4 (Parte A) — Verificação do piscar cadastral de UTI (R7).

O que se afirma em R7
---------------------
A oscilação de `uti_sus` entre anos é SUSPENSÃO E LIMPEZA CADASTRAL — por
exemplo inativação temporária por falta de intensivista — e não construção ou
demolição de ala. A capacidade subjacente é estável; o cadastro é que pisca.

Consequência verificável, e é ela que este script mede: se o cadastro pisca
enquanto a ala continua operando, devem existir observações com `uti_sus == 0`
E produção de UTI ativa (`diarias_uti > 0`). Se o zero fosse sempre ausência
real de UTI, essas observações não existiriam.

O contraste com a internação é o controle: `leitos_sus == 0` com
`diarias_internacao > 0` não deve ocorrer, porque leito de internação não é
habilitação que se suspende do mesmo modo.

Por que isso REFORÇA a estratificação fixa
------------------------------------------
O estrato é atribuído por CNES, pela MEDIANA de `uti_sus` nos onze anos, e
fica fixo no período. Se as oscilações fossem obra física, a classificação
fixa apagaria mudança real de tecnologia de produção. Sendo piscar cadastral,
a mediana é justamente o estimador certo da capacidade subjacente: ela ignora
os anos em que o registro caiu sem que a ala fechasse.

O que este script NÃO muda
--------------------------
A ETAPA 1 continua válida. `ocupacao_uti` segue indefinida com denominador
zero, e essas observações saem do modelo de qualquer forma — é por isso que
existe `ocupacao_uti_valida`, definida apenas onde `uti_sus > 0`.

O que muda é o MOTIVO REGISTRADO. Das observações com `uti_sus == 0`, a
maioria é ausência real de UTI e uma minoria é piscar cadastral com operação
ativa. As duas passam a ficar distinguidas no registro, em vez de somadas sob
o rótulo único de "sem UTI".

Números de referência (base de 314 CNES, pré-ETAPA F): 39 observações em 27
CNES, mediana de 775 diárias no Filantrópico, concentradas em 2017, 2020,
2021 e 2025; nenhum caso em internação. São ordem de grandeza esperada, NÃO
valores a reproduzir — o painel definitivo tem 289 CNES × 11 anos.

Saída
-----
  analises/tabelas/tabSEG_09_piscar_cadastral.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent
PAINEL = RAIZ / "analises" / "painel_segmentado.csv"
SAIDA = RAIZ / "analises" / "tabelas" / "tabSEG_09_piscar_cadastral.csv"


def carregar() -> pd.DataFrame:
    if not PAINEL.exists():
        sys.exit(f"painel não encontrado: {PAINEL}")
    df = pd.read_csv(PAINEL)
    n_cnes, n_anos = df["cnes"].nunique(), df["ano"].nunique()
    if len(df) != n_cnes * n_anos:
        sys.exit(f"painel não balanceado: {len(df)} != {n_cnes} × {n_anos}")
    print(f"painel: {len(df)} obs, {n_cnes} CNES, {n_anos} anos")
    return df


def piscar_uti(df: pd.DataFrame) -> pd.DataFrame:
    """Observações com cadastro zerado e produção ativa."""
    return df[(df["uti_sus"] == 0) & (df["diarias_uti"] > 0)].copy()


def main() -> None:
    df = carregar()

    zerados = df[df["uti_sus"] == 0]
    pisca = piscar_uti(df)
    ausencia_real = zerados[~zerados.index.isin(pisca.index)]

    print("\n=== 1. Decomposição das observações com uti_sus == 0 ===")
    print(f"  total com uti_sus == 0 ......... {len(zerados)} obs, "
          f"{zerados['cnes'].nunique()} CNES")
    print(f"  piscar cadastral (diarias>0) ... {len(pisca)} obs, "
          f"{pisca['cnes'].nunique()} CNES")
    print(f"  ausência real (diarias==0/NA) .. {len(ausencia_real)} obs, "
          f"{ausencia_real['cnes'].nunique()} CNES")

    print("\n=== 2. Piscar por categoria de gestão ===")
    por_cat = pisca.groupby("modelo_gestao_proxy")["diarias_uti"].agg(
        n_obs="size", n_cnes=lambda s: pisca.loc[s.index, "cnes"].nunique(),
        mediana_diarias="median", min_diarias="min", max_diarias="max",
    )
    print(por_cat.round(1).to_string() if len(por_cat) else "  (nenhum caso)")

    print("\n=== 3. Piscar por ano ===")
    por_ano = pisca.groupby("ano").size()
    print(por_ano.to_string() if len(por_ano) else "  (nenhum caso)")

    print("\n=== 4. Piscar por estrato ===")
    por_est = pisca.groupby(["estrato", "estrato_rotulo"]).size()
    print(por_est.to_string() if len(por_est) else "  (nenhum caso)")

    print("\n=== 5. Controle — internação ===")
    pisca_int = df[(df["leitos_sus"] == 0) & (df["diarias_internacao"] > 0)]
    print(f"  leitos_sus == 0 e diarias_internacao > 0: {len(pisca_int)} obs")
    if len(pisca_int):
        print("  ATENÇÃO: o controle falhou — R7 previa nenhum caso.")

    print("\n=== 6. Oscilação de uti_sus dentro do CNES ===")
    def oscila(g: pd.Series) -> bool:
        return (g > 0).any() and (g == 0).any()
    osc = df.groupby("cnes")["uti_sus"].apply(oscila)
    print(f"  CNES com uti_sus ora zero ora positivo: {int(osc.sum())}")
    cnes_pisca = sorted(pisca["cnes"].unique())
    print(f"  destes, com produção ativa em ano zerado: "
          f"{len([c for c in cnes_pisca if osc.get(c, False)])}")

    # ---- tabela de saída: uma linha por observação de piscar --------------
    cols = ["cnes", "nome_fantasia", "ano", "modelo_gestao_proxy", "estrato",
            "estrato_rotulo", "uti_sus", "uti_total", "diarias_uti",
            "uti_sus_mediana", "estrato_instavel"]
    tab = pisca[cols].sort_values(["ano", "cnes"]).reset_index(drop=True)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    tab.to_csv(SAIDA, index=False, encoding="utf-8")
    print(f"\ngravado: {SAIDA.relative_to(RAIZ)}  ({len(tab)} linhas)")


if __name__ == "__main__":
    main()
