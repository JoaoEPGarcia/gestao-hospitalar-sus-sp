# -*- coding: utf-8 -*-
"""
ETAPA 3b — Diagnóstico da ocupação de internação e variantes de denominador.

ESTE SCRIPT NÃO ESCOLHE NENHUMA VARIANTE. Ele quantifica o problema e deixa
as três alternativas lado a lado, como colunas paralelas, para ratificação
da equipe. Escolher aqui seria tomar no lugar da equipe uma decisão que muda
a definição de um indicador do documento.

O problema (identificado por João, 27/07/2026)
----------------------------------------------
ocupacao_internacao = 100 × diarias_internacao / (leitos_sus × 365), onde
leitos_sus é o leito de internação declarado ao SUS no CNES.

Ocupação acima de 100% significa mais diárias do que leito-dia disponível
segundo a capacidade CADASTRADA, e ocorre em 15,5% das observações, de forma
fortemente diferencial: 29,3% no OSS contra 3,9% na Direta.

ATENÇÃO — LEITURA REVISADA (27/07/2026, duas vezes no mesmo dia). Este
script foi escrito sob a hipótese de que leitos_sus estaria sub-registrado
frente ao leito efetivamente operado, na mesma classe de erro corrigida na
ETAPA 1 para a UTI. ESSA HIPÓTESE NÃO ESTÁ ESTABELECIDA, e tampouco foi
refutada: ficou NÃO TESTADA.

Todos os campos de leito disponíveis — leitos_sus, leitos_internacao,
total_leitos e a contagem do arquivo de classificação Barcelona — são de
linhagem CNES. A concordância entre eles não é validação externa: um CNES
que sub-registra leito SUS sub-registra em todos ao mesmo tempo. O teste
decisivo está no Privado, onde leitos_sus é 6,7% de total_leitos e a coluna
Barcelona ainda assim dá razão 1,000 contra leitos_sus.

Não se sabe se o excesso é sobrecarga assistencial real ou sub-registro
cadastral, e estes dados não conseguem distinguir. A única evidência que não
depende do CNES é o padrão episódico medido no fim deste script, que
favorece a leitura de sobrecarga sem estabelecê-la.

Consequência: o indicador fica FORA da estimação na ETAPA 4 e sai como
descritiva tarjada. Ver RESTRICOES_SEGMENTACAO.md (R1) e PENDENCIAS.md §9,
onde a pergunta está com o Alberto.

As três variantes
-----------------
  V1 censura em 100      ocup_int_censura100
     mantém a observação, trata >100 como 100. Preserva o n, mas
     achata a variação justamente onde o problema é maior.

  V2 missing acima de 100  ocup_int_missing100
     trata >100 como não-observado, na mesma lógica da ETAPA 1. Custa
     observações, e as perde de forma diferencial por categoria — o que
     transporta o viés do valor para a amostra.

  V3 denominador leitos_internacao  ocup_int_leitos_int
     100 × diarias_internacao / (leitos_internacao × 365). É o análogo
     exato do que a UTI já faz (uti_total ⊇ uti_sus; leitos_internacao ⊇
     leitos_sus). MUDA A DEFINIÇÃO DO INDICADOR: passa a medir ocupação da
     capacidade instalada total, não da capacidade contratada ao SUS. E não
     escapa do problema de linhagem: leitos_internacao vem do mesmo CNES.

NENHUMA DEVE SER APLICADA antes da resposta do Alberto. As três pressupõem
que o excesso é erro a corrigir; se for sobrecarga real, censurar em 100 ou
marcar como missing apagaria justamente o achado. Ver
RESTRICOES_SEGMENTACAO.md, restrição R1.

Saídas
------
  analises/tabelas/tabSEG_05b_ocupacao_internacao_acima_100.csv
  analises/tabelas/tabSEG_05c_variantes_ocupacao_internacao.csv
  analises/tabelas/tabSEG_05d_composicao_faixa_e3.csv
  analises/figuras_segmentacao/figSEG_02b_ocupacao_internacao_acima_100.png
  analises/painel_segmentado_variantes.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
PAINEL_IN = RAIZ / "analises" / "painel_segmentado.csv"
PAINEL_OUT = RAIZ / "analises" / "painel_segmentado_variantes.csv"
PASTA_TAB = RAIZ / "analises" / "tabelas"
PASTA_FIG = RAIZ / "analises" / "figuras_segmentacao"

DIAS_ANO = 365
PISO_CNES = 10
TARJA = "[n<10]"

CATEGORIAS = ["Direta", "OSS", "Público Municipal", "Filantrópico", "Privado"]
ESTRATOS = ["E1", "E2", "E3"]
ROTULOS = {"E1": "sem_uti_sus", "E2": "uti_baixa_complex", "E3": "uti_alta_complex"}

VARIANTES = {
    "ocupacao_internacao":  "V0 original (leitos_sus)",
    "ocup_int_censura100":  "V1 censura em 100",
    "ocup_int_missing100":  "V2 missing acima de 100",
    "ocup_int_leitos_int":  "V3 denominador leitos_internacao",
}

CORES_CAT = {
    "Direta":            "#0d366b",
    "OSS":               "#0f9b8e",
    "Público Municipal": "#5598e7",
    "Filantrópico":      "#6a51c7",
    "Privado":           "#898781",
}
CORES_VAR = {"ocupacao_internacao": "#c3c2b7", "ocup_int_censura100": "#86b6ef",
             "ocup_int_leitos_int": "#1c5cab", "ocup_int_missing100": "#5598e7"}
COR_EVENTO = "#52514e"
COR_GRADE  = "#e1e0d9"
COR_EIXO   = "#c3c2b7"
COR_MUTED  = "#898781"

plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": COR_EIXO, "axes.labelcolor": "#0b0b0b",
    "axes.grid": True, "grid.color": COR_GRADE, "grid.linewidth": .6,
    "xtick.color": COR_MUTED, "ytick.color": COR_MUTED,
    "font.size": 11.5, "axes.titlesize": 11.5, "figure.titlesize": 11,
})


def _parar(motivo: str) -> None:
    print("\n" + "!" * 78)
    print("PARAR E REPORTAR")
    print(motivo)
    print("Nenhum arquivo foi escrito.")
    print("!" * 78)
    sys.exit(1)


# ---------------------------------------------------------------------------
# LEITURA E VERIFICAÇÃO DA FÓRMULA
# ---------------------------------------------------------------------------
print("=" * 78)
print("ETAPA 3b — ocupação de internação: diagnóstico e variantes")
print("=" * 78)

if not PAINEL_IN.exists():
    _parar(f"{PAINEL_IN.name} não existe. Rodar antes a ETAPA 2.")

df = pd.read_csv(PAINEL_IN)
N_IN, COLS_IN = len(df), list(df.columns)
print(f"\nlido: {PAINEL_IN.relative_to(RAIZ)}")
print(f"  {len(df):,} observações | {df['cnes'].nunique():,} CNES")

print("\n" + "-" * 78)
print("VERIFICAÇÃO — fórmula da ocupação de internação")
print("-" * 78)
recalc = 100 * df["diarias_internacao"] / (df["leitos_sus"] * DIAS_ANO)
dif = (recalc - df["ocupacao_internacao"]).abs()
adere = dif <= 0.05
print(f"aderência a 100*diarias_internacao/(leitos_sus*365): "
      f"{100 * adere.mean():.2f}%")
print(f"maior desvio absoluto: {dif.max():.4f} pp")
if adere.mean() < 0.99:
    _parar("A identidade da ocupação de internação não se sustenta.")

print(f"\nobs com leitos_sus == 0 ............... {int((df['leitos_sus'] == 0).sum())}")
print(f"obs com leitos_internacao == 0 ....... "
      f"{int((df['leitos_internacao'] == 0).sum())}")
# Se leitos_internacao não contivesse leitos_sus, V3 não seria o análogo da
# UTI que se supõe — seria outra coisa.
n_incoerente = int((df["leitos_internacao"] < df["leitos_sus"]).sum())
print(f"obs com leitos_internacao < leitos_sus  {n_incoerente}")
if n_incoerente:
    print("  !! nesses casos leitos_internacao não contém leitos_sus; V3 "
          "produziria ocupação MAIOR que a original")


# ---------------------------------------------------------------------------
# ENTREGA 1 — quantificação do >100%
# ---------------------------------------------------------------------------
df["acima_100"] = df["ocupacao_internacao"] > 100


def _bloco_acima(bloco: pd.DataFrame, estrato: str, cat: str) -> dict:
    n = len(bloco)
    if not n:
        return None
    ac = bloco[bloco["acima_100"]]
    n_cnes = bloco["cnes"].nunique()
    return {
        "estrato": estrato,
        "estrato_rotulo": ROTULOS.get(estrato, "todos"),
        "modelo_gestao_proxy": cat,
        "n_cnes": n_cnes,
        "n_hospital_ano": n,
        "n_acima_100": len(ac),
        "pct_acima_100": round(100 * len(ac) / n, 2),
        "n_cnes_com_algum_acima": ac["cnes"].nunique(),
        "media": round(bloco["ocupacao_internacao"].mean(), 2),
        "mediana": round(bloco["ocupacao_internacao"].median(), 2),
        "p95": round(bloco["ocupacao_internacao"].quantile(.95), 2),
        "maximo": round(bloco["ocupacao_internacao"].max(), 2),
        # quão longe passam de 100 os que passam: mede se é ruído de
        # arredondamento ou subdeclaração de porte
        "excesso_mediano_pp": round(ac["ocupacao_internacao"].median() - 100, 2)
        if len(ac) else np.nan,
        "tarja": TARJA if n_cnes < PISO_CNES else "",
    }


cats = [c for c in CATEGORIAS if (df["modelo_gestao_proxy"] == c).any()]
linhas = []
for e in ["TODOS"] + ESTRATOS:
    bloco_e = df if e == "TODOS" else df[df["estrato"] == e]
    for c in cats + ["TODAS"]:
        bloco = bloco_e if c == "TODAS" else bloco_e[bloco_e["modelo_gestao_proxy"] == c]
        lin = _bloco_acima(bloco, e, c)
        if lin:
            linhas.append(lin)
tab05b = pd.DataFrame(linhas)

PASTA_TAB.mkdir(parents=True, exist_ok=True)
tab05b.to_csv(PASTA_TAB / "tabSEG_05b_ocupacao_internacao_acima_100.csv",
              index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("tabSEG_05b — ocupação de internação acima de 100%, por categoria")
print("=" * 78)
tot = tab05b[tab05b["estrato"] == "TODOS"]
print(f"{'categoria':<20} {'% >100':>8} {'n>100':>7} {'n_obs':>7} "
      f"{'media':>8} {'mediana':>8} {'exc.med':>8} {'max':>8}")
for _, r in tot[tot["modelo_gestao_proxy"] != "TODAS"].iterrows():
    print(f"{r['modelo_gestao_proxy']:<20} {r['pct_acima_100']:>8.1f} "
          f"{r['n_acima_100']:>7} {r['n_hospital_ano']:>7} {r['media']:>8.1f} "
          f"{r['mediana']:>8.1f} {r['excesso_mediano_pp']:>8.1f} "
          f"{r['maximo']:>8.1f}")
r = tot[tot["modelo_gestao_proxy"] == "TODAS"].iloc[0]
print(f"{'TODAS':<20} {r['pct_acima_100']:>8.1f} {r['n_acima_100']:>7} "
      f"{r['n_hospital_ano']:>7} {r['media']:>8.1f} {r['mediana']:>8.1f} "
      f"{r['excesso_mediano_pp']:>8.1f} {r['maximo']:>8.1f}")

print("\npor estrato × categoria (% de observações acima de 100%):")
piv = tab05b[tab05b["estrato"] != "TODOS"].pivot(
    index="modelo_gestao_proxy", columns="estrato", values="pct_acima_100")
print(piv.reindex(cats + ["TODAS"]).to_string())


# ---------------------------------------------------------------------------
# ENTREGA 2 — as três variantes, lado a lado, sem escolha
# ---------------------------------------------------------------------------
df["ocup_int_censura100"] = df["ocupacao_internacao"].clip(upper=100)
df["ocup_int_missing100"] = df["ocupacao_internacao"].where(~df["acima_100"])
df["ocup_int_leitos_int"] = np.where(
    df["leitos_internacao"] > 0,
    100 * df["diarias_internacao"] / (df["leitos_internacao"] * DIAS_ANO),
    np.nan)

print("\n" + "-" * 78)
print("VARIANTES CRIADAS (nenhuma escolhida)")
print("-" * 78)
for col, rot in VARIANTES.items():
    val = df[col].dropna()
    print(f"  {rot:<34} n={len(val):>5}  mediana={val.median():>6.1f}  "
          f"%>100={100 * (val > 100).mean():>5.1f}")

linhas_c = []
for e in ["TODOS"] + ESTRATOS:
    bloco_e = df if e == "TODOS" else df[df["estrato"] == e]
    for c in cats + ["TODAS"]:
        bloco = bloco_e if c == "TODAS" else bloco_e[bloco_e["modelo_gestao_proxy"] == c]
        if not len(bloco):
            continue
        lin = {"estrato": e, "estrato_rotulo": ROTULOS.get(e, "todos"),
               "modelo_gestao_proxy": c, "n_cnes": bloco["cnes"].nunique(),
               "n_hospital_ano": len(bloco),
               "tarja": TARJA if bloco["cnes"].nunique() < PISO_CNES else ""}
        for col in VARIANTES:
            val = bloco[col].dropna()
            lin[f"{col}__n"] = len(val)
            lin[f"{col}__media"] = round(val.mean(), 2) if len(val) else np.nan
            lin[f"{col}__mediana"] = round(val.median(), 2) if len(val) else np.nan
        linhas_c.append(lin)
tab05c = pd.DataFrame(linhas_c)
tab05c.to_csv(PASTA_TAB / "tabSEG_05c_variantes_ocupacao_internacao.csv",
              index=False, encoding="utf-8-sig")

# O número que decide: quanto do gap OSS-Direta em E3 sobrevive a cada
# variante. Se o gap encolher muito, ele era artefato de cadastro.
print("\n" + "=" * 78)
print("O QUE ACONTECE COM O GAP OSS - DIRETA EM E3")
print("=" * 78)
e3 = df[df["estrato"] == "E3"]
print(f"{'variante':<34} {'OSS':>8} {'Direta':>8} {'gap':>8} {'n OSS':>7} "
      f"{'n Dir':>7}")
for col, rot in VARIANTES.items():
    v_oss = e3.loc[e3["modelo_gestao_proxy"] == "OSS", col].dropna()
    v_dir = e3.loc[e3["modelo_gestao_proxy"] == "Direta", col].dropna()
    m_oss, m_dir = v_oss.median(), v_dir.median()
    print(f"{rot:<34} {m_oss:>8.1f} {m_dir:>8.1f} {m_oss - m_dir:>8.1f} "
          f"{len(v_oss):>7} {len(v_dir):>7}")
print("\nO gap é medida descritiva bruta, sem controles nem efeito fixo — "
      "serve para\ndimensionar a sensibilidade do achado à escolha do "
      "denominador, não como efeito.")

# Por que V3 quase não move o OSS em E3: só há folga a ganhar onde existe
# leito de internação não-SUS. Onde leitos_sus == leitos_internacao, o
# hospital é integralmente SUS e trocar o denominador não muda nada — o
# excesso sobre 100% ali não vem de leito privado fora da conta.
print("\n" + "-" * 78)
print("FOLGA ENTRE leitos_sus E leitos_internacao (o que V3 teria a ganhar)")
print("-" * 78)
df["razao_sus_int"] = df["leitos_sus"] / df["leitos_internacao"]
print(f"{'':<20} " + " ".join(f"{e:>22}" for e in ESTRATOS))
for c in cats:
    partes = []
    for e in ESTRATOS:
        b = df[(df["modelo_gestao_proxy"] == c) & (df["estrato"] == e)]
        if not len(b):
            partes.append(f"{'--':>22}")
            continue
        raz = b["razao_sus_int"].median()
        pct_pleno = 100 * (b["leitos_sus"] == b["leitos_internacao"]).mean()
        partes.append(f"{raz:>9.2f} ({pct_pleno:>5.1f}% pleno)")
    print(f"{c:<20} " + " ".join(partes))
print("\n'pleno' = observações em que todo leito de internação é SUS;")
print("nelas V3 é idêntica a V0 por construção.")

# Perda de observações sob V2, por categoria: o custo de tratar >100 como
# não-observado não é neutro entre categorias.
print("\n" + "-" * 78)
print("PERDA DE OBSERVAÇÕES SOB V2 (missing acima de 100)")
print("-" * 78)
print(f"{'categoria':<20} {'n V0':>7} {'n V2':>7} {'perda':>8}")
for c in cats:
    b = df[df["modelo_gestao_proxy"] == c]
    n0, n2 = len(b), int(b["ocup_int_missing100"].notna().sum())
    print(f"{c:<20} {n0:>7} {n2:>7} {100 * (n0 - n2) / n0:>7.1f}%")

# A pergunta que decide o quanto isto contamina a ETAPA 4: a subdeclaração é
# traço estável do hospital ou episódio de ano? Se for estável, o efeito fixo
# de CNES a absorve, e ela só compromete comparação ENTRE grupos — não a
# identificação within, que é onde repousa o efeito OSS.
print("\n" + "-" * 78)
print("A SUBDECLARAÇÃO É TRAÇO DE HOSPITAL OU EPISÓDIO DE ANO?")
print("-" * 78)
g = df.groupby("cnes")
perfil = pd.DataFrame({
    "n_anos_acima": g["acima_100"].sum(),
    "leitos_sus_n_valores": g["leitos_sus"].nunique(),
    "categoria": g["modelo_gestao_proxy"].last(),
})
n_com = int((perfil["n_anos_acima"] > 0).sum())
print(f"CNES com ao menos um ano acima de 100% ..... {n_com} de {len(perfil)}")
print(f"CNES acima em TODOS os 11 anos ............. "
      f"{int((perfil['n_anos_acima'] == 11).sum())}")
print(f"CNES acima em 1 ou 2 anos apenas ........... "
      f"{int(perfil['n_anos_acima'].between(1, 2).sum())}")
print(f"mediana de anos acima, entre os afetados ... "
      f"{perfil.loc[perfil['n_anos_acima'] > 0, 'n_anos_acima'].median():.0f}")
print(f"\nCNES com leitos_sus constante nos 11 anos .. "
      f"{int((perfil['leitos_sus_n_valores'] == 1).sum())} de {len(perfil)}")
print("distribuição dos anos acima de 100%, entre os CNES afetados:")
print(perfil.loc[perfil["n_anos_acima"] > 0]
      .groupby("categoria")["n_anos_acima"]
      .agg(n_cnes="size", mediana="median", media="mean").round(1).to_string())


# ---------------------------------------------------------------------------
# ENTREGA 3 (evidência) — composição de complexidade dentro de E3
# ---------------------------------------------------------------------------
# Sustenta a restrição de citação R2: o par de mortalidade de E3 está em
# parte comprado por composição, porque a Direta carrega o casemix mais
# pesado mesmo dentro do estrato.
linhas_d = []
for c in cats:
    bloco = e3[e3["modelo_gestao_proxy"] == c]
    if not len(bloco):
        continue
    for faixa in sorted(e3["faixa_barcelona"].unique()):
        sub = bloco[bloco["faixa_barcelona"] == faixa]
        linhas_d.append({
            "modelo_gestao_proxy": c, "faixa_barcelona": int(faixa),
            "n_cnes": sub["cnes"].nunique(), "n_hospital_ano": len(sub),
            "pct_hospital_ano_da_categoria": round(100 * len(sub) / len(bloco), 1),
        })
tab05d = pd.DataFrame(linhas_d)
tab05d.to_csv(PASTA_TAB / "tabSEG_05d_composicao_faixa_e3.csv",
              index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("tabSEG_05d — composição de faixa_barcelona dentro de E3")
print("=" * 78)
piv_d = tab05d.pivot(index="modelo_gestao_proxy", columns="faixa_barcelona",
                     values="n_hospital_ano").reindex(cats).fillna(0).astype(int)
print("hospital-ano por faixa:")
print(piv_d.to_string())
piv_dc = tab05d.pivot(index="modelo_gestao_proxy", columns="faixa_barcelona",
                      values="n_cnes").reindex(cats).fillna(0).astype(int)
print("\nCNES por faixa:")
print(piv_dc.to_string())

print("\ncomplexidade estrutural média dentro de E3:")
for c in cats:
    bloco = e3[e3["modelo_gestao_proxy"] == c]
    if len(bloco):
        print(f"  {c:<20} faixa média {bloco['faixa_barcelona'].mean():.2f} | "
              f"escore Barcelona médio {bloco['complexidade_estrutural'].mean():.1f} | "
              f"mort_all mediana {bloco['mort_all'].median():.4f}")


# ---------------------------------------------------------------------------
# FIGURA
# ---------------------------------------------------------------------------
fig, eixos = plt.subplots(1, 2, figsize=(14, 5.6))

ax = eixos[0]
sub = tot[tot["modelo_gestao_proxy"] != "TODAS"]
ordem = sub["modelo_gestao_proxy"].tolist()
x = np.arange(len(ordem))
ax.bar(x, sub["pct_acima_100"], .62,
       color=[CORES_CAT[c] for c in ordem], edgecolor="white", lw=.6)
for xi, v in zip(x, sub["pct_acima_100"]):
    ax.annotate(f"{v:.1f}%", (xi, v), textcoords="offset points",
                xytext=(0, 3), ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels([c.replace(" ", "\n") for c in ordem], fontsize=9.5)
ax.set_ylabel("% das observações com ocupação > 100%")
ax.set_title("Ocupação de internação fisicamente impossível")

ax = eixos[1]
larg = .2
for k, (col, rot) in enumerate(VARIANTES.items()):
    med = [e3.loc[e3["modelo_gestao_proxy"] == c, col].median() for c in ordem]
    ax.bar(x + (k - 1.5) * larg, med, larg, label=rot,
           color=CORES_VAR[col], edgecolor="white", lw=.5)
ax.axhline(100, color=COR_EVENTO, lw=1, ls="dashed")
ax.annotate("100%", (len(ordem) - .4, 100), fontsize=9, color=COR_EVENTO,
            va="bottom", ha="right")
ax.set_xticks(x)
ax.set_xticklabels([c.replace(" ", "\n") for c in ordem], fontsize=9.5)
ax.set_ylabel("Mediana da ocupação de internação (%)")
ax.set_title("Dentro de E3: a mediana sob cada variante")
ax.legend(frameon=False, fontsize=9, loc="upper right")

fig.suptitle("Ocupação de internação: o denominador leitos_sus é subdeclarado, "
             "e a subdeclaração é diferencial por categoria\n"
             "as três variantes ficam lado a lado — nenhuma foi escolhida",
             fontsize=11)
fig.tight_layout(rect=[0, 0, 1, .94])
PASTA_FIG.mkdir(parents=True, exist_ok=True)
fig.savefig(PASTA_FIG / "figSEG_02b_ocupacao_internacao_acima_100.png",
            dpi=150, bbox_inches="tight", facecolor="white")
plt.close(fig)


# ---------------------------------------------------------------------------
# GRAVAÇÃO
# ---------------------------------------------------------------------------
if len(df) != N_IN:
    _parar(f"Observações perdidas: {N_IN:,} -> {len(df):,}.")
if list(df.columns)[:len(COLS_IN)] != COLS_IN:
    _parar("As colunas do painel de entrada foram alteradas ou reordenadas.")

df.to_csv(PAINEL_OUT, index=False, encoding="utf-8-sig")

print("\n" + "=" * 78)
print("ESCRITO")
print("=" * 78)
for nome in ("tabelas/tabSEG_05b_ocupacao_internacao_acima_100.csv",
             "tabelas/tabSEG_05c_variantes_ocupacao_internacao.csv",
             "tabelas/tabSEG_05d_composicao_faixa_e3.csv",
             "figuras_segmentacao/figSEG_02b_ocupacao_internacao_acima_100.png"):
    print(f"  analises/{nome}")
print(f"  {PAINEL_OUT.relative_to(RAIZ)}")
print(f"\ncolunas novas: acima_100, {', '.join(list(VARIANTES)[1:])} "
      f"({len(COLS_IN)} -> {df.shape[1]} colunas)")
print("\nDECISÃO EM ABERTO — nenhuma variante foi escolhida. A ETAPA 4 não "
      "pode\nrodar o modelo de ocupação de internação antes da ratificação "
      "(R1).")
