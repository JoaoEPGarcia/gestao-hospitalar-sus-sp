"""
Frentes 2d, 3, 4 e 5 da auditoria editorial. Nao altera nada; reporta.

2d. Varredura de coerencia da tarja da SFA: toda mencao a SFA no documento
    esta sob a mesma regra?
3.  As duas classes que sobrevivem a auditoria numerica: omissao com vies
    direcional e adjetivo substituindo numero. Mais: todo ordenamento
    afirmado nomeia a estatistica que o ordena?
4.  As cinco declaracoes de limitacao estao onde o leitor as encontra?
5.  Sumario/abertura e conclusao dizem o mesmo que os resultados?
"""

from __future__ import annotations

import re
from pathlib import Path

SEC = Path(__file__).resolve().parent / "latex" / "secoes"
ARQ = sorted(SEC.glob("*.tex"))
TEX = {p.name: p.read_text(encoding="utf-8") for p in ARQ}


def norm(t):
    return re.sub(r"\s+", " ", t)


def cab(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


def frases_com(padrao, arquivos=None, janela=260):
    """Devolve (arquivo, linha, trecho) para cada ocorrencia."""
    out = []
    for nome in (arquivos or TEX):
        linhas = TEX[nome].splitlines()
        for i, l in enumerate(linhas):
            if re.search(padrao, l, re.I):
                ctx = norm(" ".join(linhas[max(0, i - 1):i + 3]))
                out.append((nome, i + 1, ctx[:janela]))
    return out


# ----------------------------------------------------------------------
cab("2d. Toda mencao a SFA esta sob a mesma regra de tarja?")

TARJA = (r"n[aã]o [eé] cit[aá]vel|n[aã]o cit[aá]vel|degenera|n[aã]o comparáve"
         r"|n[aã]o interpret|vale a ordem")
hits = frases_com(r"\bSFA\b|fronteira estoc[aá]stica")
print(f"{len(hits)} mencoes a SFA / fronteira estocastica\n")
sem_tarja = []
for nome, ln, ctx in hits:
    tem = bool(re.search(TARJA, ctx, re.I))
    marca = "COM tarja  " if tem else "SEM tarja >>"
    print(f"  {marca} {nome}:{ln}")
    print(f"       {ctx[:180]}")
    if not tem:
        sem_tarja.append((nome, ln))
print(f"\n  mencoes SEM tarja no contexto imediato: {len(sem_tarja)}")
for nome, ln in sem_tarja:
    print(f"    {nome}:{ln}")

# ----------------------------------------------------------------------
cab("3. Ordenamento afirmado sem a estatistica que o ordena")

ORD = (r"mais (eficiente|alta|cheia|intens|baixa)|melhor desempenho|"
       r"na ponta|primeiro lugar|[uú]ltimo lugar|acima da|abaixo da|"
       r"lidera|sai (melhor|pior)|ordena")
EST = r"median|m[eé]dia|percentil|escore|quartil|coeficiente|taxa|propor"
achados = []
for nome, ln, ctx in frases_com(ORD):
    if not re.search(EST, ctx, re.I):
        achados.append((nome, ln, ctx))
print(f"{len(achados)} passagens com ordenamento e sem estatistica nomeada "
      f"na vizinhanca:\n")
for nome, ln, ctx in achados:
    print(f"  {nome}:{ln}\n       {ctx[:200]}\n")

# ----------------------------------------------------------------------
cab("3b. Adjetivo de magnitude sem numero ao lado")

ADJ = (r"\b(muito|bastante|consideravel|considerável|expressiv|substancial|"
       r"forte(mente)?|marcadamente|dramatic|enorme|elevadissim|"
       r"significativamente melhor)\w*\b")
NUM = r"\d"
for nome, ln, ctx in frases_com(ADJ):
    if not re.search(NUM, ctx):
        print(f"  {nome}:{ln}\n       {ctx[:200]}\n")

# ----------------------------------------------------------------------
cab("4. As cinco declaracoes de limitacao")

CINCO = {
    "a) cinco switchers com confundidor":
        r"cinco conversores|cinco switchers|cinco hospitais que",
    "b) os cinco foram para o mesmo operador":
        r"mesmo tipo de operador|mesmo operador",
    "c) Privado n=3 nao interpretavel":
        r"3 hospitais|3 CNES|tr[eê]s hospitais",
    "d) nenhum coeficiente da SFA e citavel":
        r"SFA n[aã]o [eé] cit[aá]vel|n[aã]o [eé] cit[aá]vel.{0,40}SFA|"
        r"NÍVEL\s+da efici[eê]ncia das OSS na SFA n[aã]o [eé] cit[aá]vel",
    "e) modelo_gestao_proxy mede categoria administrativa":
        r"modelo\\_gestao\\_proxy|classifica[cç][aã]o assistencial do SIH",
}
for rot, pad in CINCO.items():
    hs = frases_com(pad)
    print(f"\n{rot}: {len(hs)} ocorrencia(s)")
    for nome, ln, ctx in hs[:6]:
        print(f"    {nome}:{ln}  {ctx[:150]}")

# ----------------------------------------------------------------------
cab("5. Abertura e conclusao contra os resultados")

for nome in ("sec00_resumo.tex", "sec01_painel.tex", "sec17_conclusao.tex"):
    if nome in TEX:
        n = len(TEX[nome].splitlines())
        print(f"  {nome}: {n} linhas")
print("\narquivos do documento, em ordem:")
for p in ARQ:
    print(f"  {p.name}")
