# verificar_restricoes_no_texto.py
# BLOCO 5 — as restrições de leitura foram violadas no texto novo?
#
# Cada restrição vira um teste sobre o .tex: ou um padrão PROIBIDO que não
# pode aparecer, ou um padrão OBRIGATÓRIO que precisa acompanhar um número.
# Reporta; não corrige.

import re
import unicodedata
from pathlib import Path

SEC = Path(__file__).resolve().parent / "latex" / "secoes"

NOVAS = ["sec02_univariada.tex", "sec04_categorias.tex",
         "sec08_correlacao_variancia.tex",
         "sec13b_segmentacao_estrutural.tex",
         "sec15_fase2_eficiencia.tex", "sec17_conclusao.tex",
         "apendiceA_diagnosticos.tex"]

TODAS = sorted(p.name for p in SEC.glob("*.tex"))


def normalizar(t):
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t.lower())


textos = {n: normalizar((SEC / n).read_text(encoding="utf-8")) for n in TODAS}
novo = " ".join(textos[n] for n in NOVAS if n in textos)
tudo = " ".join(textos.values())

falhas, passou = [], []


def proibido(rot, padrao, alvo=None, escopo="texto novo"):
    t = novo if alvo is None else alvo
    m = re.search(padrao, t)
    if m:
        ini = max(0, m.start() - 90)
        falhas.append(f"{rot}: ENCONTRADO em {escopo} -> ...{t[ini:m.end() + 60]}...")
    else:
        passou.append(rot)


def obrigatorio(rot, padrao, alvo=None):
    t = novo if alvo is None else alvo
    if re.search(padrao, t):
        passou.append(rot)
    else:
        falhas.append(f"{rot}: AUSENTE — o texto novo não traz a qualificação")


print("=" * 78)
print("R2 — o par bruto de mortalidade de E3 não é citável")
print("=" * 78)
# os valores proibidos: Direta 0,0698 contra OSS 0,0536, em qualquer forma
proibido("R2 par bruto 0,0698", r"0[,{]?,?698|0,0698")
proibido("R2 par bruto 0,0536", r"0[,{]?,?536|0,0536")
obrigatorio("R2 o controle é explicitado junto ao coeficiente",
            r"controla a complexidade Barcelona|com esse controle explicitado")
obrigatorio("R2 a proibição do par bruto é declarada",
            r"diferenca bruta de mortalidade .{0,40}nao e citavel")

print("=" * 78)
print("R5 — pressão assistencial não entra como covariável")
print("=" * 78)
proibido("R5 ocupação como covariável de mortalidade/TMP",
         r"(ocupacao|superlotacao|pressao assistencial)[^.]{0,80}"
         r"como (covariavel|controle)[^.]{0,60}(mortalidade|tmp)")

print("=" * 78)
print("R9 — o que não pode ser dito sobre a Etapa 4")
print("=" * 78)
obrigatorio("R9.1 E1/E2 declarados sem identificação within",
            r"e1 nao tem nenhum hospital que trocou de rede")
obrigatorio("R9.1 o −72,9% é rotulado ruído",
            r"nao e achado; e ruido com tarja")
obrigatorio("R9.2 identificação repousa sobre Sorocaba e Pérola",
            r"identificacao repousa sobre o conjunto hospitalar de sorocaba e o perola")
obrigatorio("R9.2 a frase do desenho sobrevive",
            r"nao e um desenho limpo; e o desenho disponivel")
obrigatorio("R9.4 Privado não interpretado",
            r"privado nao e interpretado em nenhum estrato")
obrigatorio("R9 DEA não é evidência independente",
            r"dea \*?\*?nao e evidencia independente|nao e\*?\*? evidencia independente")
# o padrão precisa tolerar a marcação LaTeX entre as palavras: o texto traz
# "\textbf{cruza o zero}: não se pode dizer...". Casar literal falharia por
# causa da chave, e a falha seria do verificador, não do documento.
obrigatorio("1.3 faturamento em E3 cruza o zero",
            r"cruza o zero.{0,4}: nao se pode dizer que as oss faturam menos")

print("=" * 78)
print("R10 — a nulidade do binário é falta de potência")
print("=" * 78)
obrigatorio("R10 nulo não é ausência de efeito",
            r"nao e evidencia de que nao ha efeito")
obrigatorio("R10 a proibição das duas direções",
            r"nao se deve escrever que a gestao nao afeta a superlotacao, nem que afeta")
obrigatorio("R10 número de switchers declarado",
            r"quatro hospitais no painel inteiro que sustentam essa estimativa")
obrigatorio("1.5C refinamento dos switchers pós-conversão",
            r"apenas dois deles registram superlotacao do lado posterior")

print("=" * 78)
print("1.5 — as três qualificações de amostra")
print("=" * 78)
obrigatorio("1.5A perda de amostra da parte B declarada",
            r"989|122 hospitais|tres hospitais inteiros|3 cnes")
# 1.5B: a sensibilidade R4.2 não pode ser citada como significativa
proibido("1.5B R4.2 citada como significativa sem a qualificação",
         r"significativa na sensibilidade")

print("=" * 78)
print("Renomeação — nenhuma reivindicação bayesiana sobrevive")
print("=" * 78)
proibido("rótulo bayesiano no documento inteiro",
         r"modelos bayesianos|bayesiana hierarquica|hierarquico bayesiano",
         alvo=tudo, escopo="documento inteiro")
proibido("famílias inferenciais distintas (afirmação falsa)",
         r"familias inferenciais distintas|convergencia entre paradigmas",
         alvo=tudo, escopo="documento inteiro")

print("=" * 78)
print("Regra transversal — nenhum ordenamento sem a estatística nomeada")
print("=" * 78)
obrigatorio("inversão da UTI nomeia média e mediana",
            r"pela \*?\*?media\*?\*?, o filantropico")
obrigatorio("gradiente dos estratos nomeia a mediana",
            r"as medianas dos tres estratos ordenam monotonicamente")

print()
print("=" * 78)
print(f"RESULTADO: {len(passou)} restrições verificadas, {len(falhas)} problemas")
print("=" * 78)
for f in falhas:
    print(f"  [PROBLEMA] {f}")
if not falhas:
    print("  Nenhuma restrição de leitura violada no texto novo.")
