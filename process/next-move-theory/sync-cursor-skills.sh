#!/usr/bin/env bash
# Copy Codex NMT skills into .cursor/skills so Cursor can discover them.
# Safe to re-run after `nmt-upgrade` / the official installer.
# Does not delete .cursor/skills/product-hypothesis (this repo's router).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/.agents/skills"
DEST="$ROOT/.cursor/skills"

if [ ! -d "$SRC" ]; then
  echo "ERROR: $SRC is missing. Run the official NMT installer from the repo root first:" >&2
  echo "  curl -fsSL https://nextmovetheory.com/install.sh | bash" >&2
  exit 1
fi

mkdir -p "$DEST"
cp -a "$SRC/PRODUCER-CONTRACT.md" "$SRC/READABILITY-CONTRACT.md" "$DEST/"

for d in "$SRC"/nmt-*; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  rm -rf "$DEST/$name"
  cp -a "$d" "$DEST/$name"
done

echo "Synced NMT Codex skills → $DEST"
echo "Preserved (if present): $DEST/product-hypothesis"
ls -1 "$DEST"
