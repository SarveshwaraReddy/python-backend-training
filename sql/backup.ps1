# PostgreSQL Daily Backup Script
$pgBinDir = "C:\Program Files\PostgreSQL\18\bin"
$dbName = "employee_management"
$dbUser = "employee_admin"
$env:PGPASSWORD = "Sarva@127536"
$backupFile = "c:\Users\DELL\Backend-training\Django-projects\company_portal\sql\backup.sql"

Write-Host "Starting database backup for $dbName..." -ForegroundColor Cyan
if (-not (Test-Path "$pgBinDir\pg_dump.exe")) {
    # Check if in PATH
    & "pg_dump.exe" -U $dbUser -h 127.0.0.1 -F p -b -v -f $backupFile $dbName 2>&1
} else {
    & "$pgBinDir\pg_dump.exe" -U $dbUser -h 127.0.0.1 -F p -b -v -f $backupFile $dbName 2>&1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup completed successfully! Saved to $backupFile" -ForegroundColor Green
} else {
    Write-Host "Backup failed!" -ForegroundColor Red
}
