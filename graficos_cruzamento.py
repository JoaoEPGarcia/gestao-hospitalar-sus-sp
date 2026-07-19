# -*- coding: utf-8 -*-
"""
graficos_cruzamento.py
======================
Bateria de gráficos de CRUZAMENTO (aprovada em 15/07/2026) — fig_cruz_01 a
fig_cruz_08, em analises/figuras_cruzamento/. Todas as figuras carregam o selo
"PRÉVIA — painel pré-Etapa 3 (314 CNES)".

Diretriz de acessibilidade (15/07/2026, itens B1/B2): as figuras NÃO embutem
caixa "como ler" — a explicação de leitura acompanha cada figura como
parágrafo no documento que a usa (fonte: analises/figuras_cruzamento/
paragrafos_como_ler.md). Permanecem na figura apenas anotações que são
conteúdo (ex.: anotação factual da fig_cruz_02) e a nota do grupo Privado
exigida pela regra única (03/07/08). Elementos de distribuição devem ser
autoexplicativos para leigos: contagem/percentual de hospitais em vez de
densidade; rótulos mínimos com frase-pista em barras de intervalo.

Tratamento de 2020-2021 (princípio geral aprovado):
  • séries temporais (01, 02, 04) e ocupação (07): SEMPRE em duas versões
    (completa e excluindo 2020-2021);
  • agregados sem eixo de tempo (03, 05, 08): versão única; a variante sem o
    biênio é calculada por baixo dos panos e a segunda figura só é gerada se a
    diferença for MATERIAL (muda ordenação de categorias / quadrante); o
    veredito é impresso no relatório final da execução.

Tratamento do grupo PRIVADO (n=3, não interpretável — regra ÚNICA aprovada
em 15/07/2026 para os 8 conceitos): fora dos painéis comparativos (03, 07,
08, com nota na figura) ou com MARCAÇÃO VISUAL DISTINTA (cinza, marcador X,
pontilhado) onde aparece (02 não se aplica, 04 pontilhado, 05 e 06 com X
cinza e fora das linhas de referência/comparações).

COORDENADAS (Ideia 6): baixadas UMA vez da API oficial de malhas do IBGE
  URL (municípios SP): https://servicodados.ibge.gov.br/api/v3/malhas/
      estados/35?formato=application/vnd.geo+json&qualidade=minima&
      intrarregiao=municipio
  URL (contorno SP):   https://servicodados.ibge.gov.br/api/v3/malhas/
      estados/35?formato=application/vnd.geo+json&qualidade=minima
  Data de acesso: 15/07/2026. Centroide = média dos vértices do anel externo
  do polígono municipal (suficiente para posicionamento de bolhas). Cache em
  analises/aux_coordenadas_municipios_sp.csv (cod_ibge de 6 dígitos do SIH =
  7 dígitos do IBGE sem o dígito verificador).
  JITTER (municípios com mais de um hospital): determinístico — hospitais
  ordenados por CNES e dispostos em anéis concêntricos ao redor da sede
  (capacidade 8 por anel; raio 0,055° por anel), ângulo 2*pi*i/k no anel.

USO: python graficos_cruzamento.py
"""

import gzip
import json
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import analise_sih as base                      # embrulha stdout em UTF-8
import construir_painel_definitivo as cpd
import analise_exploratoria as ae               # paleta/rotulos oficiais

PASTA_CRUZ = base.PASTA_ANALISES / "figuras_cruzamento"
PASTA_F2   = base.PASTA_DADOS / "resultados_fase2"
AUX_COORD  = base.PASTA_ANALISES / "aux_coordenadas_municipios_sp.csv"

URL_MUN = ("https://servicodados.ibge.gov.br/api/v3/malhas/estados/35"
           "?formato=application/vnd.geo+json&qualidade=minima"
           "&intrarregiao=municipio")
URL_UF = ("https://servicodados.ibge.gov.br/api/v3/malhas/estados/35"
          "?formato=application/vnd.geo+json&qualidade=minima")

CATS4 = ["Direta", "OSS", "Público Municipal", "Filantrópico"]  # comparáveis
SWITCHERS = {2081695: ("Conj. Hosp. Sorocaba", 2019),
             2078287: ("Pérola Byington", 2023),
             2082225: ("Kátia de Souza R. — Taipas", 2025),
             2091755: ("Vila Penteado", 2025),
             2750511: ("Pres. Prudente", 2025)}
