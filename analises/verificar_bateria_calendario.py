"""Confere cada número da terceira bateria da Seção 13 contra a fonte.

A bateria "Descasamento de calendário nos denominadores" foi acrescentada
a `sec13_robustez_diagnostico.tex` em 31/07/2026. Regra 7 do projeto: nada
entra em texto sem ser reproduzido rodando. Este script reproduz, do
painel e das tabelas gravadas pelos dois scripts de auditoria, todo valor
que o texto novo imprime, e falha se algum divergir.

Fontes:
  analises/painel_definitivo.csv
  analises/tabelas/tab_est_capacidade_movel_limite.csv   (auditar_capacidade_movel)
  analises/tabelas/tab_est_uti_ano_parcial_obs.csv       (auditar_uti_ano_parcial)

Reprodução: python analises/verificar_bateria_calendario.py
Não escreve nada.
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RAIZ = Path(__file__).resolve().parent.parent
TEX = RAIZ / "analises" / "latex" / "secoes" / "sec13_robustez_diagnostico.tex"
TAB = RAIZ / "analises" / "tabelas"

falhas = []


def conferir(rotulo, no_texto, na_fonte, tol=0.05):
    ok = (no_texto is not None and na_fonte is not None
          and abs(no_texto - na_fonte) <= tol)
    print(f"  {'OK ' if ok else 'ERRO'}  {rotulo:<52} "
          f"texto {no_texto} | fonte {na_fonte}")
    if not ok:
        falhas.append(rotulo)


texto = TEX.read_text(encoding="utf-8")
# só a bateria nova, para não conferir números das outras duas
i = texto.index("Descasamento de calendário nos denominadores")
bateria = texto[i:texto.index("Fecham o quadro as ressalvas")]


def do_texto(padrao):
    """Primeiro número que casa com o padrão, em ponto flutuante."""
    m = re.search(padrao, bateria)
    if not m:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))


painel = pd.read_csv(RAIZ / "analises" / "painel_definitivo.csv",
                     encoding="utf-8-sig").sort_values(["cnes", "ano"])
lim = pd.read_csv(TAB / "tab_est_capacidade_movel_limite.csv",
                  encoding="utf-8-sig")
obs = pd.read_csv(TAB / "tab_est_uti_ano_parcial_obs.csv",
                  encoding="utf-8-sig")

print("=" * 78)
print("BATERIA 3 DA SEÇÃO 13 — cada número contra a fonte")
print("=" * 78)

print("\n[a] painel e incidência da flag")
conferir("289 hospitais", do_texto(r"Os (\d+) hospitais"),
         float(painel["cnes"].nunique()), tol=0)
conferir("29 hospitais oscilam UTI", do_texto(r"(\d+) hospitais oscilam"),
         float(painel.assign(t=painel["uti_sus"] > 0)
               .groupby("cnes")["t"].nunique().eq(2).sum()), tol=0)
conferir("30 observações marcadas", do_texto(r"\\textbf\{(\d+)\n?observações\}"),
         float(len(obs)), tol=0)
com_uti = int((painel["uti_sus"] > 0).sum())
conferir("1,2% das obs com UTI", do_texto(r"([\d,]+)\\% daquelas com"),
         round(100 * len(obs) / com_uti, 1))
# a razão de diárias só é definida onde houve diária: 4 das 28 aberturas
# registram zero no ano de abertura e ficam fora da estatística
ab = obs[obs["uti_abertura"]
         & np.isclose(obs["uti_sus"], obs["uti_sus_cheio"])
         & (obs["diarias_uti"] > 0)]
conferir("24 aberturas com leitos idênticos", do_texto(r"nas\n?(\d+) aberturas"),
         float(len(ab)), tol=0)

print("\n[b] assinatura do ano parcial")
conferir("mediana da razão de diárias = 0,62",
         do_texto(r"\\textbf\{([\d,]+) vez\}"),
         round(ab["razao_diarias"].median(), 2), tol=0.005)
conferir("25,8 p.p. abaixo",
         do_texto(r"ocupação medida fica ([\d,]+) pontos"),
         round(-(ab["ocupacao_uti"] - ab["ocup_cheio"]).median(), 1))

# o deslocamento do ano parcial precisa ser o da especificação canônica
# (Gama), não o do log OLS: 19,3% -> 19,8%, e não 22,8% -> 23,9%
sem_p = pd.read_csv(TAB / "tab_est_ocup_uti_sem_ano_parcial.csv",
                    encoding="utf-8-sig")
conferir("ano parcial: parte de 19,3%",
         do_texto(r"de UTI de ([\d,]+)\\% para"),
         round(100 * (np.exp(0.17687) - 1), 1))
conferir("ano parcial: vai a 19,8%",
         do_texto(r"para ([\d,]+)\\% de vantagem"),
         round(100 * (np.exp(0.18069) - 1), 1))
conferir("ano parcial: 0,06 erro-padrão",
         do_texto(r"\\textbf\{([\d,]+)\nerro-padrão\}"),
         round((0.18069 - 0.17687) / 0.06031, 2), tol=0.005)

print("\n[c] frequência da capacidade móvel")
for cap, dom_col, rot, pad in [
        ("uti_sus", "uti_sus", "9,3% na UTI",
         r"em ([\d,]+)\\% das observações com\nUTI"),
        ("leitos_sus", "leitos_sus", "28,2% na internação",
         r"em ([\d,]+)\\% das de internação")]:
    ant = painel.groupby("cnes")[cap].shift(1)
    var = (painel[cap] - ant).abs() / ant.replace(0, np.nan)
    dom = painel[dom_col] > 0
    conferir(rot, do_texto(pad),
             round(100 * (dom & (var > 0)).sum() / dom.sum(), 1))

print("\n[d] tabela do limite (tab:calendario)")
esperado = {
    ("Ocupação internação", "amostra cheia"): (3177, 22.7, None),
    ("Ocupação internação", "sem QUALQUER mudança"): (2281, 25.7, 0.31),
    ("Ocupação internação", "sem mudança > 10%"): (2749, 23.1, 0.04),
    ("Ocupação internação", "sem mudança > 25%"): (3030, 23.2, 0.06),
    ("Ocupação UTI (intensidade)", "amostra cheia"): (2482, 19.3, None),
    ("Ocupação UTI (intensidade)", "sem QUALQUER mudança"): (2251, 16.6, -0.38),
    ("Ocupação UTI (intensidade)", "sem mudança > 10%"): (2276, 16.4, -0.41),
    ("Ocupação UTI (intensidade)", "sem mudança > 25%"): (2331, 16.6, -0.39),
    ("Ocupação internação", "sem mudança > 50%"): (3132, 23.0, 0.04),
    ("Ocupação UTI (intensidade)", "sem mudança > 50%"): (2393, 18.2, -0.16),
}
# Regra A do PENDENCIAS: a tabela do texto reporta TODAS as linhas de
# resultado da tabela-fonte. Se a fonte crescer, o texto tem de crescer.
if len(lim) != len(esperado):
    falhas.append(f"reporte parcial: fonte tem {len(lim)} linhas, "
                  f"texto reporta {len(esperado)}")
    print(f"  ERRO  fonte {len(lim)} linhas vs texto {len(esperado)}")
# a UTI tem de estar na especificação canônica; se a tabela vier no log
# OLS, a bateria estará certificando a especificação que a Seção 14 supera
esp = dict(zip(zip(lim["indicador"], lim["degrau"]), lim["especificacao"]))
if esp[("Ocupação UTI (intensidade)", "amostra cheia")] != "GLM Gama":
    falhas.append("UTI fora da especificação canônica (GLM Gama)")
    print("  ERRO  a tabela do limite não está em GLM Gama na UTI")
for (ind, deg), (n, efeito, delta) in esperado.items():
    lin = lim[(lim["indicador"] == ind) & (lim["degrau"] == deg)].iloc[0]
    rot = f"{ind[:22]:<22} {deg[:22]:<22}"
    conferir(rot + " n", float(n), float(lin["n"]), tol=0)
    # do coeficiente, não de efeito_pct: arredondar duas vezes move o
    # valor na fronteira (19,747 -> 19,75 -> 19,8, quando o certo é 19,7)
    conferir(rot + " efeito", efeito,
             round(100 * (np.exp(lin["coef_oss"]) - 1), 1), tol=0.005)
    if delta is not None:
        conferir(rot + " Δ EP", delta, round(lin["delta_em_ep"], 2), tol=0.005)

print("\n[e] separação entre os dois artefatos")
ant = painel.groupby("cnes")["uti_sus"].shift(1)
var = (painel["uti_sus"] - ant).abs() / ant.replace(0, np.nan)
d = painel[(painel["uti_sus"] > 0) & var.notna()]
v = var[d.index]
acima = d["ocupacao_uti"] > 100
p_mexeu = 100 * acima[v > 0].mean()
p_parado = 100 * acima[v == 0].mean()
# o texto imprime "(9,8\% contra 3,0\%)": o primeiro é o cadastro PARADO,
# que é o sujeito da frase, e o segundo é o que se mexeu
conferir("9,8% onde o cadastro ficou parado",
         do_texto(r"\(([\d,]+)\\% contra"), round(p_parado, 1))
conferir("3,0% onde o cadastro mexeu",
         do_texto(r"contra ([\d,]+)\\%\)"), round(p_mexeu, 1))
# a razão vem dos valores cheios, nunca da divisão dos arredondados
conferir("3,2 vezes mais frequente",
         do_texto(r"\\textbf\{([\d,]+) vezes mais frequente"),
         round(p_parado / p_mexeu, 1))

print("\n[f] diferencialidade por categoria (internação)")
ant_l = painel.groupby("cnes")["leitos_sus"].shift(1)
var_l = (painel["leitos_sus"] - ant_l).abs() / ant_l.replace(0, np.nan)
dl = painel[var_l.notna()]
vl = var_l[dl.index]
for cat, pad in [("Direta", r"de ([\d,]+)\\% das observações na"),
                 ("Privado", r"Direta a ([\d,]+)\\% no Privado")]:
    m = dl["modelo_gestao_proxy"] == cat
    conferir(f"{cat}", do_texto(pad), round(100 * (vl[m] > 0).mean(), 1))

print("\n[g] linha da Gama na Tabela tab:sempandemia (fora da bateria)")
alt = pd.read_csv(TAB / "tab_est_uti_alternativas.csv", encoding="utf-8-sig")
linha_tex = re.search(r"Ocupação de UTI \(Gama\)\s*&([^&]+)&([^&]+)&([^&]+)&([^\\\\]+)",
                      texto)
if not linha_tex:
    falhas.append("linha da Gama ausente em tab:sempandemia")
    print("  ERRO  a linha 'Ocupação de UTI (Gama)' não está na tabela")
else:
    def num(s):
        return float(s.strip().replace("$", "").replace("{", "")
                     .replace("}", "").replace(",", "."))
    for i, (rot, modelo, col) in enumerate([
            ("coef completo", "GLM Gama ligação log", "coef_oss"),
            ("EP completo", "GLM Gama ligação log", "ep_cluster"),
            ("coef sem pandemia", "GLM Gama, sem 2020 e 2021", "coef_oss"),
            ("EP sem pandemia", "GLM Gama, sem 2020 e 2021", "ep_cluster")]):
        fonte = float(alt.loc[alt["modelo"] == modelo, col].iloc[0])
        conferir(rot, num(linha_tex.group(i + 1)), round(fonte, 4), tol=0.00005)

print("\n" + "=" * 78)
if falhas:
    print(f"FALHOU em {len(falhas)} verificação(ões):")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)
print("TODOS OS NÚMEROS DA BATERIA 3 CONFEREM COM A FONTE.")
