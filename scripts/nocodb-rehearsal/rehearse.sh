#!/usr/bin/env bash

set -euo pipefail
umask 077

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
COMPOSE_FILE="$SCRIPT_DIR/compose.yaml"

CURRENT_NOCO_VERSION=${CURRENT_NOCO_VERSION:-0.263.8}
TARGET_NOCO_VERSION=${TARGET_NOCO_VERSION:-2026.08.2}
POSTGRES_VERSION=${POSTGRES_VERSION:-16}
POSTGRES_PORT=${POSTGRES_PORT:-5433}
NOCODB_PORT=${NOCODB_PORT:-8080}
COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-cold-nocodb-rehearsal}
NOCODB_VERSION=${NOCODB_VERSION:-$CURRENT_NOCO_VERSION}
WORK_DIR=${WORK_DIR:-"$REPO_ROOT/.context/nocodb-rehearsal"}
DUMP_FILE=${DUMP_FILE:-"$WORK_DIR/production.dump"}
RUN_ID=${RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}
REPORT_DIR="$WORK_DIR/runs/$RUN_ID"
LOCAL_DATABASE_URL="postgresql://postgres:local-rehearsal-only@127.0.0.1:${POSTGRES_PORT}/cold"
LOCAL_NOCODB_BASE_URL="http://127.0.0.1:${NOCODB_PORT}/api/v1/db/data/noco/p1q5x3pj29vkrdr"

export COMPOSE_PROJECT_NAME NOCODB_PORT NOCODB_VERSION POSTGRES_PORT POSTGRES_VERSION

usage() {
  cat <<'EOF'
Usage: rehearse.sh <command>

Commands:
  dump      Create a custom-format production dump (requires PROD_CONN)
  restore   Restore DUMP_FILE into a new isolated local PostgreSQL volume
  run       Capture current/target snapshots and execute write-path smoke tests
  target    Reuse the latest baseline snapshot and rerun only the target checks
  all       Run dump (unless DUMP_FILE exists), restore, and run
  clean     Remove only this rehearsal's local containers, network, and volume

Environment:
  PROD_CONN                 Percent-encoded PostgreSQL URI; required only by dump
  NOCODB_API_TOKEN          Optional; enables REST read/write smoke tests
  CURRENT_NOCO_VERSION      Default: 0.263.8
  TARGET_NOCO_VERSION       Default: 2026.08.2
  POSTGRES_VERSION          Default: 16
  DUMP_FILE                 Default: .context/nocodb-rehearsal/production.dump
  WORK_DIR                  Default: .context/nocodb-rehearsal
  POSTGRES_PORT             Default: 5433
  NOCODB_PORT               Default: 8080
EOF
}

