#!/bin/bash
# ==============================================================================
# स्वयंचलित PostgreSQL डेटाबेस बॅकअप स्क्रिप्ट (Daily Automated DB Backup)
# श्री देवस्थान विश्वस्त व्यवस्था
# ==============================================================================

BACKUP_DIR="/var/backups/temple_trust"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="temple_trust_db"
DB_USER="temple_admin"
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

# बॅकअप डिरेक्टरी तयार करा
mkdir -p ${BACKUP_DIR}

echo "[$(date)] डेटाबेस बॅकअप सुरू होत आहे: ${DB_NAME}..."

# pg_dump कॉम्प्रेशनसह
pg_dump -U ${DB_USER} -h localhost ${DB_NAME} | gzip > ${BACKUP_FILE}

if [ $? -eq 0 ]; then
    echo "[$(date)] बॅकअप यशस्वीरित्या जतन झाला: ${BACKUP_FILE}"
else
    echo "[$(date)] [त्रुटी] डेटाबेस बॅकअप अयशस्वी झाला!" >&2
    exit 1
fi

# ३० दिवसांपेक्षा जुने बॅकअप आपोआप नष्ट करा (Auto cleanup older than 30 days)
find ${BACKUP_DIR} -name "${DB_NAME}_*.sql.gz" -mtime +30 -exec rm {} \;
echo "[$(date)] जुने बॅकअप्स साफ करण्यात आले."
