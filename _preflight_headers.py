# -*- coding: utf-8 -*-
"""
_preflight_headers.py
Valida cabeçalhos dos 11 arquivos SIH sem varrer linhas de dado.
Reutiliza helpers de analise_sih; main() não é chamado.
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import openpyxl

from analise_sih import (
    COLUNAS_CANONICAS,
    PASTA_DADOS,
    construir_indice_colunas,
    localizar_arquivos,
    selecionar_aba_estado,
)

arquivos_sih, path_classif, fora_padrao = localizar_arquivos(PASTA_DADOS)

print(f"Arquivos SIH encontrados : {len(arquivos_sih)}", flush=True)
print(f"Classificação            : {path_classif.name if path_classif else 'NÃO ENCONTRADA'}", flush=True)
if fora_padrao:
    print(f"Fora do padrão (ignorados): {fora_padrao}", flush=True)

print(flush=True)
print(f"{'Ano':>4}  {'Aba selecionada':30}  Resultado", flush=True)
print(f"{'-'*4}  {'-'*30}  {'-'*55}", flush=True)

erros_total = 0

for path, ano in arquivos_sih:
    # Abre em modo streaming — só vai ler o cabeçalho
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)

    # Tenta selecionar aba de estado; continua se falhar
    try:
        aba = selecionar_aba_estado(wb)
    except AssertionError as exc:
        print(f"{ano:>4}  {'???':30}  [ERRO ABA] {exc}", flush=True)
        wb.close()
        erros_total += 1
        continue

    ws = wb[aba]
    header = next(ws.iter_rows(values_only=True))
    wb.close()

    col_idx = construir_indice_colunas(header)
    ausentes = [c for c in COLUNAS_CANONICAS if c not in col_idx]

    if ausentes:
        erros_total += 1
        print(f"{ano:>4}  {aba:30}  FALTAM {len(ausentes)}: {ausentes}", flush=True)
    else:
        print(f"{ano:>4}  {aba:30}  OK ({len(col_idx)} colunas reconhecidas)", flush=True)

print(flush=True)
if erros_total == 0:
    print("Todos os 11 arquivos: cabeçalhos OK.", flush=True)
else:
    print(f"ATENÇÃO: {erros_total} arquivo(s) com problema.", flush=True)
