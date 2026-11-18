#!/usr/bin/env bash
# Print always-injected agent context size and sizes of dirs that should stay out of the Cursor index.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== Always-injected context (line counts) ==="
wc -l AGENTS.md CLAUDE.md

always_on=()
for rule in .cursor/rules/*.mdc; do
  [[ -f "$rule" ]] || continue
  if awk '
    BEGIN { in_fm = 0 }
    /^---[[:space:]]*$/ {
      if (in_fm == 0) { in_fm = 1; next }
      exit
    }
    in_fm && /^alwaysApply:[[:space:]]*true[[:space:]]*$/ { found = 1 }
    END { exit(found ? 0 : 1) }
  ' "$rule"; then
    always_on+=("$rule")
  fi
done

if ((${#always_on[@]})); then
  echo
  echo "=== alwaysApply: true rules ==="
  wc -l "${always_on[@]}"
else
  echo
  echo "=== alwaysApply: true rules ==="
  echo "(none)"
fi

echo
echo "=== Dirs/files that should be ignored by Cursor index ==="
paths=(
  Next-Move-Theory-Canon
  .agents
  .claude
  NextMoveTheory-README.md
  process/next-move-theory/NextMoveTheory-README.md
  apps/zarya-tg/docs/deliverables
  apps/zarya-tg/docs/assets
)
for path in "${paths[@]}"; do
  if [[ -e "$path" ]]; then
    du -sh "$path"
  else
    printf "%s\t%s (missing)\n" "-" "$path"
  fi
done

echo
echo "=== PNG files under repo (should be covered by **/*.png) ==="
mapfile -t pngs < <(find . -path ./.git -prune -o -name '*.png' -print | sed 's|^\./||' | sort)
if ((${#pngs[@]})); then
  printf '%s\n' "${pngs[@]}"
  echo "(count: ${#pngs[@]})"
else
  echo "(none)"
fi
