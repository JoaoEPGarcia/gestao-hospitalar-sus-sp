"""
selecao_entrevistas.py
======================
Fase qualitativa da pesquisa: seleção de hospitais para entrevistas
semiestruturadas e geração do roteiro de perguntas, ancorados nos achados
da fase de estimação (relatório principal.pdf):
  - regime operacional mais intenso e eficiência maior das OSS (robustos);
  - TMP menor nas OSS: evidência sugestiva within (5 conversores, -10,2%);
  - mortalidade menor concentrada na trajetória dos conversores, não
    sobrevive ao controle sintético;
  - faturamento real por saída não difere entre categorias.

Blocos de seleção:
  a) 5 conversores Direta->OSS (inclusão obrigatória);
  b) desviantes positivos: quartil superior persistente de te_bcc_vc E
     te_sfa (mediana dos anos), um por categoria, suporte comum
     (faixas Barcelona 3-4, portes médio e grande);
  c) desviantes negativos: espelho do bloco b (quartil inferior);
  d) pares casados de contraste: OSS de alta eficiência vs vizinho mais
     próximo em Direta e Filantrópico com eficiência divergente;
  e) divergência DEA x SFA: maiores |rank_dea - rank_sfa|;
  f) validação de registro: CNES 2022648 (ocupação UTI 875% em 2021) e
     CNES 2097613 (denominadores frágeis 2020-21) — entrevistas curtas.

RESTRIÇÕES HONRADAS: Privado (n=3) fora dos blocos b-e; os 18 CNES de
longa permanência fora dos blocos b-d; mortalidade sempre acompanhada de
complexidade_estrutural, nunca de complexidade_pond_mort; diversidade
geográfica (capital vs interior) como desempate.

Saídas: analises/tabelas/tab_selecao_entrevistas.csv;
        analises/figuras_selecao_entrevistas/fig_sel_*.png (blocos b-d,
        mesmo estilo das figuras de trajetória dos conversores do
        relatório, figuras 26-35);
        analises/latex/roteiro_entrevistas.tex (pdflatex, TeX Live 2023,
        sem babel e sem lmodern, com as substituições padrão do projeto).

USO: python selecao_entrevistas.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import analise_sih as base        # embrulha stdout no encoding do terminal
import estimacao as est           # constantes, carga verificada e preparo

# ══════════════════════════════════════════════════════════════════════════════
# A. CONSTANTES
# ══════════════════════════════════════════════════════════════════════════════

PASTA_FIG_SEL = base.PASTA_ANALISES / "figuras_selecao_entrevistas"
PASTA_LATEX = base.PASTA_ANALISES / "latex"

# os 4 indicadores da fase qualitativa são os 4 achados da estimação
INDICADORES_QUALI = ["tmp", "mort_all", "custo_real", "qtde"]
ROT_QUALI = {
    "tmp":        "TMP (dias)",
    "mort_all":   "Mortalidade geral",
    "custo_real": "Faturamento real por saída (R$ de 2025)",
    "qtde":       "Saídas hospitalares (produção)",
}

CATEGORIAS_BC = ["OSS", "Direta", "Público Municipal", "Filantrópico"]

# candidatos quase empatados no escore combinado (diferença menor que
# 2 pontos percentuais) desempatam pela diversidade geográfica
TOL_EMPATE = 0.02

# nº de âncoras OSS do bloco d (o enunciado pede 2 a 3; 2 mantém o total
# de entrevistas dentro do teto de 15 a 18)
N_ANCORAS_OSS = 2

# divergência mínima de eficiência exigida do par casado: pelo menos
# 25 pontos percentuais abaixo da âncora no escore combinado
DIVERGENCIA_PAR = 0.25

# nº de casos de divergência DEA x SFA (o enunciado pede 3 a 5)
N_DIVERGENCIA = 5

# validação de registro (entrevistas curtas de cadastro, não de gestão)
CNES_VALIDACAO = {
    2022648: "ocupação de UTI de 875% em 2021: verificar leitos CNES "
             "cadastrados vs leitos operacionais na pandemia",
    2097613: "denominadores frágeis em 2020-21 (menos de 30 saídas sem "
             "COVID no biênio, TMP zero em 2021): verificar registro de "
             "produção no SIH",
}


def _capital(municipio: str) -> str:
    return "capital" if municipio == "Sao Paulo" else "interior"


def _pt(v, nd=1) -> str:
    """Número em formato PT-BR (vírgula decimal, ponto de milhar)."""
    if pd.isna(v):
        return "--"
    s = f"{v:,.{nd}f}"
    return s.replace(",", "@").replace(".", ",").replace("@", ".")


def _salvar_fig(fig, nome: str):
    fig.savefig(PASTA_FIG_SEL / nome, dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    print(f"  [FIG] {nome}")


# ══════════════════════════════════════════════════════════════════════════════
# 1. CARGA, MERGE DAS EFICIÊNCIAS E RESUMO POR CNES
# ══════════════════════════════════════════════════════════════════════════════

def preparar_base():
    painel = est.carregar_e_verificar()
    painel = est.preparar(painel)

    dea = pd.read_csv("resultados_fase2/dea/dea_escores_principal.csv",
                      encoding="utf-8")[["cnes", "ano", "te_bcc_vc"]]
    sfa = pd.read_csv("resultados_fase2/sfa/sfa_eficiencias.csv",
                      encoding="utf-8")[["cnes", "ano", "te_sfa"]]
    painel = painel.merge(dea, on=["cnes", "ano"], how="left")
    painel = painel.merge(sfa, on=["cnes", "ano"], how="left")
    print(f"\n[1] Eficiências mescladas: te_bcc_vc com "
          f"{painel['te_bcc_vc'].notna().sum()} obs, te_sfa com "
          f"{painel['te_sfa'].notna().sum()} obs (de {len(painel)})")

    # medianas por CNES; indicadores assistenciais excluem as 2 observações
    # de denominador frágil (CNES 2097613, 2020-21)
    ok = painel[painel["flag_fragil"] == 0]
    resumo = ok.groupby("cnes").agg(
        municipio=("municipio", lambda s: s.dropna().iloc[-1]),
        porte_fixo=("porte_fixo", "first"),
        faixa_barcelona=("faixa_barcelona",
                         lambda s: int(s.mode().iloc[0])),
        leitos_med=("total_leitos", "median"),
        longa_perm=("longa_perm", "max"),
        complexidade_estrutural=("complexidade_estrutural", "first"),
        te_dea_med=("te_bcc_vc", "median"),
        te_sfa_med=("te_sfa", "median"),
        tmp_med=("tmp", "median"),
        mort_med=("mort_all", "median"),
        custo_med=("custo_real", "median"),
        qtde_med=("qtde", "median"),
    )
    resumo["nome"] = [est.NOMES_CNES.get(c, str(c)) for c in resumo.index]
    resumo["geografia"] = resumo["municipio"].map(_capital)

    # categoria fixa por CNES: modal; conversores marcados à parte
    cat_modal = painel.groupby("cnes")["modelo_gestao_proxy"].agg(
        lambda s: s.mode().iloc[0])
    resumo["categoria"] = cat_modal
    resumo.loc[list(est.CONVERSOES), "categoria"] = "OSS (conversor)"

    # ranks e percentis na rede elegível (sem Privado, sem frágil,
    # sem conversores — estes já são o bloco a)
    eleg = resumo[(~resumo["categoria"].isin(["Privado", "OSS (conversor)"]))
                  & (resumo.index != est.CNES_FRAGIL)].copy()
    eleg["rank_dea"] = eleg["te_dea_med"].rank(ascending=False)
    eleg["rank_sfa"] = eleg["te_sfa_med"].rank(ascending=False)
    eleg["pct_dea"] = eleg["te_dea_med"].rank(pct=True)
    eleg["pct_sfa"] = eleg["te_sfa_med"].rank(pct=True)
    eleg["pct_comb"] = (eleg["pct_dea"] + eleg["pct_sfa"]) / 2
    print(f"[1] Rede elegível para os blocos b-e: {len(eleg)} CNES "
          f"(excluídos Privado n=3, 5 conversores e o frágil {est.CNES_FRAGIL})")
    return painel, resumo, eleg


# ══════════════════════════════════════════════════════════════════════════════
# 2. BLOCOS DE SELEÇÃO
# ══════════════════════════════════════════════════════════════════════════════

def _linha(bloco, cnes, resumo, papel, justificativa, tipo="plena"):
    r = resumo.loc[cnes]
    return {"bloco": bloco, "cnes": cnes, "nome": r["nome"],
            "municipio": r["municipio"], "geografia": r["geografia"],
            "categoria": r["categoria"], "porte": r["porte_fixo"],
            "faixa_barcelona": r["faixa_barcelona"],
            "leitos_mediana": round(r["leitos_med"], 0),
            "te_bcc_vc_mediana": round(r["te_dea_med"], 3),
            "te_sfa_mediana": round(r["te_sfa_med"], 3),
            "tmp_mediana": round(r["tmp_med"], 2),
            "mort_all_mediana": round(r["mort_med"], 4),
            "custo_real_mediana": round(r["custo_med"], 0),
            "qtde_mediana": round(r["qtde_med"], 0),
            "complexidade_estrutural": round(r["complexidade_estrutural"], 1),
            "papel": papel, "tipo_entrevista": tipo,
            "justificativa": justificativa}


def bloco_a(painel, resumo):
    """Conversores: inclusão obrigatória, trajetória antes/depois nos
    4 indicadores da fase qualitativa."""
    print("\n" + "=" * 70)
    print("[a] CONVERSORES DIRETA->OSS (inclusão obrigatória)")
    print("=" * 70)
    linhas, trajetorias = [], []
    ok = painel[painel["flag_fragil"] == 0]
    for cnes, ano_conv in est.CONVERSOES.items():
        sub = ok[ok["cnes"] == cnes].set_index("ano")
        partes = []
        for c in INDICADORES_QUALI:
            pre = sub.loc[sub.index < ano_conv, c].median()
            pos = sub.loc[sub.index >= ano_conv, c].median()
            var = (pos / pre - 1) if pre else np.nan
            trajetorias.append({"cnes": cnes, "indicador": c,
                                "ano_conversao": ano_conv,
                                "mediana_pre": round(pre, 4),
                                "mediana_pos": round(pos, 4),
                                "variacao_relativa": round(var, 4)})
            partes.append(f"{ROT_QUALI[c]}: {_pt(pre, 2)} -> {_pt(pos, 2)} "
                          f"({_pt(var * 100, 1)}%)")
        nota_pos = (" [apenas 1 ano pós: sem leitura de tendência]"
                    if ano_conv == 2025 else "")
        just = (f"Conversor Direta->OSS em {ano_conv}{nota_pos}. "
                f"Antes/depois (medianas): " + "; ".join(partes))
        linhas.append(_linha("a_conversor", cnes, resumo,
                             f"conversor ({ano_conv})", just))
        print(f"  CNES {cnes} ({resumo.loc[cnes, 'nome']}, "
              f"{resumo.loc[cnes, 'municipio']}), conversão {ano_conv}:")
        for p in partes:
            print(f"    {p}")
    tab = pd.DataFrame(trajetorias)
    tab.to_csv(base.PASTA_TABELAS / "tab_sel_conversores_trajetoria.csv",
               index=False, encoding="utf-8-sig")
    print("  [TAB] tab_sel_conversores_trajetoria.csv")
    return linhas


def _selecionar_extremos(eleg, superior: bool):
    """Um CNES por categoria no quartil superior (ou inferior) persistente
    de te_bcc_vc E te_sfa, no suporte comum, sem longa permanência.
    Desempate por diversidade geográfica entre quase-empatados."""
    pool = eleg[eleg["faixa_barcelona"].isin([3, 4])
                & eleg["porte_fixo"].isin(["Médio Porte", "Grande Porte"])
                & (eleg["longa_perm"] == 0)].copy()
    q_dea = pool["te_dea_med"].quantile(.75 if superior else .25)
    q_sfa = pool["te_sfa_med"].quantile(.75 if superior else .25)
    lado = "superior" if superior else "inferior"
    print(f"  Suporte comum sem longa permanência: {len(pool)} CNES; "
          f"quartil {lado}: te_bcc_vc {'>=' if superior else '<='} "
          f"{q_dea:.3f} E te_sfa {'>=' if superior else '<='} {q_sfa:.3f}")

    escolhidos, geografias = [], []
    for cat in CATEGORIAS_BC:
        if superior:
            cand = pool[(pool["categoria"] == cat)
                        & (pool["te_dea_med"] >= q_dea)
                        & (pool["te_sfa_med"] >= q_sfa)]
        else:
            cand = pool[(pool["categoria"] == cat)
                        & (pool["te_dea_med"] <= q_dea)
                        & (pool["te_sfa_med"] <= q_sfa)]
        relaxado = False
        if cand.empty:
            # relaxamento documentado: quartil em um método e metade
            # correspondente no outro
            med_sfa = pool["te_sfa_med"].median()
            if superior:
                cand = pool[(pool["categoria"] == cat)
                            & (pool["te_dea_med"] >= q_dea)
                            & (pool["te_sfa_med"] >= med_sfa)]
            else:
                cand = pool[(pool["categoria"] == cat)
                            & (pool["te_dea_med"] <= q_dea)
                            & (pool["te_sfa_med"] <= med_sfa)]
            relaxado = True
        if cand.empty:
            print(f"  {cat}: NENHUM candidato no quartil {lado} do suporte "
                  f"comum (mesmo com critério relaxado)")
            continue
        cand = cand.sort_values("pct_comb", ascending=not superior)
        melhor = cand.iloc[0]
        # desempate geográfico entre quase-empatados
        quase = cand[(cand["pct_comb"] - melhor["pct_comb"]).abs()
                     < TOL_EMPATE]
        if len(quase) > 1 and geografias:
            falta = ("interior" if geografias.count("capital")
                     >= geografias.count("interior") else "capital")
            alt = quase[quase["geografia"] == falta]
            if not alt.empty:
                melhor = alt.iloc[0]
        geografias.append(melhor["geografia"])
        escolhidos.append((melhor.name, cat, relaxado, melhor))
        print(f"  {cat}: CNES {melhor.name} ({melhor['nome']}, "
              f"{melhor['municipio']}) te_bcc_vc {melhor['te_dea_med']:.3f}, "
              f"te_sfa {melhor['te_sfa_med']:.3f}"
              + (" [critério relaxado]" if relaxado else ""))
    return escolhidos


def bloco_bc(eleg, resumo):
    print("\n" + "=" * 70)
    print("[b] DESVIANTES POSITIVOS (quartil superior persistente, "
          "suporte comum)")
    print("=" * 70)
    linhas_b = []
    for cnes, cat, relax, r in _selecionar_extremos(eleg, superior=True):
        just = (f"Desviante positivo da categoria {cat}"
                + (" (critério relaxado: quartil superior de DEA e acima "
                   "da mediana de SFA)" if relax else
                   " (quartil superior persistente de te_bcc_vc e te_sfa)")
                + f": eficiência DEA {_pt(r['te_dea_med'], 3)} e SFA "
                  f"{_pt(r['te_sfa_med'], 3)} (medianas 2015-2025), "
                  f"no suporte comum (faixa {r['faixa_barcelona']}, "
                  f"{r['porte_fixo']}).")
        linhas_b.append(_linha("b_desviante_positivo", cnes, resumo,
                               f"desviante positivo {cat}", just))

    print("\n" + "=" * 70)
    print("[c] DESVIANTES NEGATIVOS (quartil inferior persistente, "
          "suporte comum)")
    print("=" * 70)
    linhas_c = []
    ja = {l["cnes"] for l in linhas_b}
    for cnes, cat, relax, r in _selecionar_extremos(eleg, superior=False):
        if cnes in ja:
            continue
        just = (f"Desviante negativo da categoria {cat}"
                + (" (critério relaxado: quartil inferior de DEA e abaixo "
                   "da mediana de SFA)" if relax else
                   " (quartil inferior persistente de te_bcc_vc e te_sfa)")
                + f": eficiência DEA {_pt(r['te_dea_med'], 3)} e SFA "
                  f"{_pt(r['te_sfa_med'], 3)} (medianas 2015-2025), "
                  f"no suporte comum (faixa {r['faixa_barcelona']}, "
                  f"{r['porte_fixo']}).")
        linhas_c.append(_linha("c_desviante_negativo", cnes, resumo,
                               f"desviante negativo {cat}", just))
    return linhas_b, linhas_c


def bloco_d(eleg, resumo, linhas_b):
    """Pares casados: para as âncoras OSS de alta eficiência, o vizinho
    mais próximo em Direta e em Filantrópico com eficiência divergente."""
    print("\n" + "=" * 70)
    print(f"[d] PARES CASADOS DE CONTRASTE ({N_ANCORAS_OSS} âncoras OSS)")
    print("=" * 70)
    pool = eleg[eleg["faixa_barcelona"].isin([3, 4])
                & eleg["porte_fixo"].isin(["Médio Porte", "Grande Porte"])
                & (eleg["longa_perm"] == 0)].copy()
    ancoras = (pool[pool["categoria"] == "OSS"]
               .sort_values("pct_comb", ascending=False)
               .head(N_ANCORAS_OSS))
    ja_b = {l["cnes"] for l in linhas_b}
    linhas = []
    for cnes_a, a in ancoras.iterrows():
        reuso = (" — já selecionado no bloco b, mesma entrevista"
                 if cnes_a in ja_b else "")
        print(f"  Âncora OSS: CNES {cnes_a} ({a['nome']}, {a['municipio']}) "
              f"pct_comb {a['pct_comb']:.2f}{reuso}")
        if cnes_a not in ja_b and cnes_a not in {l["cnes"] for l in linhas}:
            linhas.append(_linha(
                "d_par_casado", cnes_a, resumo, "âncora OSS",
                f"Âncora OSS de alta eficiência (DEA {_pt(a['te_dea_med'], 3)}, "
                f"SFA {_pt(a['te_sfa_med'], 3)}) para os pares casados."))
        for cat_par in ["Direta", "Filantrópico"]:
            cand = pool[(pool["categoria"] == cat_par)
                        & (pool["porte_fixo"] == a["porte_fixo"])
                        & (pool["pct_comb"] <= a["pct_comb"]
                           - DIVERGENCIA_PAR)].copy()
            if cand.empty:
                print(f"    {cat_par}: sem par com porte igual e "
                      f"eficiência divergente")
                continue
            # distância: leitos em log; faixa diferente e município
            # diferente penalizam (região aproxima quando possível)
            cand["dist"] = (
                np.abs(np.log(cand["leitos_med"] / a["leitos_med"]))
                + 0.5 * (cand["faixa_barcelona"]
                         != a["faixa_barcelona"]).astype(float)
                + 0.1 * (cand["municipio"] != a["municipio"]).astype(float))
            par = cand.sort_values("dist").iloc[0]
            if par.name in {l["cnes"] for l in linhas}:
                print(f"    {cat_par}: melhor par (CNES {par.name}) já "
                      f"selecionado; mantido sem duplicar")
                continue
            just = (f"Par casado da âncora OSS {a['nome']} (CNES {cnes_a}): "
                    f"mesmo porte ({par['porte_fixo']}), faixa Barcelona "
                    f"{par['faixa_barcelona']} vs {a['faixa_barcelona']}, "
                    f"leitos {_pt(par['leitos_med'], 0)} vs "
                    f"{_pt(a['leitos_med'], 0)}, mas eficiência divergente: "
                    f"DEA {_pt(par['te_dea_med'], 3)} vs "
                    f"{_pt(a['te_dea_med'], 3)}; SFA "
                    f"{_pt(par['te_sfa_med'], 3)} vs "
                    f"{_pt(a['te_sfa_med'], 3)}. Estrutura parecida, "
                    f"gestão {cat_par}: o que a gestão faz de diferente?")
            linhas.append(_linha("d_par_casado", par.name, resumo,
                                 f"par {cat_par} da âncora {cnes_a}", just))
            print(f"    {cat_par}: CNES {par.name} ({par['nome']}, "
                  f"{par['municipio']}) leitos {par['leitos_med']:.0f}, "
                  f"pct_comb {par['pct_comb']:.2f} "
                  f"(divergência {a['pct_comb'] - par['pct_comb']:.2f})")
    return linhas, list(ancoras.index)


def bloco_e(eleg, resumo, ja_selecionados):
    """Divergência DEA x SFA: maiores |rank_dea - rank_sfa| na rede
    elegível (longa permanência pode entrar; anotada quando presente)."""
    print("\n" + "=" * 70)
    print(f"[e] DIVERGÊNCIA DEA x SFA (top {N_DIVERGENCIA} de "
          f"|rank_dea - rank_sfa|)")
    print("=" * 70)
    d = eleg.copy()
    d["diff_rank"] = (d["rank_dea"] - d["rank_sfa"]).abs()
    d = d.sort_values("diff_rank", ascending=False)
    linhas = []
    for cnes, r in d.iterrows():
        if len(linhas) >= N_DIVERGENCIA:
            break
        if cnes in ja_selecionados:
            continue
        lp = " Hospital de longa permanência." if r["longa_perm"] else ""
        lado = ("DEA favorável, SFA desfavorável"
                if r["rank_dea"] < r["rank_sfa"]
                else "SFA favorável, DEA desfavorável")
        just = (f"Divergência DEA x SFA: rank DEA {int(r['rank_dea'])} vs "
                f"rank SFA {int(r['rank_sfa'])} entre {len(d)} CNES "
                f"(|dif| = {int(r['diff_rank'])}; {lado}; te_bcc_vc "
                f"{_pt(r['te_dea_med'], 3)}, te_sfa "
                f"{_pt(r['te_sfa_med'], 3)}). Os dois métodos discordam: "
                f"há algo que os modelos não capturam.{lp}")
        linhas.append(_linha("e_divergencia_dea_sfa", cnes, resumo,
                             "divergência DEA x SFA", just))
        print(f"  CNES {cnes} ({r['nome']}, {r['municipio']}, "
              f"{r['categoria']}): rank DEA {int(r['rank_dea'])} vs "
              f"rank SFA {int(r['rank_sfa'])} (|dif| {int(r['diff_rank'])})"
              + (" [longa permanência]" if r["longa_perm"] else ""))
    return linhas


def bloco_f(painel, resumo):
    print("\n" + "=" * 70)
    print("[f] VALIDAÇÃO DE REGISTRO (entrevistas curtas de cadastro)")
    print("=" * 70)
    linhas = []
    for cnes, motivo in CNES_VALIDACAO.items():
        sub = painel[painel["cnes"] == cnes].set_index("ano")
        if cnes == 2022648:
            detalhe = (f"Ocupação de UTI registrada: 2020 = "
                       f"{_pt(sub.loc[2020, 'ocupacao_uti'])}%, 2021 = "
                       f"{_pt(sub.loc[2021, 'ocupacao_uti'])}% "
                       f"(leitos UTI cadastrados: "
                       f"{int(sub.loc[2021, 'uti_total'])}).")
        else:
            detalhe = (f"Saídas registradas: 2020 = "
                       f"{_pt(sub.loc[2020, 'qtde'], 0)}, 2021 = "
                       f"{_pt(sub.loc[2021, 'qtde'], 0)}; TMP 2021 = "
                       f"{_pt(sub.loc[2021, 'tmp'], 2)}.")
        linhas.append(_linha("f_validacao_registro", cnes, resumo,
                             "validação de registro",
                             f"{motivo}. {detalhe}", tipo="curta"))
        print(f"  CNES {cnes} ({resumo.loc[cnes, 'nome']}, "
              f"{resumo.loc[cnes, 'municipio']}): {detalhe}")
    return linhas


# ══════════════════════════════════════════════════════════════════════════════
# 3. FIGURAS DOS BLOCOS b-d (estilo das figuras 26-35 do relatório)
# ══════════════════════════════════════════════════════════════════════════════

def figuras_trajetoria(painel, linhas_bcd):
    print("\n" + "=" * 70)
    print("[FIG] Trajetórias dos selecionados nos blocos b-d vs mediana "
          "da própria categoria")
    print("=" * 70)
    PASTA_FIG_SEL.mkdir(exist_ok=True)
    ok = painel[painel["flag_fragil"] == 0]
    anos = sorted(ok["ano"].unique())
    med_cat = ok.groupby(["ano", "modelo_gestao_proxy"])[
        INDICADORES_QUALI].median()
    feitos = set()
    for l in linhas_bcd:
        cnes = l["cnes"]
        if cnes in feitos:
            continue
        feitos.add(cnes)
        cat = l["categoria"]
        sub = ok[ok["cnes"] == cnes].set_index("ano")
        fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.6))
        for ax, c in zip(axes.ravel(), INDICADORES_QUALI):
            s = med_cat.xs(cat, level=1)[c]
            ax.plot(s.index, s.values, ls="dashed", lw=1.1,
                    marker=est.MARCADORES.get(cat, "o"), ms=3.5,
                    color=est.CORES_CAT.get(cat, est.COR_APOIO), alpha=.75,
                    label=f"mediana {cat}")
            ax.plot(anos, sub[c].reindex(anos), "o", ls="solid",
                    color="#0b0b0b", lw=1.7, ms=4, label="hospital")
            ax.set_title(ROT_QUALI[c], fontsize=11)
            ax.tick_params(axis="x", rotation=45)
            ax.legend(fontsize=8.5)
        fig.suptitle(f"{l['nome']} (CNES {cnes}, {l['municipio']}) — "
                     f"{l['papel']}", fontsize=12)
        fig.tight_layout()
        _salvar_fig(fig, f"fig_sel_{l['bloco'][0]}_{cnes}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. ROTEIRO DE ENTREVISTAS EM LATEX
# ══════════════════════════════════════════════════════════════════════════════

def _tex_escapar(s: str) -> str:
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"),
                 ("#", r"\#"), ("_", r"\_"), ("$", r"\$")]:
        s = s.replace(a, b)
    return s


def _tex_pergunta(pergunta: str, achado: str) -> str:
    return (f"  \\item {pergunta}\n"
            f"  \\par\\nopagebreak\\achado{{{achado}}}\n")


def gerar_tex(selecao: pd.DataFrame, n_unicos: int, n_plenas: int,
              n_curtas: int):
    print("\n" + "=" * 70)
    print("[TEX] roteiro_entrevistas.tex")
    print("=" * 70)

    preambulo = r"""% roteiro_entrevistas.tex — fase qualitativa da pesquisa
