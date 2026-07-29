"""
Verificação das cinco famílias da intensidade de UTI (Etapa 5).

Reproduz, a partir de `resultados_fase2/tabelas/tabE5_sensibilidade_familias.csv`:

  - o efeito percentual exp(coef) - 1 de cada especificação;
  - os limites do IC95% convertidos para pontos percentuais;
  - a decomposição da atenuação em zeros x função de variância;
  - a diferença entre a ziGamma e a Gama publicada, casa decimal a casa
    decimal.

Nada aqui é reestimação: é conversão de escala das saídas já gravadas por
`fase2_ocupacao_familias.R`. O script existe porque os números que entram no
registro permanente (R10) não devem ser copiados do próprio registro — e
porque a conversão de escala foi exatamente onde se encontrou um erro: o
limite inferior do IC da Gama publicada constava como +5,6%, lido em pontos
de log, quando exponenciado é +5,7%.

Rodar com o venv do projeto:
    .venv\\Scripts\\python.exe verificar_familias_e5.py
"""

import csv
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
CSV = BASE / "resultados_fase2" / "tabelas" / "tabE5_sensibilidade_familias.csv"


def pct(x):
    """coeficiente em pontos de log -> variação percentual"""
    return (math.exp(float(x)) - 1.0) * 100.0


rows = list(csv.DictReader(CSV.open(encoding="utf-8")))

print("=" * 78)
print("CINCO FAMILIAS — intensidade de UTI")
print("=" * 78)
print(f"{'especificacao':<34}{'n':>6}{'coef':>10}{'EP':>9}"
      f"{'efeito':>9}{'IC lo':>9}{'IC hi':>9}")
print("-" * 78)

for r in rows:
    if r["situacao"] != "estimado":
        print(f"{r['especificacao'].strip():<34}{r['n']:>6}"
              f"{'':>10}{'':>9}{'FALHOU':>9}")
        continue
    print(f"{r['especificacao'].strip():<34}{int(r['n']):>6}"
          f"{float(r['coef_oss']):>10.5f}{float(r['ep']):>9.4f}"
          f"{pct(r['coef_oss']):>8.2f}%"
          f"{pct(r['ic_lo']):>8.2f}%{pct(r['ic_hi']):>8.2f}%")

d = {r["especificacao"].strip().split()[0]: r for r in rows}

print()
print("=" * 78)
print("ziGamma vs Gama publicada — quantas casas decimais coincidem")
print("=" * 78)
g = float(d["G_semzero"]["coef_oss"])
z = float(d["ZIG_comzero"]["coef_oss"])
print(f"  Gama publicada  (G_semzero)  : {g:.5f}")
print(f"  ziGamma/hurdle  (ZIG_comzero): {z:.5f}")
print(f"  diferenca absoluta           : {abs(z - g):.2e}")
for casas in (2, 3, 4, 5):
    igual = round(g, casas) == round(z, casas)
    print(f"  arredondado a {casas} casas: {round(g, casas)} vs "
          f"{round(z, casas)}  -> {'IGUAL' if igual else 'DIFERE'}")
print("  (o registro dizia 'quarta casa'; coincide ate a TERCEIRA)")

print()
print("=" * 78)
print("Decomposicao da atenuacao Gama -> Tweedie (zeros x funcao de variancia)")
print("=" * 78)
t_sem = float(d["T_semzero"]["coef_oss"])
t_com = float(d["T_comzero"]["coef_oss"])
zeros = t_com - t_sem
varfun = t_sem - g
total = zeros + varfun
print(f"  zeros   (T_com - T_sem) : {zeros:+.5f}   {100 * zeros / total:5.1f}%")
print(f"  V(mu)   (T_sem - G_sem) : {varfun:+.5f}   {100 * varfun / total:5.1f}%")
print(f"  total                   : {total:+.5f}")

print()
print("=" * 78)
print("Lognormal — o afastamento e de precisao, nao de ponto")
print("=" * 78)
ln = d["LN_semzero"]
ln_c, ln_ep = float(ln["coef_oss"]), float(ln["ep"])
ep_t, ep_g = float(d["T_semzero"]["ep"]), float(d["G_semzero"]["ep"])
print(f"  lognormal       coef {ln_c:.5f}  EP {ln_ep:.5f}")
print(f"  Tweedie s/zeros coef {t_sem:.5f}  EP {ep_t:.5f}")
print(f"  Gama publicada  coef {g:.5f}  EP {ep_g:.5f}")
print(f"  distancia lognormal vs Tweedie (mesma amostra): "
      f"{abs(ln_c - t_sem):.5f} em pontos de log")
print(f"  EP lognormal / EP Tweedie : {ln_ep / ep_t:.3f}")
print(f"  EP lognormal / EP Gama    : {ln_ep / ep_g:.3f}")
print(f"  limite inferior do IC (log): {float(ln['ic_lo']):+.5f}")

print()
print("  AIC por especificacao — NAO comparaveis entre escalas da resposta.")
print("  A lognormal ajusta log(y) e as demais ajustam y; o AIC menor dela")
print("  NAO indica ajuste melhor.")
for r in rows:
    if r["situacao"] == "estimado":
        print(f"    {r['especificacao'].strip():<32} {float(r['aic']):>10.1f}")
