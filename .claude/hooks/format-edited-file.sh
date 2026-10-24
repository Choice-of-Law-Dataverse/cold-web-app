#!/usr/bin/env bash
file_path=$(jq -r '.tool_input.file_path // empty')
project_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"

case "$file_path" in
  "$project_dir"/frontend/*)
    pnpm --dir "$project_dir/frontend" exec prettier --log-level warn --ignore-unknown --write "$file_path" >/dev/null 2>&1
    ;;
  "$project_dir"/backend/*.py)
    uv run --directory "$project_dir/backend" ruff format --force-exclude "$file_path" >/dev/null 2>&1
    ;;
esac

exit 0
