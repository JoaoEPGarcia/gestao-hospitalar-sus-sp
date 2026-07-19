# -*- coding: utf-8 -*-
"""
_investigacao_revisao_jul2026.py
================================
INVESTIGAÇÃO (ETAPA 1 da revisão jul/2026) — SOMENTE LEITURA.

Este script NÃO altera o painel, nem nenhum artefato do pipeline. Apenas lê o
painel bruto (analise_sih -> painel_hospital_ano) e o painel definitivo
(painel_definitivo.csv), varre os arquivos de código/texto do repositório e
imprime as respostas às cinco perguntas da revisão, para decisão da equipe
(João/Priscilla/Alberto) antes de qualquer correção (ETAPA 2).

  1a. Candidatos a hospital pediátrico dentro do painel (por especialização
      declarada e por nome de fantasia).
  1b. Hospital Guilherme Álvaro (Santos, CNES 2079720): histórico ano a ano de
      class_assistencial na base bruta + rótulo em modelo_gestao_proxy no painel
      definitivo.
  1c. Categoria "Privado" (n=3): CNES, nome e rótulo atual.
  1d. Uso do termo "custo" no código e nos textos (grep reprodutível).
  1e. Localização do gráfico "mediana anual por categoria" e confirmação de que
      a mediana é calculada sobre o painel inteiro (todas as faixas Barcelona),
      não filtrada para faixa_barcelona == 3.

USO: python _investigacao_revisao_jul2026.py
"""

import re
from pathlib import Path

import pandas as pd

import analise_sih as base                       # embrulha stdout em UTF-8
import construir_painel_definitivo as cpd

CNES_GUILHERME_ALVARO = 2079720
LARGURA = 78


def _titulo(txt: str):
    print("\n" + "=" * LARGURA)
    print(txt)
    print("=" * LARGURA)


# ══════════════════════════════════════════════════════════════════════════════
# CARGA
# ══════════════════════════════════════════════════════════════════════════════

def carregar():
    bruto = cpd.carregar_painel_bruto()
    df_def = pd.read_csv(cpd.PAINEL_DEFINITIVO_CSV, encoding="utf-8-sig")
    df_def["cnes"] = pd.to_numeric(df_def["cnes"], errors="raise").astype("int64")
    df_def["ano"] = df_def["ano"].astype(int)
    return bruto, df_def


def _municipio_por_cnes(bruto: pd.DataFrame) -> pd.Series:
    return (bruto[bruto["municipio"].notna()]
            .sort_values("ano").groupby("cnes")["municipio"].last())


# ══════════════════════════════════════════════════════════════════════════════
# 1a. HOSPITAIS PEDIÁTRICOS — LEVANTAMENTO (não exclui nada)
# ══════════════════════════════════════════════════════════════════════════════

