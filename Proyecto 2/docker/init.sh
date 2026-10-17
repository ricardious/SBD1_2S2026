#!/usr/bin/env bash
set -euo pipefail
# Las claves se interpolan en literales T-SQL; aceptar solo caracteres seguros.
for value in "$DB_PASSWORD" "$IMPORT_DB_PASSWORD"; do
  if [[ ! "$value" =~ ^[A-Za-z0-9_!-]{16,128}$ ]]; then
    echo 'Las claves DB_PASSWORD e IMPORT_DB_PASSWORD requieren 16-128 caracteres A-Z a-z 0-9 _ ! -.' >&2
    exit 1
  fi
done
exec /opt/mssql-tools18/bin/sqlcmd -S sqlserver -U sa -C -b \
  -v DB_PASSWORD="$DB_PASSWORD" IMPORT_DB_PASSWORD="$IMPORT_DB_PASSWORD" \
  -i /bootstrap/init.sql
