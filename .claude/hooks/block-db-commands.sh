#!/usr/bin/env bash
command=$(jq -r '.tool_input.command // empty')

block() {
  echo "Blocked: $1. Only the production database exists; leave database work to the developer." >&2
  exit 2
}

if grep -qE '(^|[^[:alnum:]_-])(psql|pgcli|pg_dump|pg_restore|dropdb|createdb)([^[:alnum:]_-]|$)' <<<"$command"; then
  block "direct database clients are not allowed"
fi

if grep -qE '(^|[^[:alnum:]_-])alembic([[:space:]][^;&|]*)?[[:space:]](upgrade|downgrade|stamp)([^[:alnum:]_-]|$)' <<<"$command"; then
  block "applying or reverting migrations is not allowed"
fi

if grep -qE '(^|[^[:alnum:]_-])make([[:space:]].*)?[[:space:]](migrate-views|revert-views|migrate_suggestions|revert_migration)([^[:alnum:]_-]|$)' <<<"$command"; then
  block "migration make targets are not allowed"
fi

command_segments() {
  awk '
    heredoc != "" {
      if ($0 ~ "^[[:space:]]*" heredoc "[[:space:]]*$") heredoc = ""
      next
    }
    {
      line = $0
      if (match(line, /(^|[^<])<<-?[[:space:]]*["\x27]?[A-Za-z_][A-Za-z0-9_]*/)) {
        heredoc = substr(line, RSTART, RLENGTH)
        sub(/^[^<]?<<-?[[:space:]]*["\x27]?/, "", heredoc)
      }
      gsub(/\x27[^\x27]*\x27/, "Q", line)
      gsub(/"[^"]*"/, "Q", line)
      gsub(/&&|\|\||;|\|/, "\n", line)
      print line
    }
  ' <<<"$command"
}

read_only_search() {
  local segment first
  while IFS= read -r segment; do
    first=$(awk '{print $1}' <<<"$segment")
    case "$first" in
      "" | cd | git | grep | rg | head | tail | wc | sort | uniq | cut | echo | printf | cat | ls | sed) ;;
      *) return 1 ;;
    esac
  done < <(command_segments)
}

if ! read_only_search &&
  grep -qiE '(drop|alter)[[:space:]]+(table|view|materialized[[:space:]]+view|schema|database|function|index|type|sequence|extension|role)|truncate[[:space:]]+(table[[:space:]]+)?[[:alnum:]_."]+|delete[[:space:]]+from|insert[[:space:]]+into|update[[:space:]]+[[:alnum:]_."]+[[:space:]]+set([^[:alnum:]_]|$)' <<<"$command"; then
  block "SQL that writes to the database is not allowed"
fi

exit 0