% Gerado por selecao_entrevistas.py. Compilar com pdflatex (TeX Live 2023).
% Substituições padrão do projeto: sem babel português e sem lmodern;
% \sloppy, \emergencystretch=3em, microtype sem expansão nem protrusão,
% xcolor carregado antes de hyperref.
\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[top=2.2cm, bottom=2.2cm, left=2.4cm, right=2.4cm]{geometry}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage[expansion=false,protrusion=false]{microtype}
\usepackage{xcolor}
\usepackage[hidelinks]{hyperref}
\sloppy
\emergencystretch=3em

% linha que liga cada pergunta ao achado quantitativo que ela testa
\newcommand{\achado}[1]{%
  \noindent{\small\itshape\textcolor{black!60}{Achado que a pergunta
  testa: #1}}\par\smallskip}

\title{Roteiro de Entrevistas Semiestruturadas\\
  {\large Fase Qualitativa --- Gest\~ao Hospitalar no SUS/SP, 2015--2025}}
\author{Jo\~ao Eduardo Pastori Garcia (Estat\'istico Respons\'avel)}
\date{Julho de 2026}

\begin{document}
\maketitle
\tableofcontents
\clearpage
"""

    # ── seção 1: apresentação ──────────────────────────────────────────────
    sec1 = r"""
\section{Apresentação e método}

Este roteiro operacionaliza a fase qualitativa da pesquisa sobre o efeito
do modelo institucional de gestão no desempenho de hospitais SUS de São
Paulo (painel balanceado de 314 hospitais, 2015 a 2025). A fase de
estimação, concluída, deixou quatro achados que as entrevistas devem
explicar por dentro: (i) o regime operacional mais intenso e a eficiência
técnica maior das OSS (DEA-BCC corrigida de viés e SFA-BC95) são traços
robustos da rede; (ii) o tempo médio de permanência cerca de 10\% menor
nas OSS é evidência sugestiva de variação dentro do hospital, apoiada em
apenas 5 conversores; (iii) a mortalidade menor concentra-se na
trajetória dos conversores e não sobrevive ao controle sintético, o que
recomenda cautela e investigação de mecanismo; (iv) o faturamento real por
saída não difere entre categorias --- a diferença de gestão, se existe,
não aparece no faturamento. Ressalva de leitura (regime de pagamento):
hospitais OSS são custeados por contrato de gestão com orçamento global,
não por reembolso de AIH --- o valor registrado por saída é, para eles,
produção sem consequência financeira direta; a diferença de faturamento
pode refletir o próprio regime de pagamento, a variável cujo efeito se
busca medir, e não uso de recursos ou qualidade assistencial. Toda
leitura de mortalidade nesta fase usa a
complexidade estrutural como referência de perfil, nunca a complexidade
ponderada pela mortalidade, para evitar circularidade.

A seleção de entrevistados segue seis blocos amostrais descritos na
Seção~\ref{sec:selecao}: os 5 conversores Direta$\to$OSS (obrigatórios),
desviantes positivos e negativos de eficiência persistente no suporte
comum (faixas Barcelona 3--4, portes médio e grande), pares casados de
contraste OSS vs.\ Direta e OSS vs.\ Filantrópico com estrutura parecida
e eficiência divergente, casos de maior divergência entre DEA e SFA, e
duas entrevistas curtas de validação de registro. O grupo Privado (3
hospitais) e os 18 hospitais de longa permanência ficam fora dos blocos
comparativos, pelo tamanho e pelo perfil assistencial não comparável. As
entrevistas são semiestruturadas: o roteiro-base da Seção~\ref{sec:base}
vale para todos os entrevistados dos blocos a--e, e os módulos da
Seção~\ref{sec:modulos} acrescentam perguntas específicas por perfil.
Cada pergunta traz, em itálico, o achado quantitativo que ela testa ---
o entrevistador deve conhecer esses achados, mas não deve revelá-los ao
entrevistado antes da resposta.
"""

    # ── seção 2: tabela de selecionados por bloco ──────────────────────────
    nomes_bloco = {
        "a_conversor": "Bloco a --- Conversores Direta$\\to$OSS "
                       "(obrigatórios)",
        "b_desviante_positivo": "Bloco b --- Desviantes positivos "
                                "(quartil superior persistente)",
        "c_desviante_negativo": "Bloco c --- Desviantes negativos "
                                "(quartil inferior persistente)",
        "d_par_casado": "Bloco d --- Pares casados de contraste",
        "e_divergencia_dea_sfa": "Bloco e --- Divergência DEA$\\times$SFA",
        "f_validacao_registro": "Bloco f --- Validação de registro "
                                "(entrevistas curtas)",
    }
    sec2 = ["\n\\section{Hospitais selecionados}\n\\label{sec:selecao}\n"]
    for bloco in nomes_bloco:
        sub = selecao[selecao["bloco"] == bloco]
        if sub.empty:
            continue
        sec2.append(f"\n\\subsection{{{nomes_bloco[bloco]}}}\n")
        sec2.append("\\begin{center}\\small\n"
                    "\\begin{tabular}{llllrr}\n\\toprule\n"
                    "CNES & Hospital & Município & Categoria & "
                    "DEA & SFA \\\\\n\\midrule\n")
        for _, r in sub.iterrows():
            sec2.append(f"{r['cnes']} & {_tex_escapar(str(r['nome'])[:38])} "
                        f"& {_tex_escapar(r['municipio'])} & "
                        f"{_tex_escapar(r['categoria'])} & "
                        f"{_pt(r['te_bcc_vc_mediana'], 3)} & "
                        f"{_pt(r['te_sfa_mediana'], 3)} \\\\\n")
        sec2.append("\\bottomrule\n\\end{tabular}\n\\end{center}\n")
        for _, r in sub.iterrows():
            sec2.append(f"\\noindent\\textbf{{{r['cnes']} --- "
                        f"{_tex_escapar(str(r['nome']))}}} "
                        f"({_tex_escapar(r['municipio'])}, "
                        f"{r['geografia']}; {_tex_escapar(r['porte'])}, "
                        f"faixa Barcelona {r['faixa_barcelona']}, "
                        f"complexidade estrutural "
                        f"{_pt(r['complexidade_estrutural'])}). "
                        f"{_tex_escapar(r['justificativa'])}\\par\\medskip\n")
    sec2 = "".join(sec2)

    # ── seção 3: roteiro-base comum ────────────────────────────────────────
    sec3 = ["\n\\section{Roteiro-base comum (blocos a--e)}\n"
            "\\label{sec:base}\n\n"
            "O roteiro-base cobre seis domínios e dura de 50 a 60 minutos. "
            "As perguntas são abertas; os itens entre colchetes são "
            "estímulos de aprofundamento para o entrevistador.\n"]

    dominios = [
        ("Governança e desenho institucional", [
            ("Como se organiza a direção do hospital: quem decide o quê "
             "entre a diretoria local, a mantenedora ou OSS e a Secretaria? "
             "[organograma real vs.\\ formal; conselhos; tempo de mandato "
             "da direção]",
             "a eficiência técnica maior das OSS é traço robusto da rede "
             "(DEA e SFA concordam); a hipótese é que o desenho de "
             "governança seja o canal."),
            ("Que decisões precisam de autorização externa ao hospital e "
             "quanto tempo levam, do pedido à resposta? [contratação, "
             "compra acima de um teto, abertura de leito]",
             "o regime operacional mais intenso das OSS sugere menor "
             "fricção decisória; a pergunta mede a fricção diretamente."),
            ("Com que frequência a direção examina indicadores "
             "assistenciais e o que acontece quando um indicador piora? "
             "[rotina de reunião; quem responde pelo indicador]",
             "desviantes positivos mantêm eficiência alta por 11 anos; "
             "persistência sugere rotina gerencial, não sorte."),
        ]),
        ("Autonomia de recursos humanos e compras", [
            ("Como o hospital contrata e desliga pessoal assistencial, e "
             "quanto tempo passa entre a necessidade identificada e o "
             "profissional trabalhando? [concurso vs.\\ CLT; terceirização; "
             "banco de horas]",
             "a produção das OSS é cerca de 45\\% maior a estrutura "
             "comparável; elasticidade de RH é o mecanismo candidato."),
            ("Como funcionam as compras e a manutenção de equipamentos: "
             "prazos típicos, o que mais trava? [licitação vs.\\ compra "
             "direta; estoque; equipamento parado]",
             "o faturamento real por saída não difere entre categorias; se as "
             "OSS produzem mais com faturamento igual, a diferença deve estar "
             "no uso dos insumos, não no preço."),
            ("Qual é a rotatividade das equipes médica e de enfermagem, e "
             "o que a explica? [vínculos múltiplos; plantões; salário "
             "relativo]",
             "estabilidade de equipe é explicação concorrente à gestão "
             "para a eficiência persistente dos desviantes positivos."),
        ]),
        ("Contrato de gestão e metas", [
            ("Existe contrato, convênio ou instrumento com metas "
             "quantitativas? Quais indicadores, quem apura, e o que "
             "acontece quando a meta não é cumprida? [glosa; aditivo; "
             "renegociação]",
             "o contrato de gestão é a diferença institucional formal "
             "entre OSS e administração direta; TMP $-$10,2\\% e produção "
             "$+$45\\% são os efeitos que ele teria de explicar."),
            ("As metas chegam ao cotidiano clínico? Dê um exemplo de "
             "decisão de ponta (alta, agenda cirúrgica, escala) que mudou "
             "por causa de meta. [quem traduz a meta para a equipe]",
             "o TMP menor nas OSS é evidência within (5 conversores): a "
             "pergunta busca o elo micro entre contrato e permanência."),
        ]),
        ("Relação com a Secretaria e financiamento", [
            ("Como é a interação com a Secretaria (estadual ou municipal): "
             "cobrança, apoio técnico, regulação de fila? Com que "
             "frequência? [câmaras técnicas; visitas; sistemas]",
             "categorias públicas e OSS respondem à mesma Secretaria com "
             "resultados diferentes; a pergunta separa o vínculo formal "
             "da relação praticada."),
            ("Como o dinheiro chega e o que acontece numa crise de caixa? "
             "[teto MAC; incentivos; atraso de repasse; quem socorre]",
             "o faturamento real por saída não difere entre categorias: se o "
             "financiamento é semelhante, a diferença de desempenho não "
             "é explicada por mais dinheiro."),
        ]),
        ("Gestão de leitos e fluxo do paciente", [
            ("Descreva a rotina de altas: horário, critérios, quem decide, "
             "existe reunião diária de leitos? [alta assistida; "
             "previsão de alta na admissão]",
             "TMP cerca de 10\\% menor nas OSS: a rotina de gestão de "
             "altas é o mecanismo mais direto que a entrevista pode "
             "verificar."),
            ("Quem controla a fila de internação e a ocupação do leito "
             "(NIR, regulação própria, CROSS)? Como se decide quem entra? "
             "[leito de retaguarda; internação social]",
             "o giro alto dos desviantes positivos exige controle fino "
             "de entrada e saída; a pergunta identifica o instrumento."),
            ("Que parte da cirurgia migrou para o regime ambulatorial ou "
             "hospital-dia, e o que impediu de migrar mais? [centro "
             "cirúrgico; anestesia; retorno]",
             "produção maior com TMP menor é compatível com substituição "
             "de internação por ambulatório; a pergunta testa essa "
             "composição."),
        ]),
        ("Resposta à pandemia (2020--2021)", [
            ("O que mudou em leitos, equipes e fluxo em 2020--21, e quanto "
             "da expansão foi física de fato vs.\\ apenas cadastro? "
             "[leitos de campanha; UTI improvisada; registro no CNES]",
             "as séries de 2020--21 têm extremos de ocupação de UTI e "
             "denominadores frágeis; a distinção entre leito real e leito "
             "cadastrado é decisiva para a leitura desses anos."),
            ("O que a pandemia deixou de permanente na operação do "
             "hospital? [telessaúde; protocolos; equipes]",
             "a estimação de robustez sem 2020--21 preserva os achados "
             "principais; a pergunta explora se houve mudança estrutural "
             "que os dados pós-2021 já refletem."),
        ]),
    ]
    for titulo, perguntas in dominios:
        sec3.append(f"\n\\subsection{{{titulo}}}\n"
                    "\\begin{enumerate}[itemsep=2pt]\n")
        for p, a in perguntas:
            sec3.append(_tex_pergunta(p, a))
        sec3.append("\\end{enumerate}\n")
    sec3 = "".join(sec3)

    # ── seção 4: módulos específicos ───────────────────────────────────────
    sec4 = ["\n\\section{Módulos específicos por perfil}\n"
            "\\label{sec:modulos}\n"]

    modulos = [
        ("Módulo A --- Conversores Direta$\\to$OSS (bloco a)", r"""
Reconstituir a linha do tempo da transição: quando a conversão começou a
ser discutida, quando o contrato foi assinado, quando a OSS assumiu de
fato. Atenção metodológica: no Pérola Byington e em Sorocaba a melhora
dos indicadores começou \emph{antes} da conversão formal --- é
indispensável perguntar o que já estava em curso no período anterior
(intervenção da Secretaria, troca de direção, obra, mudança de perfil),
pois a resposta separa efeito da gestão OSS de tendência pré-existente.
""", [
            ("Conte a linha do tempo da transição para OSS: primeira "
             "discussão, decisão, assinatura, assunção. O que aconteceu "
             "no hospital em cada etapa? [greves; judicialização; "
             "transição de direção]",
             "as datas de conversão da proxy (2019, 2023 e três em 2025) "
             "vêm do cadastro; a linha do tempo real pode antecedê-las e "
             "reinterpretar o estudo de eventos."),
            ("O que mudou concretamente no primeiro ano de OSS: rotinas, "
             "chefias, sistemas, escalas? O que NÃO mudou? [primeiros 90 "
             "dias; o que a OSS trouxe pronto]",
             "no estudo de eventos, o TMP cai já nos primeiros anos pós; "
             "a pergunta identifica qual prática explica a queda rápida."),
            ("Quanto da equipe assistencial e das chefias permaneceu após "
             "a conversão? [estatutários cedidos; recontratação CLT]",
             "continuidade de equipe distingue efeito de gestão de efeito "
             "de composição --- se a equipe é a mesma, a mudança é de "
             "método, não de pessoas."),
            ("Quais metas o contrato de gestão fixou no início e como "
             "elas mudaram? Alguma meta era vista como inatingível? "
             "[metas de produção vs.\\ qualidade]",
             "produção $+$45\\% e TMP $-$10,2\\% within: as metas "
             "contratuais são a explicação institucional candidata."),
            ("(Somente Pérola Byington e Sorocaba) Os indicadores já "
             "vinham melhorando antes da conversão formal. O que estava "
             "acontecendo no hospital nos 2--3 anos anteriores? [gestor "
             "interino; plano de saneamento; antecipação da OSS]",
             "a melhora pré-conversão observada nesses dois hospitais "
             "ameaça a leitura causal do estudo de eventos; a resposta "
             "decide entre antecipação, tendência ou seleção."),
        ]),
        ("Módulo B --- Desviantes positivos (bloco b)", r"""
O objetivo é extrair práticas concretas e transferíveis por trás do giro
alto e da eficiência persistente, com ceticismo ativo: pedir sempre o
exemplo, o documento, a rotina --- não aceitar declaração de princípios.
""", [
            ("O hospital está no quartil superior de eficiência da rede "
             "há 11 anos. Na sua leitura, quais três práticas explicam "
             "isso? Para cada uma: desde quando, quem implantou, o que "
             "custou? [pedir exemplos datados]",
             "a persistência no quartil superior em DEA e SFA "
             "simultaneamente afasta artefato de método; deve haver "
             "prática real por trás."),
            ("Como funciona, passo a passo, a gestão de altas num dia "
             "típico? [huddle; previsão de alta; alta aos sábados]",
             "giro alto com TMP baixo é a assinatura operacional dos "
             "desviantes positivos."),
            ("Que procedimentos o hospital faz em regime ambulatorial "
             "que vizinhos comparáveis internam? [cirurgia ambulatorial; "
             "hospital-dia; protocolos]",
             "a produção alta com leitos comparáveis sugere substituição "
             "ambulatorial; a pergunta lista os procedimentos."),
            ("Como o hospital se relaciona com a regulação de vagas: "
             "aceita tudo que a central manda? Recusa o quê, e com que "
             "argumento? [seleção de casos; perfil de demanda]",
             "eficiência alta pode ser gestão ou seleção de pacientes "
             "mais leves; a pergunta confronta a hipótese de seleção "
             "--- ler junto com a complexidade estrutural do hospital."),
        ]),
        ("Módulo C --- Desviantes negativos (bloco c)", r"""
Simétrico ao módulo B, mas centrado nas restrições percebidas. O tom não
é de auditoria: o objetivo é entender o que impede o giro, na visão de
quem opera, e confrontar depois com as restrições objetivas do painel.
""", [
            ("Quais são hoje os três maiores obstáculos para o hospital "
             "girar mais os leitos? [financiamento; RH; perfil de "
             "demanda; física do prédio]",
             "o hospital está no quartil inferior persistente de DEA e "
             "SFA; a pergunta colhe a explicação nativa antes de "
             "confrontá-la com os dados."),
            ("Descreva o paciente típico que fica internado mais tempo do "
             "que precisaria. Por que ele não sai? [internação social; "
             "retaguarda; exame que não sai]",
             "TMP alto com ocupação alta indica leito ocupado por "
             "paciente que não precisaria dele; a pergunta identifica o "
             "gargalo."),
            ("O financiamento cobre o custo do que o hospital produz? "
             "Onde aperta primeiro? [tabela SUS; folha; incentivos]",
             "o faturamento real por saída não difere entre categorias na "
             "rede; se a restrição percebida é financeira, ela precisa "
             "ser conciliada com esse achado."),
            ("Se o hospital pudesse mudar uma única regra (de RH, compra "
             "ou contrato), qual mudaria e o que aconteceria? [pergunta "
             "projetiva]",
             "a resposta revela qual margem de autonomia o gestor "
             "acredita que falta --- comparável, em espelho, com o que "
             "as OSS dizem ter."),
        ]),
        ("Módulo D --- Pares casados (bloco d)", r"""
As perguntas dos domínios 2 (RH e compras), 3 (contrato e metas) e 5
(leitos e fluxo) do roteiro-base devem ser feitas de forma espelhada e
com a mesma ordem nos dois hospitais do par, para permitir comparação
direta das respostas. Acrescentar:
""", [
            ("Num dia típico, quem decide a abertura de um leito extra, a "
             "contratação de um plantonista e a compra urgente de um "
             "insumo --- e em quanto tempo? [responder para os três "
             "casos]",
             "o par tem faixa Barcelona, porte e leitos parecidos com "
             "eficiência divergente; a velocidade decisória é a diferença "
             "de gestão mais plausível com estrutura igual."),
            ("Como é montada a escala médica do fim de semana e o que "
             "acontece com as altas de sexta a domingo? [alta no fim de "
             "semana; plantão de sexta]",
             "diferenças de TMP entre pares estruturalmente parecidos "
             "costumam se concentrar no fim de semana; pergunta "
             "espelhada nos dois hospitais do par."),
        ]),
        ("Módulo E --- Divergência DEA$\\times$SFA (bloco e)", r"""
A divergência entre os dois métodos sugere algo que os modelos não
capturam: composição de casos atípica, insumo mal medido, produção
heterogênea. A entrevista busca esse fator omitido.
""", [
            ("O que este hospital faz que hospitais parecidos não fazem "
             "--- serviços, perfis de paciente, papéis na rede que não "
             "aparecem em leitos e saídas? [ensino; referência regional; "
             "porta aberta vs.\\ referenciada]",
             "DEA e SFA discordam fortemente sobre este hospital; a "
             "explicação provável é dimensão de produto ou insumo que "
             "nenhum dos dois modelos mede."),
            ("Os números oficiais de leitos, produção e permanência do "
             "hospital refletem a operação real? Onde o registro "
             "distorce? [leitos bloqueados; produção não faturada]",
             "a divergência entre métodos também pode ser artefato de "
             "medida; a pergunta verifica a qualidade do dado antes de "
             "interpretar o resto da entrevista."),
        ]),
        ("Módulo F --- Validação de registro (bloco f, entrevistas curtas)",
         r"""
Entrevistas de 20 a 30 minutos, apenas com o responsável pelo cadastro
CNES e faturamento SIH, restritas ao registro --- não são entrevistas de
gestão e não usam o roteiro-base.
""", [
            ("(CNES 2022648) Em 2021 a ocupação de UTI calculada chega a "
             "875\\%. Quantos leitos de UTI operavam de fato em 2020--21 "
             "e quantos estavam no CNES? Houve atraso ou represamento de "
             "atualização cadastral? [leitos de campanha; UTI COVID]",
             "ocupação acima de 100\\% em escala implica denominador "
             "(leitos CNES) menor que a operação real; a resposta define "
             "como tratar as observações extremas de 2020--21."),
            ("(CNES 2097613) O registro mostra menos de 30 saídas sem "
             "COVID no biênio 2020--21 e TMP zero em 2021. O hospital "
             "fechou, mudou de papel ou parou de faturar pelo SIH nesse "
             "período? [interdição; reforma; migração de convênio]",
             "as duas observações desse CNES já são tratadas como "
             "denominador frágil e excluídas dos desfechos; a resposta "
             "confirma ou corrige esse tratamento."),
        ]),
    ]
    for titulo, intro, perguntas in modulos:
        sec4.append(f"\n\\subsection{{{titulo}}}\n{intro}\n"
                    "\\begin{enumerate}[itemsep=2pt]\n")
        for p, a in perguntas:
            sec4.append(_tex_pergunta(p, a))
        sec4.append("\\end{enumerate}\n")
    sec4 = "".join(sec4)

    # ── seção 5: logística ─────────────────────────────────────────────────
    sec5 = f"""
\\section{{Logística e esforço}}

A seleção soma {n_unicos} hospitais únicos: {n_plenas} entrevistas
plenas (roteiro-base de 50--60 minutos mais módulo específico de 20--30
minutos) e {n_curtas} entrevistas curtas de validação de registro (20--30
minutos). O teto recomendado é de 15 a 18 entrevistas. Havendo
necessidade de corte, a ordem de prioridade é: bloco a (obrigatório),
bloco f (curtas, custo baixo), blocos b e c (o contraste
positivo--negativo é o núcleo da fase), bloco d (manter ao menos um par
completo por âncora, preferindo o par Direta, que espelha a comparação
principal da estimação) e, por último, bloco e. Recomenda-se gravar com
consentimento, transcrever integralmente e codificar as respostas contra
a lista de achados deste roteiro, para que a fase qualitativa feche o
ciclo: cada mecanismo declarado nas entrevistas deve ser reexaminável no
painel.

\\end{{document}}
"""

    conteudo = preambulo + sec1 + sec2 + sec3 + sec4 + sec5
    destino = PASTA_LATEX / "roteiro_entrevistas.tex"
    destino.write_text(conteudo, encoding="utf-8")
    print(f"  [TEX] {destino}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def main():
    painel, resumo, eleg = preparar_base()

    la = bloco_a(painel, resumo)
    lb, lc = bloco_bc(eleg, resumo)
    ld, ancoras = bloco_d(eleg, resumo, lb)
    ja = ({l["cnes"] for l in la + lb + lc + ld}
          | set(ancoras) | set(CNES_VALIDACAO))
    le = bloco_e(eleg, resumo, ja)
    lf = bloco_f(painel, resumo)

    selecao = pd.DataFrame(la + lb + lc + ld + le + lf)
    selecao.to_csv(base.PASTA_TABELAS / "tab_selecao_entrevistas.csv",
                   index=False, encoding="utf-8-sig")
    print(f"\n  [TAB] tab_selecao_entrevistas.csv ({len(selecao)} linhas)")

    figuras_trajetoria(painel, lb + lc + ld)

    unicos = selecao.drop_duplicates("cnes")
    n_plenas = (unicos["tipo_entrevista"] == "plena").sum()
    n_curtas = (unicos["tipo_entrevista"] == "curta").sum()
    gerar_tex(selecao, len(unicos), n_plenas, n_curtas)

    print("\n" + "=" * 70)
    print("SUMÁRIO DA SELEÇÃO")
    print("=" * 70)
    # âncoras reaproveitadas do bloco b contam uma única entrevista
    for bloco, sub in selecao.groupby("bloco"):
        novos = sub.drop_duplicates("cnes")
        print(f"  {bloco}: {len(novos)} hospitais")
    print(f"  TOTAL DE HOSPITAIS ÚNICOS: {len(unicos)}")
    print(f"  Esforço estimado: {n_plenas} entrevistas plenas "
          f"(~80-90 min cada) + {n_curtas} curtas de validação "
          f"(~20-30 min) = {len(unicos)} entrevistas.")
    if len(unicos) > 18:
        print("  ACIMA do teto de 15-18: cortar pelo fim da ordem de "
              "prioridade (a > f > b > c > d > e).")
    else:
        print("  Dentro do teto sugerido de 15-18 entrevistas.")


if __name__ == "__main__":
    main()