compose() {
  docker compose --file "$COMPOSE_FILE" --project-name "$COMPOSE_PROJECT_NAME" "$@"
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

check_prerequisites() {
  require_command curl
  require_command diff
  require_command docker
  require_command uv
  docker info >/dev/null
  docker compose version >/dev/null
}

normalize_prod_conn() {
  PROD_CONN_INPUT=$PROD_CONN uv run --frozen --directory "$REPO_ROOT/backend" python -c '
import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

raw = os.environ["PROD_CONN_INPUT"]
parts = urlsplit(raw)
scheme = parts.scheme.split("+", 1)[0]
if scheme not in {"postgres", "postgresql"} or not parts.hostname:
    raise SystemExit("PROD_CONN must be a postgresql:// URI with percent-encoded credentials")

query = [(key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True) if key != "options"]
if not any(key == "sslmode" for key, _ in query):
    query.append(("sslmode", "require"))

print(urlunsplit((scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)))
'
}

dump_production() {
  if [[ -z ${PROD_CONN:-} ]]; then
    echo "PROD_CONN is required as a percent-encoded PostgreSQL URI." >&2
    exit 1
  fi
  if [[ -e $DUMP_FILE ]]; then
    echo "Refusing to overwrite existing dump: $DUMP_FILE" >&2
    echo "Set DUMP_FILE to a new path or remove the old dump deliberately." >&2
    exit 1
  fi

  mkdir -p "$(dirname -- "$DUMP_FILE")"
  echo "Creating read-only PostgreSQL $POSTGRES_VERSION dump at $DUMP_FILE"
  local dump_conn
  dump_conn=$(normalize_prod_conn)
  if ! docker run --rm "postgres:${POSTGRES_VERSION}" \
    pg_dump --format=custom --no-owner --no-privileges --dbname="$dump_conn" >"$DUMP_FILE.partial"; then
    unset dump_conn
    rm -f -- "$DUMP_FILE.partial"
    exit 1
  fi
  unset dump_conn
  mv -- "$DUMP_FILE.partial" "$DUMP_FILE"
}

restore_local() {
  if [[ ! -f $DUMP_FILE ]]; then
    echo "Dump file not found: $DUMP_FILE" >&2
    exit 1
  fi
  if compose ps --all --quiet | grep -q .; then
    echo "Rehearsal containers already exist. Run '$0 clean' before restoring again." >&2
    exit 1
  fi
  if docker volume inspect "${COMPOSE_PROJECT_NAME}_postgres-data" >/dev/null 2>&1; then
    echo "Rehearsal volume already exists. Run '$0 clean' before restoring again." >&2
    exit 1
  fi

  compose up --detach --build postgres
  compose exec --no-TTY postgres sh -c 'until pg_isready -U postgres -d cold; do sleep 1; done'
  echo "Restoring production copy into the isolated local database"
  compose exec --no-TTY postgres pg_restore \
    --exit-on-error \
    --no-owner \
    --no-privileges \
    --username=postgres \
    --dbname=cold <"$DUMP_FILE"
}

wait_for_nocodb() {
  local attempts=120
  local version=$1
  for ((attempt = 1; attempt <= attempts; attempt++)); do
    if curl --fail --silent "http://127.0.0.1:${NOCODB_PORT}/api/v1/version" >"$REPORT_DIR/${version}-version.json"; then
      return 0
    fi
    if [[ $(compose ps --status exited --quiet nocodb) ]]; then
      echo "NocoDB $version exited during startup." >&2
      compose logs --no-color nocodb >&2
      return 1
    fi
    if ((attempt % 10 == 0)); then
      echo "Still waiting for NocoDB $version to finish starting ($((attempt * 2))s elapsed)"
    fi
    sleep 2
  done
  echo "NocoDB $version did not become ready in time." >&2
  compose logs --no-color nocodb >&2
  return 1
}

start_nocodb() {
  local version=$1
  export NOCODB_VERSION=$version
  compose --profile nocodb up --detach --force-recreate --no-deps nocodb
  wait_for_nocodb "$version"
  compose logs --no-color nocodb >"$REPORT_DIR/${version}-nocodb.log"
}

stop_nocodb() {
  compose stop nocodb
}

verify_version() {
  local expected=$1
  local actual
  actual=$(curl --fail --silent "http://127.0.0.1:${NOCODB_PORT}/api/v1/version" | \
    uv run --frozen --directory "$REPO_ROOT/backend" python -c 'import json, sys; print(json.load(sys.stdin)["currentVersion"])')
  if [[ $actual != "$expected" ]]; then
    echo "Expected NocoDB $expected, but the container reports $actual" >&2
    exit 1
  fi
}

capture_snapshot() {
  local label=$1
  local output="$REPORT_DIR/${label}-snapshot.json"
  uv run --frozen --directory "$REPO_ROOT/backend" python scripts/nocodb_rehearsal.py snapshot \
    --database-url "$LOCAL_DATABASE_URL" \
    --output "$output"
}

run_smoke_tests() {
  local label=$1
  local -a smoke_command=(
    uv run --frozen --directory "$REPO_ROOT/backend" python scripts/nocodb_rehearsal.py smoke
    --database-url "$LOCAL_DATABASE_URL"
    --output "$REPORT_DIR/${label}-smoke.json"
  )
  if [[ -n ${NOCODB_API_TOKEN:-} ]]; then
    smoke_command+=(
      --nocodb-base-url "$LOCAL_NOCODB_BASE_URL"
      --nocodb-api-token "$NOCODB_API_TOKEN"
    )
  fi
  "${smoke_command[@]}"
}

run_rehearsal() {
  if ! compose ps --status running --quiet postgres | grep -q .; then
    echo "The rehearsal database is not running. Run '$0 restore' first." >&2
    exit 1
  fi

  mkdir -p "$REPORT_DIR"

  echo "Recording baseline with NocoDB $CURRENT_NOCO_VERSION"
  start_nocodb "$CURRENT_NOCO_VERSION"
  verify_version "$CURRENT_NOCO_VERSION"
  capture_snapshot baseline
  run_smoke_tests baseline
  stop_nocodb

  echo "Running metadata migration with NocoDB $TARGET_NOCO_VERSION"
  start_nocodb "$TARGET_NOCO_VERSION"
  verify_version "$TARGET_NOCO_VERSION"
  capture_snapshot target
  run_smoke_tests target

  if ! diff --unified "$REPORT_DIR/baseline-snapshot.json" "$REPORT_DIR/target-snapshot.json" \
    >"$REPORT_DIR/snapshot.diff"; then
    echo "NocoDB changed physical schema invariants; inspect $REPORT_DIR/snapshot.diff" >&2
    exit 1
  fi

  echo "Rehearsal passed. Reports: $REPORT_DIR"
  if [[ -z ${NOCODB_API_TOKEN:-} ]]; then
    echo "REST API smoke tests were skipped because NOCODB_API_TOKEN was not supplied."
  fi
}

latest_baseline_snapshot() {
  local candidate
  local latest=""
  for candidate in "$WORK_DIR"/runs/*/baseline-snapshot.json; do
    if [[ -f $candidate && (-z $latest || $candidate -nt $latest) ]]; then
      latest=$candidate
    fi
  done
  printf '%s\n' "$latest"
}

run_target_only() {
  if ! compose ps --status running --quiet postgres | grep -q .; then
    echo "The rehearsal database is not running. Run '$0 restore' first." >&2
    exit 1
  fi

  local baseline_snapshot
  baseline_snapshot=$(latest_baseline_snapshot)
  if [[ -z $baseline_snapshot ]]; then
    echo "No baseline snapshot found. Run '$0 run' first." >&2
    exit 1
  fi

  mkdir -p "$REPORT_DIR"
  echo "Reusing baseline snapshot: $baseline_snapshot"
  echo "Running target checks with NocoDB $TARGET_NOCO_VERSION"
  start_nocodb "$TARGET_NOCO_VERSION"
  verify_version "$TARGET_NOCO_VERSION"
  capture_snapshot target
  run_smoke_tests target

  if ! diff --unified "$baseline_snapshot" "$REPORT_DIR/target-snapshot.json" >"$REPORT_DIR/snapshot.diff"; then
    echo "NocoDB changed physical schema invariants; inspect $REPORT_DIR/snapshot.diff" >&2
    exit 1
  fi

  echo "Target rehearsal passed. Reports: $REPORT_DIR"
  if [[ -z ${NOCODB_API_TOKEN:-} ]]; then
    echo "REST API smoke tests were skipped because NOCODB_API_TOKEN was not supplied."
  fi
}

clean_local() {
  export NOCODB_VERSION=$CURRENT_NOCO_VERSION
  compose --profile nocodb down --volumes --remove-orphans
}

main() {
  check_prerequisites
  case ${1:-} in
    dump)
      dump_production
      ;;
    restore)
      restore_local
      ;;
    run)
      run_rehearsal
      ;;
    target)
      run_target_only
      ;;
    all)
      if [[ ! -f $DUMP_FILE ]]; then
        dump_production
      fi
      restore_local
      run_rehearsal
      ;;
    clean)
      clean_local
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
