# ==============================================================================
# Windows PowerShell PostgreSQL डेटाबेस बॅकअप स्क्रिप्ट
# श्री देवस्थान विश्वस्त व्यवस्था
# ==============================================================================

$BackupDir = "C:\backups\temple_trust"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$DbName = "temple_trust_db"
$DbUser = "postgres"
$BackupFile = "$BackupDir\${DbName}_${Timestamp}.sql"

if (!(Test-Path -Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "डेटाबेस बॅकअप सुरू करत आहे: $DbName..."
& pg_dump -U $DbUser -h localhost -F c -b -v -f $BackupFile $DbName

if ($LASTEXITCODE -eq 0) {
    Write-Host "[यशस्वी] बॅकअप जतन झाला: $BackupFile" -ForegroundColor Green
} else {
    Write-Host "[त्रुटी] बॅकअप अयशस्वी झाला!" -ForegroundColor Red
}

# ३० दिवसांपेक्षा जुने बॅकअप हटवा
Get-ChildItem -Path $BackupDir -Filter "${DbName}_*.sql" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item
