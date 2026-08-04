"""
listas_estruturais.py
=====================
Gera as duas listas nominais do Apêndice D e confere os números que o
Sumário Executivo cita da segmentação estrutural.

Motivo (04/08/2026, a pedido de João): o documento afirmava, desde a Seção 2
e a Seção 5, que 31,3% dos hospitais-ano não registram alta complexidade e
que 35 hospitais nunca a registram em onze anos, mas nunca dizia QUAIS. O
mesmo vale, e com mais força, para a UTI: 21,6% das observações são de
hospital sem leito de UTI do SUS cadastrado, e o leitor não tinha como saber
se isso é sempre o mesmo hospital ou um cadastro que oscila. Uma lista
nominal responde às duas perguntas de uma vez e é auditável por quem conhece
a rede.

As duas listas usam o MESMO critério: hospital cuja contagem é zero em
TODOS os onze anos do painel. Quem tem zero em alguns anos e não em outros
fica fora das listas e aparece contado à parte, porque a oscilação é outro
fenômeno (no caso da UTI, suspensão e limpeza de cadastro, conforme a
Subseção dos três estratos da Seção 14).

Saídas:
  tab_ap_sem_alta_complexidade.csv  — os 35 que nunca registram alta complex.
  tab_ap_sem_uti_sus.csv            — os 49 que nunca têm leito de UTI SUS
  (e as duas listas em LaTeX, prontas para o apêndice, no stdout)

USO: python analises/listas_estruturais.py
"""

import sys
import unicodedata
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import analise_sih as base  # noqa: E402

FONTE = base.PASTA_ANALISES / "painel_definitivo.csv"


def _titulo(s: str) -> str:
    """Nome de hospital em caixa de título, com as partículas em minúscula.

    A base grava o nome fantasia com capitalização própria ("Hospital De
    Clinicas"), e a lista impressa fica visualmente melhor com as partículas
    rebaixadas. Nada além da caixa é alterado: o nome continua sendo o do
    cadastro, para que a lista possa ser conferida contra o CNES.
    """
    particulas = {"de", "da", "do", "das", "dos", "e", "em"}
    palavras = str(s).split()
    return " ".join(p.lower() if (i and p.lower() in particulas) else p
                    for i, p in enumerate(palavras))


def _tex(s: str) -> str:
    """Escapa o que o LaTeX interpretaria dentro de uma célula de tabela."""
    for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")):
        s = s.replace(a, b)
    return s


