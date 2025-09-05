#!/bin/bash
set -e

: "${PATRONI_POSTGRESQL_DATA_DIR:?Need to set PATRONI_POSTGRESQL_DATA_DIR}"

# Ensure data directory exists and has correct permissions
if [ ! -d "$PATRONI_POSTGRESQL_DATA_DIR" ]; then
    mkdir -p "$PATRONI_POSTGRESQL_DATA_DIR"
fi

# Set correct ownership and permissions
chown -R postgres:postgres "$PATRONI_POSTGRESQL_DATA_DIR"
chmod 700 "$PATRONI_POSTGRESQL_DATA_DIR"

# Clean up any failed data directory
rm -rf "${PATRONI_POSTGRESQL_DATA_DIR}.failed" 2>/dev/null || true

# Set ownership for Patroni directories
chown -R postgres:postgres /etc/patroni /var/log/patroni /home/postgres

# Process patroni.yml template
envsubst < /etc/patroni/patroni.yml > /tmp/patroni.yml
chown postgres:postgres /tmp/patroni.yml

# Start postgres_exporter
export DATA_SOURCE_NAME="postgresql://migrator:sosiska@localhost:5432/migrator?sslmode=disable"
su-exec postgres postgres_exporter &

# Start Patroni
exec su-exec postgres patroni /tmp/patroni.yml