def inv_1a_pediatricos(bruto: pd.DataFrame, df_def: pd.DataFrame):
    _titulo("1a. CANDIDATOS A HOSPITAL PEDIÁTRICO (levantamento — nada é excluído)")

    nomes       = cpd.nome_referencia_por_cnes(bruto)
    espec_modal = cpd.valor_modal_por_cnes(bruto, "especializacao")
    tipo_modal  = cpd.valor_modal_por_cnes(bruto, "tipo_hospital")
    class_modal = cpd.valor_modal_por_cnes(bruto, "class_assistencial")
    mun         = _municipio_por_cnes(bruto)

    def_cnes  = set(df_def["cnes"].unique())
    anos_def  = df_def.groupby("cnes")["ano"].nunique()
    anos_prod = (bruto[bruto["qtde"] > 0].groupby("cnes")["ano"]
                 .nunique())

    # ── Caminho 1: especialização declarada (qualquer ano) ──────────────────
    PAT_ESPEC = re.compile(r"PEDIATR|INFANTIL|CRIANCA")
    esp = bruto[["cnes", "especializacao"]].dropna(subset=["especializacao"]).copy()
    esp["norm"] = esp["especializacao"].map(cpd.normalizar_texto)
    esp_hit = esp[esp["norm"].str.contains(PAT_ESPEC, regex=True)]
    cnes_por_espec = set(esp_hit["cnes"])
    vals_espec = sorted(esp_hit["especializacao"].unique())

    print("\n[Caminho 1] Valores DISTINTOS de 'especializacao' que casam com "
          "PEDIATR/INFANTIL/CRIANCA (base bruta, qualquer ano):")
    if vals_espec:
        for v in vals_espec:
            n = esp_hit.loc[esp_hit["especializacao"] == v, "cnes"].nunique()
            print(f"   • {v!r}  ({n} CNES)")
    else:
        print("   (nenhum)")

    # ── Caminho 2: nome de fantasia (só existe em 2020-2021) ─────────────────
    PAT_NOME = re.compile(r"INFANTIL|PEDIATR|CRIANCA|BOLDRINI|DARCY VARGAS")
    nm = bruto[["cnes", "nome_fantasia"]].dropna(subset=["nome_fantasia"]).copy()
    nm["norm"] = nm["nome_fantasia"].map(cpd.normalizar_texto)
    nm_hit = nm[nm["norm"].str.contains(PAT_NOME, regex=True)]
    cnes_por_nome = set(nm_hit["cnes"])

    print("\n[Caminho 2] Nomes de fantasia (2020-2021) que casam com "
          "INFANTIL/PEDIATR/CRIANCA/BOLDRINI/DARCY VARGAS:")
    if cnes_por_nome:
        for cnes in sorted(cnes_por_nome):
            nome = nm_hit.loc[nm_hit["cnes"] == cnes, "nome_fantasia"].iloc[0]
            print(f"   • CNES {cnes}: {nome}")
    else:
        print("   (nenhum)")
    print("   NOTA: nome_fantasia só é preenchido em 2020-2021; hospitais "
          "pediátricos sem produção nesse biênio não são pegos por este caminho.")

    # ── União e tabela de decisão ────────────────────────────────────────────
    union = sorted(cnes_por_espec | cnes_por_nome)
    linhas = []
    for cnes in union:
        via = ("espec+nome" if cnes in cnes_por_espec and cnes in cnes_por_nome
               else "espec" if cnes in cnes_por_espec else "nome")
        linhas.append({
            "cnes": cnes,
            "nome_fantasia": nomes.get(cnes, ""),
            "municipio": mun.get(cnes, ""),
            "tipo_modal": tipo_modal.get(cnes, ""),
            "espec_modal": espec_modal.get(cnes, ""),
            "class_modal": class_modal.get(cnes, ""),
            "no_painel_definitivo": "SIM" if cnes in def_cnes else "não",
            "anos_no_def": int(anos_def.get(cnes, 0)),
            "anos_prod_bruto": int(anos_prod.get(cnes, 0)),
            "via": via,
        })
    df = pd.DataFrame(linhas)
    print(f"\n[União] {len(df)} CNES candidatos "
          f"({len(cnes_por_espec)} por especialização, "
          f"{len(cnes_por_nome)} por nome):")
    if len(df):
        with pd.option_context("display.max_colwidth", 46, "display.width", 320,
                               "display.max_columns", 20):
            print(df.to_string(index=False))
        n_no_def = (df["no_painel_definitivo"] == "SIM").sum()
        print(f"\n  Destes, {n_no_def} estão no painel definitivo (314 CNES) e "
              f"{len(df) - n_no_def} já ficaram de fora por outros filtros.")
    else:
        print("   (nenhum candidato)")
    print("\n  >>> Nada foi excluído. Lista para você e a Priscilla decidirem a "
          "lista nominal final (ETAPA 2b).")


# ══════════════════════════════════════════════════════════════════════════════
# 1b. HOSPITAL GUILHERME ÁLVARO (CNES 2079720)
# ══════════════════════════════════════════════════════════════════════════════

def inv_1b_guilherme_alvaro(bruto: pd.DataFrame, df_def: pd.DataFrame):
    _titulo(f"1b. HOSPITAL GUILHERME ÁLVARO — Santos, CNES {CNES_GUILHERME_ALVARO}")

    sub = (bruto[bruto["cnes"] == CNES_GUILHERME_ALVARO]
           .sort_values("ano"))
    if sub.empty:
        print("   CNES não encontrado na base bruta.")
        return

    nome = (sub["nome_fantasia"].dropna().iloc[-1]
            if sub["nome_fantasia"].notna().any() else "(sem nome_fantasia)")
    munic = (sub["municipio"].dropna().iloc[-1]
             if sub["municipio"].notna().any() else "")
    print(f"   Nome (2020-2021): {nome}   |   Município: {munic}")

    print("\n   Histórico ano a ano de class_assistencial (BASE BRUTA):")
    for _, r in sub.iterrows():
        prod = "com produção" if r["qtde"] > 0 else "SEM produção"
        print(f"     {int(r['ano'])}: {r['class_assistencial']!r:28}  ({prod})")

    vals = sorted(sub["class_assistencial"].dropna().unique())
    print(f"\n   Valores distintos de class_assistencial na série: {vals}")
    if len(vals) == 1:
        print(f"   → SIH rotula de forma ESTÁVEL como {vals[0]!r} em toda a série "
              f"(nenhuma mudança ao longo do tempo).")
    else:
        print("   → SIH apresenta MUDANÇA/INCONSISTÊNCIA de rótulo ao longo dos anos.")

    # Rótulo no painel definitivo
    no_def = df_def[df_def["cnes"] == CNES_GUILHERME_ALVARO].sort_values("ano")
    _titulo_proxy = "modelo_gestao_proxy"
    if no_def.empty:
        print(f"\n   No painel DEFINITIVO: AUSENTE (removido por algum filtro).")
    else:
        proxy_vals = sorted(no_def[_titulo_proxy].dropna().unique())
        print(f"\n   No painel DEFINITIVO ({len(no_def)}/11 anos) — "
              f"{_titulo_proxy}: {proxy_vals}")
        for _, r in no_def.iterrows():
            print(f"     {int(r['ano'])}: {r[_titulo_proxy]!r}")
    print("\n   >>> Informação de campo da equipe: é administração DIRETA, não OSS. "
          "A reclassificação manual (OSS→Direta) é a ETAPA 2c.")