IND4 = ["mort_all", "tmp", "custo_real", "pct_alta_complex"]

SELO = "PRÉVIA — painel pré-Etapa 3 (314 CNES)"
NOTA_PRIV = ("Privado (n=3): não interpretável como categoria; "
             "fora desta comparação.")
VEREDITOS = []          # relatório final: quem ganhou versão sem 2020-2021


def _selo(fig):
    fig.text(.995, .995, SELO, ha="right", va="top", fontsize=8,
             color="#8a2620", style="italic")


def _nota_privado(fig):
    """Nota exigida pela regra única do Privado (fica NA figura em 03/07/08)."""
    fig.text(.008, .012, NOTA_PRIV, ha="left", va="bottom",
             fontsize=8.2, color="#52514e", style="italic")


def _salvar(fig, nome):
    fig.savefig(PASTA_CRUZ / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [FIG] {nome}")


def _sufixo(sem_pand):
    return "_sem_pandemia" if sem_pand else ""


def carregar():
    df = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
    df["cnes"] = pd.to_numeric(df["cnes"], errors="raise").astype("int64")
    df["ano"] = df["ano"].astype(int)
    df["custo_real"] = df["custo_saida"] * df["ano"].map(ae._fatores_ipca_2025())
    dea = pd.read_csv(PASTA_F2 / "dea" / "dea_escores_principal.csv")
    sfa = pd.read_csv(PASTA_F2 / "sfa" / "sfa_eficiencias.csv")
    sfa = sfa.merge(df[["cnes", "ano", "modelo_gestao_proxy"]],
                    on=["cnes", "ano"], how="left")
    return df, dea, sfa


# ══════════════════════════════════════════════════════════════════════════════
# 01 — TRAJETÓRIA DOS 5 SWITCHERS (pequenos múltiplos)
# ══════════════════════════════════════════════════════════════════════════════

def fig01(df, sem_pand):
    d = df[~df["ano"].isin([2020, 2021])] if sem_pand else df
    ordem = sorted(SWITCHERS, key=lambda c: (SWITCHERS[c][1], c))
    fig, axes = plt.subplots(5, 4, figsize=(15, 13.5), sharex=True)
    for i, cnes in enumerate(ordem):
        nome, ano_conv = SWITCHERS[cnes]
        s = d[d["cnes"] == cnes].sort_values("ano")
        for j, c in enumerate(IND4):
            ax = axes[i, j]
            if not sem_pand:
                ae._banda_covid(ax)
            ax.plot(s["ano"], s[c], marker="o", ms=3.5, lw=1.6,
                    color=ae.COR_SERIE)
            ax.axvline(ano_conv - .5, color="#8a2620", lw=1.2, ls="dashed")
            lo, hi = df[df["cnes"].isin(ordem)][c].min(), \
                df[df["cnes"].isin(ordem)][c].max()
            folga = .06 * (hi - lo)
            ax.set_ylim(lo - folga, hi + folga)
            if i == 0:
                ax.set_title(ae.ROT[c], fontsize=10)
            if j == 0:
                ax.set_ylabel(f"{nome}\n(OSS em {ano_conv})", fontsize=8.6)
            ax.tick_params(labelsize=8)
    for j in range(4):
        axes[-1, j].set_xlabel("Ano", fontsize=9)
    extra = (" — anos de 2020 e 2021 excluídos"
             if sem_pand else " (faixa cinza: 2020 e 2021)")
    fig.suptitle("Trajetória dos 5 conversores Direta→OSS: a melhora coincide "
                 "com a conversão? A complexidade atendida mudou junto?"
                 + extra, fontsize=13)
    fig.tight_layout(rect=[0, .01, 1, .965])
    _selo(fig)
    _salvar(fig, f"fig_cruz_01_trajetoria_switchers{_sufixo(sem_pand)}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 02 — "EFEITO SOROCABA": MORTALIDADE OSS COM/SEM OS 5 SWITCHERS
# ══════════════════════════════════════════════════════════════════════════════

def fig02(df, sem_pand):
    d = df[~df["ano"].isin([2020, 2021])] if sem_pand else df
    sw = set(SWITCHERS)
    oss = d[d["modelo_gestao_proxy"] == "OSS"]
    series = {
        "OSS (com os 5 conversores)":
            oss.groupby("ano")["mort_all"].median(),
        "OSS sem os 5 conversores":
            oss[~oss["cnes"].isin(sw)].groupby("ano")["mort_all"].median(),
        "Direta (referência)":
            d[d["modelo_gestao_proxy"] == "Direta"]
            .groupby("ano")["mort_all"].median(),
    }
    estilos = {
        "OSS (com os 5 conversores)": dict(color=ae.CORES_CAT["OSS"],
                                           ls="solid", marker="s", lw=2),
        "OSS sem os 5 conversores": dict(color=ae.CORES_CAT["OSS"],
                                         ls="dashed", marker="s", lw=1.6),
        "Direta (referência)": dict(color=ae.CORES_CAT["Direta"],
                                    ls="solid", marker="o", lw=2),
    }
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    if not sem_pand:
        ae._banda_covid(ax)
    for rot, s in series.items():
        ax.plot(s.index, s.values, ms=4.5, **estilos[rot], label=rot)
    m = {rot: s.median() for rot, s in series.items()}
    # Coeficientes dos MODELOS (CRE/Mundlak) — fonte: tabR_frente1_variantes
    fr = pd.read_csv(PASTA_F2 / "tabelas" / "tabR_frente1_variantes.csv")
    fr = fr[fr["modelo"] == "mortalidade"].set_index("variante")
    b_p, lo_p, hi_p = fr.loc["principal", ["coef_oss", "ic_lo", "ic_hi"]]
    b_s, lo_s, hi_s = fr.loc["sem_switchers", ["coef_oss", "ic_lo", "ic_hi"]]
    ax.text(.02, .97,
            "Nas MEDIANAS simples deste gráfico a OSS nunca esteve abaixo\n"
            f"da Direta (medianas 2015–2025: OSS "
            f"{m['OSS (com os 5 conversores)']:.4f}; OSS sem conversores "
            f"{m['OSS sem os 5 conversores']:.4f};\n"
            f"Direta {m['Direta (referência)']:.4f}).\n"
            "É nos MODELOS que o sinal inverte: o efeito OSS de mortalidade\n"
            f"(logito) vai de {b_p:.3f} (IC95% {lo_p:.2f} a {hi_p:.2f}) para "
            f"{b_s:+.3f} (IC {lo_s:.2f} a {hi_s:.2f})\n"
            "sem os 5 conversores — a 'vantagem' de mortalidade da OSS é\n"
            "um fenômeno da trajetória de quem converteu, não da rede OSS.",
            transform=ax.transAxes, va="top", fontsize=8.8,
            bbox={"facecolor": "#fff7e6", "edgecolor": "#e0a800", "pad": 5})
    ax.set_xlabel("Ano")
    ax.set_ylabel("Mortalidade geral (mediana da categoria)")
    extra = (" — anos de 2020 e 2021 excluídos"
             if sem_pand else " (faixa cinza: 2020 e 2021)")
    ax.set_title("Mortalidade mediana: quanto da vantagem da OSS vem dos 5 "
                 "hospitais que trocaram de gestão?" + extra, fontsize=12)
    ax.legend(fontsize=9.5, loc="lower left")
    fig.tight_layout(rect=[0, .01, 1, 1])
    _selo(fig)
    _salvar(fig, f"fig_cruz_02_efeito_switchers_mortalidade"
                 f"{_sufixo(sem_pand)}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 03 — HEATMAP-BOLHA: CATEGORIA × FAIXA × INDICADOR × N
# ══════════════════════════════════════════════════════════════════════════════

def _celulas_03(d, indicador):
    g = (d[d["modelo_gestao_proxy"].isin(CATS4)]
         .groupby(["modelo_gestao_proxy", "faixa_barcelona"])[indicador]
         .agg(["median", "size"]).reset_index())
    return g


def _ordenacao_03(g):
    """Ordenação das categorias por faixa (para o teste de materialidade)."""
    out = {}
    for fx, sub in g.groupby("faixa_barcelona"):
        out[fx] = tuple(sub.sort_values("median")["modelo_gestao_proxy"])
    return out


def fig03(df, indicador, letra):
    g = _celulas_03(df, indicador)
    g_sem = _celulas_03(df[~df["ano"].isin([2020, 2021])], indicador)
    material = _ordenacao_03(g) != _ordenacao_03(g_sem)
    VEREDITOS.append(
        (f"fig_cruz_03{letra} ({indicador})",
         "SEGUNDA VERSÃO GERADA (ordenação de categorias muda sem 2020-2021)"
         if material else
         "verificado: exclusão de 2020-2021 não altera a ordenação — "
         "sem segunda figura"))

    versoes = [(g, False)] + ([(g_sem, True)] if material else [])
    for gg, sem_pand in versoes:
        faixas = sorted(gg["faixa_barcelona"].unique())
        fig, ax = plt.subplots(figsize=(9.5, 5.8))
        x_de = {f: i for i, f in enumerate(faixas)}
        y_de = {c: i for i, c in enumerate(CATS4[::-1])}
        smax = gg["size"].max()
        sc = ax.scatter(
            [x_de[f] for f in gg["faixa_barcelona"]],
            [y_de[c] for c in gg["modelo_gestao_proxy"]],
            s=3200 * gg["size"] / smax + 60, c=gg["median"],
            cmap="Blues", edgecolor="#52514e", lw=.6, zorder=3)
        for _, r in gg.iterrows():
            ax.annotate(f"n={int(r['size'])}",
                        (x_de[r["faixa_barcelona"]],
                         y_de[r["modelo_gestao_proxy"]]),
                        textcoords="offset points", xytext=(0, -26),
                        ha="center", fontsize=8, color="#52514e")
        cb = fig.colorbar(sc, ax=ax, shrink=.85)
        cb.set_label(f"Mediana — {ae.ROT[indicador]}", fontsize=9.5)
        ax.set_xticks(range(len(faixas)))
        ax.set_xticklabels([f"Faixa {f}" for f in faixas], fontsize=10)
        ax.set_yticks(range(len(CATS4)))
        ax.set_yticklabels(CATS4[::-1], fontsize=10)
        ax.set_xlim(-.6, len(faixas) - .4)
        ax.set_ylim(-.7, len(CATS4) - .3)
        ax.set_xlabel("Faixa de complexidade Barcelona", fontsize=10)
        extra = " — anos de 2020 e 2021 excluídos" if sem_pand else ""
        ax.set_title(f"{ae.ROT[indicador]} por categoria × complexidade: "
                     f"valor (cor) e confiabilidade (tamanho = nº de "
                     f"hospital-ano){extra}", fontsize=11.5)
        fig.tight_layout(rect=[0, .035, 1, 1])
        _selo(fig)
        _nota_privado(fig)
        _salvar(fig, f"fig_cruz_03{letra}_heatmap_{indicador}"
                     f"{_sufixo(sem_pand)}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 04 — EFICIÊNCIA TÉCNICA (DEA E SFA) POR CATEGORIA AO LONGO DO TEMPO
# ══════════════════════════════════════════════════════════════════════════════

def fig04(dea, sfa, sem_pand):
    d1 = dea[~dea["ano"].isin([2020, 2021])] if sem_pand else dea
    d2 = sfa[~sfa["ano"].isin([2020, 2021])] if sem_pand else sfa
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), sharex=True)
    fontes = [(axes[0], d1, "categoria", "te_bcc_vc",
               "Eficiência DEA-BCC (corrigida de viés)"),
              (axes[1], d2, "modelo_gestao_proxy", "te_sfa",
               "Eficiência técnica SFA (BC95)")]
    for ax, d, col, met, titulo in fontes:
        if not sem_pand:
            ae._banda_covid(ax)
        med = d.groupby(["ano", col])[met].median()
        for cat in ae.CATEGORIAS:
            if cat not in med.index.get_level_values(1):
                continue
            s = med.xs(cat, level=1)
            estilo = ({"lw": 1, "ls": "dotted"} if cat == "Privado"
                      else {"lw": 1.8, "ls": "solid"})
            ax.plot(s.index, s.values, marker=ae.MARCADORES[cat], ms=4,
                    color=ae.CORES_CAT[cat], label=cat, **estilo)
        ax.set_title(titulo, fontsize=11)
        ax.set_xlabel("Ano")
        ax.set_ylabel("Escore de eficiência (mediana)")
        ax.tick_params(axis="x", rotation=45)
    axes[0].legend(fontsize=8.6, title="Privado: n=3, pontilhado",
                   title_fontsize=8.4)
    extra = (" — anos de 2020 e 2021 excluídos"
             if sem_pand else " (faixa cinza: 2020 e 2021)")
    fig.suptitle("Eficiência técnica por categoria administrativa ao longo "
                 "do tempo (dois métodos)" + extra, fontsize=12.5)
    fig.tight_layout(rect=[0, .01, 1, .94])
    _selo(fig)
    _salvar(fig, f"fig_cruz_04_eficiencia_tempo{_sufixo(sem_pand)}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 05 — DISPERSÃO FATURAMENTO × MORTALIDADE (QUADRANTES)
# ══════════════════════════════════════════════════════════════════════════════

def _quadrantes_05(d):
    """Quadrante do ponto mediano de cada categoria comparável."""
    ref = d[d["modelo_gestao_proxy"].isin(CATS4)]
    mx, my = ref["custo_real"].median(), ref["mort_all"].median()
    out = {}
    for cat in CATS4:
        s = ref[ref["modelo_gestao_proxy"] == cat]
        out[cat] = (s["custo_real"].median() > mx, s["mort_all"].median() > my)
    return out


def fig05(df):
    material = _quadrantes_05(df) != _quadrantes_05(
        df[~df["ano"].isin([2020, 2021])])
    VEREDITOS.append(
        ("fig_cruz_05 (dispersão)",
         "SEGUNDA VERSÃO GERADA (ponto mediano de categoria muda de "
         "quadrante sem 2020-2021)" if material else
         "verificado: exclusão de 2020-2021 não muda o quadrante do ponto "
         "mediano de nenhuma categoria — sem segunda figura"))
    versoes = [(df, False)] + (
        [(df[~df["ano"].isin([2020, 2021])], True)] if material else [])
    for d, sem_pand in versoes:
        ref = d[d["modelo_gestao_proxy"].isin(CATS4)]
        mx, my = ref["custo_real"].median(), ref["mort_all"].median()
        fig, ax = plt.subplots(figsize=(10.5, 7))
        for cat in CATS4:
            s = d[d["modelo_gestao_proxy"] == cat]
            ax.scatter(s["custo_real"], s["mort_all"],
                       s=np.sqrt(s["qtde_sem_covid"].clip(lower=1)) * .9,
                       color=ae.CORES_CAT[cat], alpha=.38, lw=0, label=cat)
        priv = d[d["modelo_gestao_proxy"] == "Privado"]
        ax.scatter(priv["custo_real"], priv["mort_all"],
                   s=np.sqrt(priv["qtde_sem_covid"].clip(lower=1)) * .9,
                   color="#898781", marker="X", alpha=.85, lw=.5,
                   edgecolor="#52514e",
                   label="Privado (n=3, não comparável)")
        ax.axvline(mx, color="#52514e", lw=1, ls="dashed")
        ax.axhline(my, color="#52514e", lw=1, ls="dashed")
        ax.set_xscale("log")
        for (fx, fy, txt) in [
                (.02, .96, "faturamento abaixo da mediana,\n"
                           "mortalidade acima da mediana"),
                (.98, .96, "faturamento acima da mediana,\n"
                           "mortalidade acima da mediana"),
                (.02, .05, "faturamento abaixo da mediana,\n"
                           "mortalidade abaixo da mediana"),
                (.98, .05, "faturamento acima da mediana,\n"
                           "mortalidade abaixo da mediana")]:
            ax.text(fx, fy, txt, transform=ax.transAxes, fontsize=8,
                    color="#898781", ha="left" if fx < .5 else "right",
                    va="top" if fy > .5 else "bottom", style="italic")
        ax.set_xlabel("Faturamento real por saída (R$ de 2025, escala log)")
        ax.set_ylabel("Mortalidade geral")
        extra = " — anos de 2020 e 2021 excluídos" if sem_pand else ""
        ax.set_title("Cada ponto é um hospital-ano: faturamento × mortalidade "
                     "(tamanho = volume de saídas)" + extra, fontsize=12)
        ax.legend(fontsize=9, loc="center left", bbox_to_anchor=(1.01, .5))
        fig.tight_layout(rect=[0, .01, 1, 1])
        _selo(fig)
        _salvar(fig, f"fig_cruz_05_dispersao_faturamento_mortalidade"
                     f"{_sufixo(sem_pand)}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 06 — MAPA DE SP POR CATEGORIA
# ══════════════════════════════════════════════════════════════════════════════

def _http_geojson(url):
    """GET com suporte a resposta gzip (a API de malhas do IBGE comprime)."""
    req = urllib.request.Request(url, headers={"Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def _baixar_coordenadas():
    if AUX_COORD.exists():
        print(f"  [CACHE] {AUX_COORD.name} já existe — download não repetido.")
        return pd.read_csv(AUX_COORD, encoding="utf-8-sig")
    print("  [IBGE] Baixando malha municipal de SP (API de malhas v3, "
          "qualidade mínima) — acesso em 15/07/2026 ...")
    gj = _http_geojson(URL_MUN)
    linhas = []
    for feat in gj["features"]:
        cod7 = str(feat.get("properties", {}).get("codarea", ""))
        geom = feat["geometry"]
        aneis = ([geom["coordinates"][0]] if geom["type"] == "Polygon"
                 else [p[0] for p in geom["coordinates"]])
        pts = np.array([pt for anel in aneis for pt in anel], dtype=float)
        lon, lat = pts[:, 0].mean(), pts[:, 1].mean()
        linhas.append({"cod_ibge7": cod7, "cod_ibge6": cod7[:6],
                       "lon": round(lon, 5), "lat": round(lat, 5)})
    t = pd.DataFrame(linhas)
    t.to_csv(AUX_COORD, index=False, encoding="utf-8-sig")
    print(f"  [IBGE] {len(t)} municípios → {AUX_COORD.name} "
          f"(fonte: {URL_MUN})")
    return t


def _contorno_sp(ax):
    try:
        gj = _http_geojson(URL_UF)
        for feat in gj["features"]:
            geom = feat["geometry"]
            polys = ([geom["coordinates"]] if geom["type"] == "Polygon"
                     else geom["coordinates"])
            for poly in polys:
                anel = np.array(poly[0], dtype=float)
                ax.plot(anel[:, 0], anel[:, 1], color="#c3c2b7", lw=.9,
                        zorder=1)
    except Exception as e:
        print(f"  [AVISO] contorno do estado indisponível ({e}) — mapa sai "
              f"só com os pontos.")


def _jitter(k):
    """Deslocamentos determinísticos: anéis concêntricos (8 por anel,
    raio 0,055° por anel), ângulo 2*pi*i/capacidade. k = nº de hospitais."""
    des = []
    i = 0
    anel = 1
    while len(des) < k:
        cap = 8 * anel
        for j in range(cap):
            if len(des) >= k:
                break
            th = 2 * np.pi * j / cap
            des.append((0.055 * anel * np.cos(th),
                        0.055 * anel * np.sin(th)))
        anel += 1
        i += 1
    if k == 1:
        return [(0.0, 0.0)]
    return des


def fig06(df):
    coords = _baixar_coordenadas()
    coords["cod_ibge6"] = coords["cod_ibge6"].astype(str)
    ultimo = (df.sort_values("ano").groupby("cnes")
              .agg(categoria=("modelo_gestao_proxy", "last"),
                   cplx=("complexidade_estrutural", "last"),
                   cod_ibge=("cod_ibge", "last")).reset_index())
    ultimo["cod6"] = (pd.to_numeric(ultimo["cod_ibge"], errors="coerce")
                      .astype("Int64").astype(str))
    m = ultimo.merge(coords, left_on="cod6", right_on="cod_ibge6", how="left")
    sem = m["lon"].isna().sum()
    print(f"  [MAPA] {len(m)} CNES; sem coordenada: {sem}")

    m = m.dropna(subset=["lon"]).sort_values(["cod6", "cnes"])
    des = []
    for _, grupo in m.groupby("cod6", sort=False):
        des += _jitter(len(grupo))
    m["lon_j"] = m["lon"] + [d[0] for d in des]
    m["lat_j"] = m["lat"] + [d[1] for d in des]

    fig, ax = plt.subplots(figsize=(11.5, 10))
    _contorno_sp(ax)
    for cat in CATS4:
        s = m[m["categoria"] == cat]
        ax.scatter(s["lon_j"], s["lat_j"], s=s["cplx"] * .55 + 12,
                   color=ae.CORES_CAT[cat], alpha=.75, lw=.4,
                   edgecolor="white", label=f"{cat} ({len(s)})", zorder=3)
    priv = m[m["categoria"] == "Privado"]
    ax.scatter(priv["lon_j"], priv["lat_j"], s=priv["cplx"] * .55 + 12,
               color="#898781", marker="X", lw=.6, edgecolor="#52514e",
               label=f"Privado ({len(priv)}; n=3, não comparável)", zorder=4)
    ax.set_aspect("equal")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Os 314 hospitais do painel no mapa de SP — cor = categoria "
                 "administrativa, tamanho = complexidade estrutural "
                 "(Barcelona)", fontsize=12.5)
    ax.legend(fontsize=9, loc="lower left")
    fig.tight_layout(rect=[0, .01, 1, 1])
    _selo(fig)
    _salvar(fig, "fig_cruz_06_mapa_categorias.png")


# ══════════════════════════════════════════════════════════════════════════════
# 07 — OCUPAÇÃO POR CATEGORIA × FAIXA AO LONGO DO TEMPO
# ══════════════════════════════════════════════════════════════════════════════

def fig07(df, metrica, letra, sem_pand):
    d = df[~df["ano"].isin([2020, 2021])] if sem_pand else df
    d = d[d["modelo_gestao_proxy"].isin(CATS4)]
    faixas = sorted(df["faixa_barcelona"].unique())
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True, sharey=True)
    for ax, cat in zip(axes.ravel(), CATS4):
        if not sem_pand:
            ae._banda_covid(ax)
        s_cat = d[d["modelo_gestao_proxy"] == cat]
        med = s_cat.groupby(["ano", "faixa_barcelona"])[metrica].median()
        for i, fx in enumerate(faixas):
            if fx not in med.index.get_level_values(1):
                continue
            s = med.xs(fx, level=1)
            ax.plot(s.index, s.values, marker="o", ms=3.4, lw=1.5,
                    color=ae.RAMPA_5[i], label=f"Faixa {fx}")
        ax.set_title(f"{cat} ({s_cat['cnes'].nunique()} CNES)", fontsize=11)
        ax.tick_params(axis="x", rotation=45, labelsize=9)
    axes[0, 0].legend(fontsize=8.4, ncol=2, title="Complexidade Barcelona",
                      title_fontsize=8.4)
    for ax in axes[-1, :]:
        ax.set_xlabel("Ano")
    for ax in axes[:, 0]:
        ax.set_ylabel(ae.ROT[metrica])
    extra = (" — anos de 2020 e 2021 excluídos"
             if sem_pand else " (faixa cinza: 2020 e 2021)")
    fig.suptitle(f"{ae.ROT[metrica]}: mediana anual por categoria e faixa de "
                 f"complexidade{extra}", fontsize=13)
    fig.tight_layout(rect=[0, .035, 1, .95])
    _selo(fig)
    _nota_privado(fig)
    _salvar(fig, f"fig_cruz_07{letra}_ocupacao_{metrica}"
                 f"{_sufixo(sem_pand)}.png")


# ══════════════════════════════════════════════════════════════════════════════
# 08 — RADAR POR CATEGORIA (NORMALIZADO, COM RESSALVA)
# ══════════════════════════════════════════════════════════════════════════════

EIXOS_08 = [("mort_all", "Mortalidade"), ("tmp", "TMP"),
            ("custo_real", "Faturamento real"),
            ("ocupacao_internacao", "Ocupação internação"),
            ("te_bcc_vc", "Eficiência DEA")]


def _medianas_08(df, dea):
    d = df.merge(dea[["cnes", "ano", "te_bcc_vc"]], on=["cnes", "ano"],
                 how="left")
    d = d[d["modelo_gestao_proxy"].isin(CATS4)]
    return d.groupby("modelo_gestao_proxy")[[c for c, _ in EIXOS_08]].median()


def _norm_08(med):
    return (med - med.min()) / (med.max() - med.min()) * 100


def fig08(df, dea):
    med = _medianas_08(df, dea)
    med_sem = _medianas_08(df[~df["ano"].isin([2020, 2021])], dea)
    rank = lambda m: {c: tuple(m[c].sort_values().index) for c in m.columns}
    material = rank(med) != rank(med_sem)
    VEREDITOS.append(
        ("fig_cruz_08 (radar)",
         "SEGUNDA VERSÃO GERADA (ordenação por eixo muda sem 2020-2021)"
         if material else
         "verificado: exclusão de 2020-2021 não altera a ordenação das "
         "categorias em nenhum eixo — sem segunda figura"))
    versoes = [(med, False)] + ([(med_sem, True)] if material else [])
    for m, sem_pand in versoes:
        norm = _norm_08(m)
        ang = np.linspace(0, 2 * np.pi, len(EIXOS_08), endpoint=False)
        ang_f = np.concatenate([ang, ang[:1]])
        fig, ax = plt.subplots(figsize=(8.6, 8.2),
                               subplot_kw={"polar": True})
        for cat in CATS4:
            vals = norm.loc[cat].to_numpy()
            vals = np.concatenate([vals, vals[:1]])
            ax.plot(ang_f, vals, color=ae.CORES_CAT[cat], lw=1.8,
                    marker=ae.MARCADORES[cat], ms=4, label=cat)
            ax.fill(ang_f, vals, color=ae.CORES_CAT[cat], alpha=.06)
        ax.set_xticks(ang)
        ax.set_xticklabels([r for _, r in EIXOS_08], fontsize=9.5)
        ax.set_yticks([0, 50, 100])
        ax.set_yticklabels(["mín. entre categorias", "50", "máx."],
                           fontsize=7.5, color="#898781")
        extra = " — anos de 2020 e 2021 excluídos" if sem_pand else ""
        ax.set_title("Perfil relativo das categorias em 5 indicadores "
                     "(medianas normalizadas 0–100 entre as 4 categorias)"
                     + extra, fontsize=11.5, pad=22)
        ax.legend(fontsize=9, loc="lower right", bbox_to_anchor=(1.18, -.06))
        fig.tight_layout(rect=[0, .035, 1, 1])
        _selo(fig)
        _nota_privado(fig)
        _salvar(fig, f"fig_cruz_08_radar_categorias{_sufixo(sem_pand)}.png")


def main():
    print("=" * 78)
    print("BATERIA DE GRÁFICOS DE CRUZAMENTO — fig_cruz_01 a fig_cruz_08")
    print("=" * 78)
    base.configurar_diretorios()
    PASTA_CRUZ.mkdir(parents=True, exist_ok=True)
    df, dea, sfa = carregar()
    print(f"[CARGA] painel {df['cnes'].nunique()} CNES / {len(df)} linhas | "
          f"DEA {len(dea)} | SFA {len(sfa)}")

    for sem in (False, True):
        fig01(df, sem)
        fig02(df, sem)
        fig04(dea, sfa, sem)
        fig07(df, "ocupacao_internacao", "a", sem)
        fig07(df, "ocupacao_uti", "b", sem)
    VEREDITOS.append(("fig_cruz_01/02/04/07",
                      "duas versões SEMPRE (séries temporais/ocupação — "
                      "princípio geral)"))
    for ind, letra in [("mort_all", "a"), ("tmp", "b"), ("custo_real", "c")]:
        fig03(df, ind, letra)
    fig05(df)
    fig06(df)
    fig08(df, dea)

    print("\n" + "=" * 78)
    print("RELATÓRIO COM/SEM 2020-2021 (materialidade):")
    for nome, veredito in VEREDITOS:
        print(f"  • {nome}: {veredito}")
    n = len(list(PASTA_CRUZ.glob("fig_cruz_*.png")))
    print(f"\nTOTAL: {n} PNGs em {PASTA_CRUZ}")
    print("=" * 78)


if __name__ == "__main__":
    main()
