# -*- coding: utf-8 -*-
"""
verificacao_tipo_modal.py
=========================
Verificações solicitadas antes de aprovar a regra do VALOR MODAL para
tipo_hospital/especializacao (Etapa A do painel definitivo):

  (a) Quantos CNES têm cadastro INSTÁVEL de tipo_hospital ao longo dos anos
      com produção (mais de um valor informativo distinto), e quantos foram
      efetivamente marcados no log de revisão manual;
  (b) Quantos CNES teriam decisão DIFERENTE na Etapa A (excluído vs. mantido)
      se, em vez da MODA, a classificação fixa usasse o valor do ÚLTIMO ANO
      com produção — com a lista nominal dos casos divergentes.

  (c) Bônus (item 2 da mesma rodada): quais CNES excluídos na Etapa C1
      dependeram do ano de 2019 no critério ANOS_CAMPANHA — i.e., produção
      contida em {2019,2020,2021} mas NÃO contida em {2020,2021}.

Não altera nada. USO: python verificacao_tipo_modal.py
"""

import pandas as pd

import analise_sih as base
import construir_painel_definitivo as cpd


def classificar(cod_tipo, cod_espec):
    """Reproduz a decisão da Etapa A a partir dos códigos extraídos."""
    if cod_tipo == "62":
        return "EXCLUI: hospital dia (62)"
    if cod_tipo == "70":
        return "EXCLUI: CAPS (70)"
    if cod_tipo == "07" and cod_espec == "006":
        return "EXCLUI: psiquiátrico (07+006)"
    return "MANTÉM"


def main():
    painel = cpd.carregar_painel_bruto()
    prod = painel[painel["qtde"] > 0].copy()

    # ── (a) instabilidade de cadastro ────────────────────────────────────────
    informativo = (~prod["tipo_hospital"].isin(["N/A", "#N/A", "-"])
                   & prod["tipo_hospital"].notna())
    tipos_por_cnes = (prod[informativo].groupby("cnes")["tipo_hospital"]
                      .agg(lambda s: sorted(set(s))))
    instaveis = tipos_por_cnes[tipos_por_cnes.map(len) > 1]
    print("=" * 70)
    print("(a) INSTABILIDADE DE CADASTRO DE tipo_hospital")
    print("=" * 70)
    print(f"CNES com produção e tipo informativo: {len(tipos_por_cnes)}")
    print(f"CNES com MAIS de um tipo distinto entre anos: {len(instaveis)}")

    aud_rev = pd.read_csv(cpd.TAB_AUD_REVISAO, encoding="utf-8-sig")
    n_log = (aud_rev["etapa"] == "ETAPA A").sum()
    print(f"CNES no log de revisão manual da Etapa A (tocou 62/70 e foi "
          f"mantido pela moda): {n_log}")

    # ── (b) moda × último ano ────────────────────────────────────────────────
    moda_tipo  = cpd.valor_modal_por_cnes(painel, "tipo_hospital")
    moda_espec = cpd.valor_modal_por_cnes(painel, "especializacao")

    def ultimo_valor(coluna):
        sub = prod[~prod[coluna].isin(["N/A", "#N/A", "-"])
                   & prod[coluna].notna()]
        return sub.sort_values("ano").groupby("cnes")[coluna].last()

    ult_tipo, ult_espec = ultimo_valor("tipo_hospital"), ultimo_valor("especializacao")

    linhas = []
    for cnes in tipos_por_cnes.index:
        dec_moda = classificar(cpd.extrair_codigo(moda_tipo.get(cnes)),
                               cpd.extrair_codigo(moda_espec.get(cnes)))
        dec_ult  = classificar(cpd.extrair_codigo(ult_tipo.get(cnes)),
                               cpd.extrair_codigo(ult_espec.get(cnes)))
        if dec_moda != dec_ult:
            hist = (prod[prod["cnes"] == cnes].sort_values("ano"))
            linhas.append({
                "cnes": cnes,
                "decisao_moda": dec_moda,
                "decisao_ultimo_ano": dec_ult,
                "historico_tipo": "; ".join(
                    f"{int(a)}={t}" for a, t in
                    zip(hist["ano"], hist["tipo_hospital"].fillna("?"))),
            })
    print("\n" + "=" * 70)
    print("(b) DIVERGÊNCIAS MODA × ÚLTIMO ANO NA DECISÃO DA ETAPA A")
    print("=" * 70)
    print(f"CNES com decisão diferente: {len(linhas)}")
    if linhas:
        with pd.option_context("display.max_colwidth", 150, "display.width", 250):
            print(pd.DataFrame(linhas).to_string(index=False))

    # ── (c) dependência do ano 2019 na Etapa C1 ─────────────────────────────
    aud_rem = pd.read_csv(cpd.TAB_AUD_REMOVIDOS, encoding="utf-8-sig")
    rem_c1 = aud_rem[aud_rem["etapa"] == "ETAPA C1"]["cnes"].astype(int)
    anos_prod = prod.groupby("cnes")["ano"].agg(lambda s: set(s.astype(int)))
    dependentes = [c for c in rem_c1
                   if not anos_prod.get(c, set()) <= {2020, 2021}]
    print("\n" + "=" * 70)
    print("(c) EXCLUÍDOS NA ETAPA C1 QUE DEPENDEM DO ANO 2019 NO CRITÉRIO")
    print("=" * 70)
    print(f"CNES excluídos em C1: {len(rem_c1)} | dependentes de 2019: "
          f"{len(dependentes)} {dependentes if dependentes else ''}")
    print("(Se 0, o critério pode ser estreitado para 2020-2021 sem alterar "
          "nenhum resultado.)")


if __name__ == "__main__":
    main()
