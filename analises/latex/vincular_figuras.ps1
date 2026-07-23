# vincular_figuras.ps1
# ---------------------------------------------------------------------------
# Recria, apos um "git clone" em outro computador, os vinculos das pastas de
# figuras ao lado de principal.tex. As figuras SAO versionadas no repositorio
# (em analises/figuras_*), mas as pastas espelho dentro de analises/latex/ sao
# junctions locais e ficam de fora do git (ver .gitignore). Sem elas o
# pdfLaTeX/latexmk local nao acha as imagens.
#
# Uso (PowerShell, a partir da pasta analises/latex):
#     ./vincular_figuras.ps1
#
# Nao afeta o fluxo do Overleaf (la as pastas sao enviadas manualmente, ver
# LEIAME_overleaf.txt). Roda quantas vezes quiser: se o vinculo ja existir,
# apenas avisa e segue.

$ErrorActionPreference = 'Stop'
$base = $PSScriptRoot
$fonte = Join-Path $base '..'   # analises/

$pastas = @(
    'figuras_analise_exploratoria',
    'figuras_estimacao',
    'figuras_fase2',
    'figuras_selecao_entrevistas'
)

foreach ($p in $pastas) {
    $alvo   = Join-Path $base $p                 # analises/latex/figuras_*
    $origem = Join-Path $fonte $p                # analises/figuras_*

    if (-not (Test-Path $origem)) {
        Write-Warning "origem nao encontrada, pulando: $origem"
        continue
    }
    if (Test-Path $alvo) {
        Write-Host "ja existe, pulando: $p"
        continue
    }
    New-Item -ItemType Junction -Path $alvo -Target (Resolve-Path $origem) | Out-Null
    Write-Host "vinculo criado: $p -> ..\$p"
}

Write-Host ""
Write-Host "Pronto. Agora compile com: latexmk -pdf principal.tex  (ou pdflatex duas vezes)."
