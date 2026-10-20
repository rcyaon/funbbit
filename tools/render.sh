#!/usr/bin/env bash
# Render docs/renders/{top,bottom,iso}.png from eda/eda.kicad_pcb with KiCad 10.
#
# The library 3D models of J1/J2 (SJ-3523-SMT) and BT1 (Keystone 3034) are
# rotated 180 degrees relative to their footprints, so this renders from a temp
# copy of the board with those models turned around. The design files are not touched.
set -euo pipefail

cd "$(dirname "$0")/.."
KICAD_CLI="${KICAD_CLI:-$(command -v kicad-cli || echo /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli)}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/eda" docs/renders
cp eda/eda.kicad_pcb eda/eda.kicad_pro eda/fp-lib-table "$tmp/eda/"

python3 -I - "$tmp/eda/eda.kicad_pcb" <<'EOF'
import re, sys
path = sys.argv[1]
s = open(path).read()
s, n = re.subn(
    r'(\(model "kicad-embed://(?:SJ-3523-SMT|Keystone_3034)\.step"\s*'
    r'\(offset\s*\(xyz[^)]*\)\s*\)\s*\(scale\s*\(xyz[^)]*\)\s*\)\s*\(rotate\s*)'
    r'\(xyz 0 0 0\)',
    r'\1(xyz 0 0 180)', s)
if n != 3:
    sys.exit(f"expected 3 models to rotate (J1, J2, BT1), found {n}")
open(path, "w").write(s)
EOF

opts=(--quality high -w 1600 -h 1200 --zoom 0.9 --use-board-stackup-colors)
pcb="$tmp/eda/eda.kicad_pcb"
"$KICAD_CLI" pcb render "$pcb" -o docs/renders/top.png    --side top    "${opts[@]}"
"$KICAD_CLI" pcb render "$pcb" -o docs/renders/bottom.png --side bottom "${opts[@]}"
"$KICAD_CLI" pcb render "$pcb" -o docs/renders/iso.png    --rotate '-45,0,45' --perspective "${opts[@]}"
