#!/bin/bash

apt-get update && apt-get install -y cron

export DB_USER=${DB_USER:-migrator}
export DB_NAME=${DB_NAME:-migrator}
export PGPASSWORD=${PGPASSWORD:-sosiska}
export BACKUP_RETENTION_COUNT=${BACKUP_RETENTION_COUNT:-7}
export BACKUP_INTERVAL_CRON=${BACKUP_INTERVAL_CRON:-"0 * * * *"}

backup_db() {
    echo "Starting backup at $(date)"
    FILENAME="/backups/$(date +"%Y%m%d_%H%M%S").sql.gz"

    if ! /usr/bin/pg_dump -h "haproxy" -p "5432" -U "$DB_USER" -d "$DB_NAME" 2>/backups/last_pg_dump_error.log | gzip > "$FILENAME"; then
        echo "[ERROR] pg_dump failed, check /backups/last_pg_dump_error.log"
        rm -f "$FILENAME"
        echo "Exit code: $?"
        return 1
    fi

    echo "Backup completed at $(date)"
    ls -1t /backups/*.sql.gz | tail -n +$(($BACKUP_RETENTION_COUNT+1)) | xargs rm -f 2>/dev/null || true
}

echo "$BACKUP_INTERVAL_CRON /usr/local/bin/backup.sh run_backup" > /etc/cron.d/backup-cron
chmod 0644 /etc/cron.d/backup-cron

if [ "$1" != "run_backup" ]; then
    echo "Starting cron daemon..."
    cron -f &
    
    backup_db
else
    backup_db
fi

if [ "$1" != "run_backup" ]; then
    while true; do
        sleep 86400
    done
fi