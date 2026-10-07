#!/usr/bin/env bash
# Konwersja docs/*.md -> docs/pdf/*.pdf (pandoc -> HTML -> Chromium headless).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-/opt/pw-browsers/chromium-1194/chrome-linux/chrome}"
TMP="${TMPDIR:-/tmp}/md2pdf.$$"; mkdir -p "$TMP" "$ROOT/docs/pdf"
for md in "$@"; do
  base="$(basename "${md%.md}")"
  pandoc "$md" -f gfm -t html5 -s --metadata title="$base" -c "file://$ROOT/tools/style.css" -o "$TMP/$base.html"
  "$CHROME" --headless=new --no-sandbox --disable-gpu --allow-file-access-from-files \
    --no-pdf-header-footer --print-to-pdf="$ROOT/docs/pdf/$base.pdf" "file://$TMP/$base.html" >/dev/null 2>&1
  echo "PDF: docs/pdf/$base.pdf"
done
rm -rf "$TMP"