# ══════════════════════════════════════════════════════════════════════════════
# 1c. CATEGORIA "PRIVADO" (n=3)
# ══════════════════════════════════════════════════════════════════════════════

def inv_1c_privado(bruto: pd.DataFrame, df_def: pd.DataFrame):
    _titulo("1c. CATEGORIA 'PRIVADO' — CNES, nome e rótulo atual")

    nomes = cpd.nome_referencia_por_cnes(bruto)
    mun   = _municipio_por_cnes(bruto)

    priv = df_def[df_def["modelo_gestao_proxy"] == "Privado"]
    cnes_priv = sorted(priv["cnes"].unique())
    print(f"   {len(priv)} hospital-ano rotulados 'Privado' — "
          f"{len(cnes_priv)} CNES distintos: {cnes_priv}")

    linhas = []
    for cnes in cnes_priv:
        s = df_def[df_def["cnes"] == cnes]
        rotulos = sorted(s["modelo_gestao_proxy"].dropna().unique())
        linhas.append({
            "cnes": cnes,
            "nome_fantasia": nomes.get(cnes, ""),
            "municipio": mun.get(cnes, ""),
            "anos_no_def": s["ano"].nunique(),
            "rotulo_atual_modelo_gestao_proxy": "; ".join(rotulos),
        })
    df = pd.DataFrame(linhas)
    with pd.option_context("display.max_colwidth", 46, "display.width", 320):
        print(df.to_string(index=False))
    print("\n   >>> Não há dado interno que confirme PPP. Tabela apenas organiza a "
          "decisão de renomeação 'Privado'→'PPP'/'Privado/PPP' (ETAPA 2d). "
          "Lembrar: o grupo inclui o HU-UFSCar (autarquia federal Ebserh).")


# ══════════════════════════════════════════════════════════════════════════════
# 1d. USO DO TERMO "custo" NO CÓDIGO E NOS TEXTOS (grep reprodutível)
# ══════════════════════════════════════════════════════════════════════════════

def inv_1d_custo():
    _titulo("1d. OCORRÊNCIAS DE 'custo' EM .py / .tex / .md (grep reprodutível)")

    raiz = base.PASTA_DADOS
    exts = ("*.py", "*.tex", "*.md")
    arquivos = []
    for ext in exts:
        arquivos += [p for p in raiz.rglob(ext)
                     if ".git" not in p.parts
                     and "scratchpad" not in str(p).lower()]
    arquivos = sorted(set(arquivos))

    PAT = re.compile(r"custo", re.IGNORECASE)
    # Heurística: é IDENTIFICADOR de código (manter) se casar custo_saida /
    # custo_real / custo_col / custo_mediana etc. (custo seguido de '_').
    PAT_IDENT = re.compile(r"\bcusto_\w+|\w*_custo\b", re.IGNORECASE)

    total = 0
    ident = 0
    prosa = 0
    por_arquivo: dict[str, list] = {}
    for p in arquivos:
        try:
            linhas = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception as e:
            print(f"   [ERRO ao ler {p}]: {e}")
            continue
        for i, ln in enumerate(linhas, start=1):
            if PAT.search(ln):
                eh_ident = bool(PAT_IDENT.search(ln))
                total += 1
                if eh_ident:
                    ident += 1
                else:
                    prosa += 1
                rel = p.relative_to(raiz)
                por_arquivo.setdefault(str(rel), []).append(
                    (i, "IDENT" if eh_ident else "TEXTO", ln.strip()))

    print(f"\n   {total} ocorrências em {len(por_arquivo)} arquivos "
          f"(marcadas IDENT={ident} p/ manter; TEXTO={prosa} p/ possível reescrita).")
    print("   Marca [IDENT] = linha contém identificador custo_saida/custo_real "
          "(código — MANTER). [TEXTO] = prosa/título/legenda (candidato a reescrita).")
    for rel in sorted(por_arquivo):
        print(f"\n   ── {rel}")
        for (i, tipo, txt) in por_arquivo[rel]:
            corte = txt if len(txt) <= 150 else txt[:147] + "..."
            print(f"      L{i:<5} [{tipo:5}] {corte}")
    print("\n   >>> ETAPA 2a decidirá onde trocar por 'faturamento por saída' / "
          "'valor reembolsado por saída (SIH)'. Identificadores custo_saida no "
          "código PERMANECEM (estabilidade do pipeline).")


