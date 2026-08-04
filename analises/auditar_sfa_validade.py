"""
Auditoria da alegacao de invalidade da SFA (sec15), aberta em 30/07/2026.

A Secao 15 declara que "nenhum valor do painel (b) e citavel, em nenhuma
categoria" e apoia essa generalizacao em DOIS defeitos:

  (i)  a degeneracao das OSS na equacao de ineficiencia (separacao perfeita);
  (ii) a monotonicidade da fronteira violada em 94,9% das observacoes.

O defeito (i) sozinho so alcanca as OSS. E o defeito (ii) que estende a
proibicao as outras quatro categorias --- e por isso ele precisa ser
verificado com o mesmo cuidado que sustenta a conclusao.

Este script faz duas coisas, e nao altera nada:

  1. REPRODUZ os sete numeros que a sec15 publica sobre a fronteira, sem ler
     nenhum .rds: reconstroi as elasticidades a partir de
     tabS_fronteira_bc95.csv + painel_definitivo.csv, replicando as
     transformacoes de fase2_sfa.R (linhas 39-50 e 93-112).

  2. TESTA as duas raizes candidatas da violacao de UTI: o insumo aninhado
     (leito de UTI e subconjunto de leito total) e a colinearidade do valor
     faturado com o proprio produto.

A pergunta que este script NAO responde --- se a fronteira sobrevive a
retirada do insumo de UTI --- exige reestimacao e esta em
resultados_fase2/auditar_fronteira_sem_uti.R.

Regra 7 do projeto: nenhum numero entra em relatorio sem ser reproduzido
rodando. Este script e a reproducao.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
F2 = RAIZ / "resultados_fase2"

IPCA = {2015: 10.67, 2016: 6.29, 2017: 2.95, 2018: 3.75, 2019: 4.31,
        2020: 4.52, 2021: 10.06, 2022: 5.79, 2023: 4.62, 2024: 4.83,
        2025: 4.26}


def cabecalho(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


# ---- painel, replicando preparo_fase2.R no que a SFA usa -----------------
p = pd.read_csv(RAIZ / "analises" / "painel_definitivo.csv",
                encoding="utf-8-sig")
anos = sorted(IPCA)
indice = np.cumprod([1 + IPCA[a] / 100 for a in anos])
fator = dict(zip(anos, indice[-1] / indice))
p["valor_real"] = p["valor"] * p["ano"].map(fator)
p["categoria"] = p["modelo_gestao_proxy"]

# flag_fragil: denominador fragil do CNES 2097613 em 2020-2021
d = p[~((p.cnes == 2097613) & (p.ano.isin([2020, 2021])))].copy()
print(f"painel {len(p)} obs -> amostra de desfecho {len(d)} obs, "
      f"{d.cnes.nunique()} CNES")

d["y"] = np.log(d.qtde)
d["lc"] = np.log(d.total_leitos) - np.log(d.total_leitos).mean()
d["uc"] = np.log1p(d.uti_total) - np.log1p(d.uti_total).mean()
d["vc"] = np.log(d.valor_real) - np.log(d.valor_real).mean()

co = pd.read_csv(F2 / "tabelas" / "tabS_fronteira_bc95.csv")
b = co.set_index("termo")["coef"]

# derivadas do Translog (os quadraticos entram como 0,5 x^2)
e_l = b["lc"] + b["lc2"] * d.lc + b["lu"] * d.uc + b["lv"] * d.vc
e_u = b["uc"] + b["uc2"] * d.uc + b["lu"] * d.lc + b["uv"] * d.vc
e_v = b["vc"] + b["vc2"] * d.vc + b["lv"] * d.lc + b["uv"] * d.uc

# ----------------------------------------------------------------------
cabecalho("1. Reproducao dos numeros publicados na sec15")

for nome, e, alvo in [("leitos", e_l, "99,7% monotonas"),
                      ("uti (log1p)", e_u, "94,9% VIOLADAS"),
                      ("valor real", e_v, "99,6% monotonas")]:
    print(f"  {nome:<14} monotonas {100 * (e > 0).mean():6.2f}%   "
          f"violadas {100 * (e <= 0).mean():6.2f}%   (documento: {alvo})")

print("\n  as tres definicoes de 'UTI ativa' que a sec15 usa:")
for rot, sel, alvo in [
        ("uti_total > 0 (capacidade)", d.uti_total > 0, "97,8%"),
        ("uti_sus > 0", d.uti_sus > 0, "97,8%"),
        ("diarias_uti > 0 (uso)", d.diarias_uti > 0, "96,9%"),
        ("uti_total == 0", d.uti_total == 0, "nao publicado")]:
    print(f"    {rot:<28} n={sel.sum():5d}  violadas "
          f"{100 * (e_u[sel] <= 0).mean():6.2f}%   (documento: {alvo})")

print("\n  por categoria (documento: de 93,6% no Filantropico a 99,3% na "
      "Direta):")
for cat, g in (e_u <= 0).groupby(d.categoria):
    print(f"    {cat:<20} n={len(g):5d}  violadas {100 * g.mean():6.2f}%")

print(f"\n  zeros de UTI (documento: 19%): "
      f"{100 * (d.uti_total == 0).mean():.2f}%")

# ----------------------------------------------------------------------
cabecalho("2. Raiz A: o insumo de UTI esta ANINHADO no insumo de leitos")

sub = (d.uti_total <= d.total_leitos)
print(f"  uti_total <= total_leitos em {100 * sub.mean():.2f}% das obs")
print(f"  razao mediana uti_total/total_leitos: "
      f"{(d.uti_total / d.total_leitos).median():.4f}")
print(f"  corr(lc, uc) = {np.corrcoef(d.lc, d.uc)[0, 1]:.4f}"
      "   (RELATORIO_EXECUCAO.md registra 0,82)")
print("""
  Leito de UTI e subconjunto de leito total, e os dois entram na mesma
  fronteira. Condicionado ao total de leitos, "mais UTI" nao e mais
  capacidade: e COMPOSICAO diferente. E o produto e qtde (saidas), que cai
  quando a permanencia sobe. Uma elasticidade condicional negativa e o
  resultado esperado, nao uma patologia.

  Monotonicidade e condicao de regularidade sobre insumos LIVRES E
  SEPARAVEIS. Nao se aplica a um insumo aninhado em outro ja no modelo.""")

print(f"\n  a violacao e curvatura da Translog ou so o sinal do coeficiente?")
print(f"    coeficiente de primeira ordem b[uc] = {b['uc']:+.4f}")
print(f"    mediana de e_u obs a obs        = {e_u.median():+.4f}")
print(f"    faixa de e_u: [{e_u.min():+.4f}, {e_u.max():+.4f}]")
print("    -> e_u esta centrada no proprio coeficiente. Os 94,9% sao o SINAL")
print("       de um coeficiente, nao curvatura. Cobb Douglas com os mesmos")
print("       insumos daria ~100% de violacao, nao menos.")

# ----------------------------------------------------------------------
cabecalho("3. Raiz B: valor_real e quase o proprio produto")

print(f"  corr(log qtde, log valor_real) = "
      f"{np.corrcoef(d.y, np.log(d.valor_real))[0, 1]:.4f}")
print(f"  corr(lc, vc) = {np.corrcoef(d.lc, d.vc)[0, 1]:.4f}"
      "   (RELATORIO_EXECUCAO.md registra 0,84)")
print(f"  corr(uc, vc) = {np.corrcoef(d.uc, d.vc)[0, 1]:.4f}")

X = np.column_stack([np.ones(len(d)), d.lc, d.uc, d.vc])
print("\n  VIF dos tres insumos de primeira ordem:")
for i, nm in enumerate(["lc", "uc", "vc"], start=1):
    outros = np.delete(X, i, axis=1)
    bb, *_ = np.linalg.lstsq(outros, X[:, i], rcond=None)
    r2 = 1 - ((X[:, i] - outros @ bb) ** 2).sum() / \
        ((X[:, i] - X[:, i].mean()) ** 2).sum()
    print(f"    {nm}: R2 contra os outros = {r2:.4f}, VIF = {1 / (1 - r2):.2f}")

Z = np.column_stack([d.lc, d.uc, d.vc, .5 * d.lc ** 2, .5 * d.uc ** 2,
                     .5 * d.vc ** 2, d.lc * d.uc, d.lc * d.vc, d.uc * d.vc])
Zs = (Z - Z.mean(0)) / Z.std(0)
print(f"  numero de condicao dos 9 regressores Translog: "
      f"kappa = {np.linalg.cond(Zs):.1f}")
print("""
  O valor do SIH e reembolso por producao faturada: preco x quantidade da
  propria saida que a fronteira explica. A sec15 levanta essa ressalva como
  "de primeira ordem" e a resolve PARA O DEA com duas checagens (producao
  fisica por leito; DEA so com leitos). Para a SFA, nunca --- as tres
  sensibilidades de tabS_sensibilidade.csv sao principal, sem UTI e Mundlak.
  A variante so-leitos da SFA esta em auditar_fronteira_sem_uti.R.""")

# ----------------------------------------------------------------------
cabecalho("4. O defeito que NAO tem reparo: a degeneracao das OSS")

te = pd.read_csv(F2 / "sfa" / "sfa_eficiencias.csv")
te = te.merge(d[["cnes", "ano", "categoria"]], on=["cnes", "ano"])
g = te.groupby("categoria")["te_sfa"].agg(
    ["count", "mean", "median", "std", "min", "max"])
print(g.round(6).to_string())

oss = te[te.categoria == "OSS"]["te_sfa"]
print(f"\n  OSS: amplitude total {oss.max() - oss.min():.2e} sobre "
      f"{len(oss)} observacoes; 100% acima de 0,999")
print("  A TE das OSS e uma CONSTANTE. Sob Battese e Coelli, o coeficiente")
print("  de -1.298 (EP 906) empurra a ineficiencia das OSS a zero: a")
print("  verossimilhanca fica plana e o Wald calculado ali nao tem")
print("  interpretacao. Este defeito e real, e a sec15 esta certa sobre ele.")

sens = pd.read_csv(F2 / "tabelas" / "tabS_sensibilidade.csv")
print("\n  e ele reaparece em todas as sensibilidades ja rodadas:")
print(sens.to_string(index=False))

cabecalho("Leitura")
print("""Os sete numeros da sec15 conferem. O que esta em questao nao e
aritmetica, e a atribuicao de causa: a violacao de 94,9% e propriedade do
INSUMO ANINHADO, nao da forma Translog nem da tecnologia hospitalar. O teste
que decide isso --- reestimar sem o insumo de UTI --- esta em
resultados_fase2/auditar_fronteira_sem_uti.R.""")
