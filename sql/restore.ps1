# PostgreSQL Restore Script
$pgBinDir = "C:\Program Files\PostgreSQL\18\bin"
$dbName = "employee_management"
$dbUser = "employee_admin"
$env:PGPASSWORD = "Sarva@127536"
$backupFile = "c:\Users\DELL\Backend-training\Django-projects\company_portal\sql\backup.sql"

if (-not (Test-Path $backupFile)) {
    Write-Host "ERROR: Backup file $backupFile not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Restoring database $dbName from $backupFile..." -ForegroundColor Cyan
if (-not (Test-Path "$pgBinDir\psql.exe")) {
    & "psql.exe" -U $dbUser -h 127.0.0.1 -d $dbName -f $backupFile 2>&1
} else {
    & "$pgBinDir\psql.exe" -U $dbUser -h 127.0.0.1 -d $dbName -f $backupFile 2>&1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "Restore completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Restore failed!" -ForegroundColor Red
}