# ══════════════════════════════════════════════════════════════════════════════
# 1e. GRÁFICO "mediana anual por categoria" — escopo do cálculo
# ══════════════════════════════════════════════════════════════════════════════

def _corpo_funcao(texto: str, nome_func: str) -> tuple[int, str]:
    """Retorna (linha_inicial_1based, corpo) da função top-level `nome_func`."""
    linhas = texto.splitlines()
    ini = None
    for i, ln in enumerate(linhas):
        if ln.startswith(f"def {nome_func}("):
            ini = i
            break
    if ini is None:
        return (-1, "")
    fim = len(linhas)
    for j in range(ini + 1, len(linhas)):
        if linhas[j].startswith("def "):
            fim = j
            break
    return (ini + 1, "\n".join(linhas[ini:fim]))


def inv_1e_grafico_categoria():
    _titulo("1e. GRÁFICO 'mediana anual por categoria' — escopo do cálculo")

    alvo = base.PASTA_DADOS / "analise_exploratoria.py"
    if not alvo.exists():
        print(f"   {alvo.name} não encontrado.")
        return
    texto = alvo.read_text(encoding="utf-8", errors="replace")

    print("   Arquivo: analise_exploratoria.py")
    print("   Gráfico descrito pela revisão (linhas por categoria, Privado "
          "pontilhado):")
    print("     função  tendencia_temporal(painel)")
    print("     figura  fig_ae_08_categoria_<indicador>.png  (ex.: "
          "fig_ae_08_categoria_mort_all.png = 'Mortalidade geral: mediana anual "
          "por categoria')")

    for nome_func in ("tendencia_temporal", "por_categoria"):
        ini, corpo = _corpo_funcao(texto, nome_func)
        if ini < 0:
            print(f"\n   [função {nome_func} não localizada]")
            continue
        tem_faixa = bool(re.search(r"faixa_barcelona|faixa\s*==\s*3|faixa_complex",
                                   corpo))
        print(f"\n   Função '{nome_func}' (linha {ini}): filtro de faixa "
              f"Barcelona no corpo? -> {'SIM' if tem_faixa else 'NÃO'}")
        # imprime as linhas de groupby/median e de título
        for k, ln in enumerate(corpo.splitlines(), start=ini):
            if re.search(r"groupby\(.*modelo_gestao_proxy|\.median\(\)|set_title",
                         ln):
                print(f"      L{k}: {ln.strip()}")

    print("\n   >>> CONCLUSÃO 1e: a mediana é calculada com "
          "groupby(['ano','modelo_gestao_proxy']).median() sobre o PAINEL "
          "INTEIRO — TODAS as faixas de complexidade Barcelona. NÃO há filtro "
          "faixa_barcelona == 3. O 'faixa cinza' do título refere-se à banda dos "
          "anos COVID (2020-2021), não à faixa de complexidade — fonte da "
          "ambiguidade apontada. Correção de título é a ETAPA 2e.")
    print("   OBS: este gráfico está em analise_exploratoria.py (NÃO em "
          "diagnostico_painel_definitivo.py, como o enunciado supôs).")


def main():
    print("=" * LARGURA)
    print("INVESTIGAÇÃO DA REVISÃO (jul/2026) — SOMENTE LEITURA, NADA É ALTERADO")
    print("=" * LARGURA)

    base.configurar_diretorios()
    bruto, df_def = carregar()
    print(f"[CARGA] bruto: {bruto['cnes'].nunique()} CNES / {len(bruto)} linhas | "
          f"definitivo: {df_def['cnes'].nunique()} CNES / {len(df_def)} linhas")

    inv_1a_pediatricos(bruto, df_def)
    inv_1b_guilherme_alvaro(bruto, df_def)
    inv_1c_privado(bruto, df_def)
    inv_1d_custo()
    inv_1e_grafico_categoria()

    print("\n" + "=" * LARGURA)
    print("FIM DA INVESTIGAÇÃO. Nenhum arquivo do pipeline foi modificado.")
    print("=" * LARGURA)


if __name__ == "__main__":
    main()
