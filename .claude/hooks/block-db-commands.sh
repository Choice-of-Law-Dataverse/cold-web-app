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

if grep -qE '(python3?|ipython|uv[[:space:]]+run)' <<<"$command" &&
  grep -qiE '(drop|truncate|alter)[[:space:]]+(table|view|materialized[[:space:]]+view|schema|database|function|index)|delete[[:space:]]+from|insert[[:space:]]+into|update[[:space:]]+[[:alnum:]_."]+[[:space:]]+set([^[:alnum:]_]|$)' <<<"$command"; then
  block "SQL that writes to the database is not allowed"
fi

exit 0
