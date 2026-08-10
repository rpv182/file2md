# Genera file2md.exe (ventana, un solo archivo)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Instalando dependencias..."
py -m pip install -r requirements.txt

Write-Host "Compilando ejecutable file2md.exe..."
py -m PyInstaller `
  --noconfirm `
  --clean `
  --onefile `
  --windowed `
  --name "file2md" `
  --collect-all pymupdf `
  --collect-all pymupdf4llm `
  --collect-all winocr `
  --collect-all ebooklib `
  --collect-all extract_msg `
  --hidden-import winrt.windows.media.ocr `
  --hidden-import winrt.windows.globalization `
  --hidden-import winrt.windows.graphics.imaging `
  --hidden-import winrt.windows.storage.streams `
  --hidden-import winrt.windows.foundation `
  --hidden-import winrt.windows.foundation.collections `
  --hidden-import docx `
  --hidden-import pptx `
  --hidden-import openpyxl `
  --hidden-import odf `
  --hidden-import striprtf `
  --hidden-import markdownify `
  --hidden-import bs4 `
  --hidden-import lxml `
  --hidden-import i18n `
  app.py

$exe = Join-Path $PSScriptRoot "dist\file2md.exe"
if (Test-Path $exe) {
  Write-Host ""
  Write-Host "Listo: $exe"
} else {
  Write-Error "No se generó el ejecutable."
}