def _ordenar(df: pd.DataFrame) -> pd.DataFrame:
    """Ordena por nome ignorando acento, para a lista sair em ordem
    alfabética de verdade e não com os acentuados no fim."""
    chave = df["nome"].map(
        lambda s: unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore").decode().lower())
    return df.assign(_k=chave).sort_values("_k").drop(columns="_k")


def _perfil(painel: pd.DataFrame, cnes) -> pd.DataFrame:
    sub = painel[painel["cnes"].isin(cnes)]
    return _ordenar(sub.groupby("cnes").agg(
        nome=("nome_fantasia", "last"),
        municipio=("municipio", "last"),
        rede=("modelo_gestao_proxy", "last"),
        leitos_sus=("leitos_sus", "median"),
        faixa=("faixa_barcelona", "last"),
    ).reset_index()).assign(nome=lambda d: d["nome"].map(_titulo))


def _imprimir_tex(df: pd.DataFrame, colunas: list) -> None:
    for _, r in df.iterrows():
        campos = " & ".join(
            (f"{r[c]:.0f}" if isinstance(r[c], float) else _tex(str(r[c])))
            for c in colunas)
        print(f"{campos} \\\\")


def main() -> None:
    base.configurar_diretorios()
    painel = pd.read_csv(FONTE, encoding="utf-8-sig")
    n_obs, n_cnes = len(painel), painel["cnes"].nunique()
    print(f"[0] Painel: {n_cnes} hospitais, {n_obs} observações.")
    if (n_cnes, n_obs) != (289, 3179):
        raise SystemExit("[0] PAINEL NÃO CONFERE. PARANDO.")

    g = painel.groupby("cnes")

    # ── 1. Nunca registram alta complexidade ──────────────────────────────
    total_ac = g["qtde_alta_complex"].sum()
    sem_ac = total_ac[total_ac == 0].index
    obs_zero_ac = int((painel["pct_alta_complex"] == 0).sum())
    algum_ano_ac = painel.loc[painel["pct_alta_complex"] == 0,
                              "cnes"].nunique()
    print(f"\n[1] ALTA COMPLEXIDADE")
    print(f"    observações com zero: {obs_zero_ac} "
          f"({obs_zero_ac / n_obs:.1%})")
    print(f"    hospitais com ao menos um ano em zero: {algum_ano_ac}")
    print(f"    hospitais com zero nos ONZE anos: {len(sem_ac)}")
    perfil_ac = _perfil(painel, sem_ac)
    print(f"    por rede: {perfil_ac['rede'].value_counts().to_dict()}")
    print(f"    na faixa 2 de complexidade: "
          f"{int((perfil_ac['faixa'] == 2).sum())}")
    perfil_ac.to_csv(base.PASTA_TABELAS / "tab_ap_sem_alta_complexidade.csv",
                     index=False, encoding="utf-8-sig")

    # ── 2. Nunca têm leito de UTI SUS ─────────────────────────────────────
    painel["tem_uti"] = painel["uti_sus"].fillna(0) > 0
    anos_com_uti = painel.groupby("cnes")["tem_uti"].sum()
    sem_uti = anos_com_uti[anos_com_uti == 0].index
    sempre_uti = anos_com_uti[anos_com_uti == 11].index
    oscila = anos_com_uti[(anos_com_uti > 0) & (anos_com_uti < 11)].index
    obs_sem_uti = int((~painel["tem_uti"]).sum())
    print(f"\n[2] UTI SUS")
    print(f"    observações sem leito de UTI SUS: {obs_sem_uti} "
          f"({obs_sem_uti / n_obs:.1%})")
    print(f"    hospitais SEM UTI nos onze anos: {len(sem_uti)} "
          f"({len(sem_uti) * 11} observações)")
    print(f"    hospitais COM UTI nos onze anos: {len(sempre_uti)}")
    print(f"    hospitais que oscilam:            {len(oscila)} "
          f"({obs_sem_uti - len(sem_uti) * 11} observações sem UTI)")
    perfil_uti = _perfil(painel, sem_uti)
    print(f"    por rede: {perfil_uti['rede'].value_counts().to_dict()}")
    # quantos deles têm UTI NÃO SUS (leito privado dentro do mesmo hospital)
    tem_uti_total = (painel[painel["cnes"].isin(sem_uti)]
                     .groupby("cnes")["uti_total"].max().fillna(0) > 0)
    print(f"    dos quais com UTI não SUS em algum ano: "
          f"{int(tem_uti_total.sum())}")
    nas_duas = sorted(set(sem_ac) & set(sem_uti))
    print(f"    nas DUAS listas: {len(nas_duas)}")
    perfil_uti.to_csv(base.PASTA_TABELAS / "tab_ap_sem_uti_sus.csv",
                      index=False, encoding="utf-8-sig")

    # ── 3. Confere os números da segmentação citados no Sumário ───────────
    # E3 = mediana de leitos de UTI SUS positiva e faixa Barcelona >= 4.
    # Definição da Seção 14; reproduzida aqui para conferir os totais que o
    # Sumário Executivo passou a citar (125 hospitais em E3, 28 OSS e 20 da
    # administração Direta).
    #
    # ATENÇÃO ao conferir contra a Tabela dos estratos da Seção 14: lá os
    # cinco conversores são contados NAS DUAS categorias que ocuparam, por
    # convenção declarada na legenda. Aqui cada hospital entra uma vez só,
    # na categoria em que terminou, e por isso a Direta sai com 5 em E2 e
    # 16 em E3. A diferença é exatamente a dos conversores: +1 em E2
    # (Presidente Prudente) e +4 em E3 (Sorocaba, Pérola Byington, Taipas e
    # Vila Penteado), que reconstroem os 6 e os 20 publicados. Os totais por
    # estrato, que é o que o Sumário cita, coincidem sem ressalva.
    med_uti = g["uti_sus"].median()
    faixa = g["faixa_barcelona"].last()
    rede = g["modelo_gestao_proxy"].last()
    e3 = (med_uti > 0) & (faixa >= 4)
    e2 = (med_uti > 0) & (faixa < 4)
    e1 = med_uti <= 0
    print(f"\n[3] ESTRATOS (para o Sumário Executivo)")
    for nome, m in (("E1 sem UTI", e1), ("E2 UTI baixa", e2),
                    ("E3 UTI alta", e3)):
        d = rede[m].value_counts()
        print(f"    {nome:14s} {int(m.sum()):3d} hospitais "
              f"({m.sum() / n_cnes:.0%}) | "
              f"Direta {d.get('Direta', 0)}, OSS {d.get('OSS', 0)}")
    dentro = set(sem_uti) <= set(e1[e1].index)
    print(f"    os {len(sem_uti)} sem UTI estão todos em E1: {dentro} "
          f"(E1 tem {int(e1.sum())})")

    # ── 4. Blocos LaTeX prontos para o apêndice ───────────────────────────
    print("\n" + "=" * 70)
    print("% ---- LISTA 1: nunca registram alta complexidade ----")
    _imprimir_tex(perfil_ac, ["nome", "municipio", "rede", "leitos_sus"])
    print("\n% ---- LISTA 2: nunca têm leito de UTI SUS ----")
    _imprimir_tex(perfil_uti, ["nome", "municipio", "rede", "leitos_sus"])


if __name__ == "__main__":
    main()
