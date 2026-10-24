#!/usr/bin/env bash
file_path=$(jq -r '.tool_input.file_path // empty')

case "$(basename "$file_path")" in
  .env.blueprint) exit 0 ;;
  .env | .env.*)
    echo "Blocked: do not edit $file_path. Change the matching .env.blueprint template instead and tell the developer which values to set." >&2
    exit 2
    ;;
esac

exit 0
