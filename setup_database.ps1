# Setup PostgreSQL database for Employee Management System
# Run this script from the company_portal folder

$pgBin = "C:\Program Files\PostgreSQL\18\bin\psql.exe"

if (-not (Test-Path $pgBin)) {
    Write-Host "ERROR: PostgreSQL not found at $pgBin" -ForegroundColor Red
    Write-Host "Install PostgreSQL or update the path in this script."
    exit 1
}

Write-Host ""
Write-Host "=== PostgreSQL Database Setup ===" -ForegroundColor Cyan
Write-Host "Enter the password you set for the 'postgres' user during PostgreSQL installation."
Write-Host ""

$postgresPassword = Read-Host "PostgreSQL postgres user password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword)
$PlainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
$env:PGPASSWORD = $PlainPassword

Write-Host ""
Write-Host "Step 1: Creating database and user..." -ForegroundColor Yellow

$result = & $pgBin -U postgres -h 127.0.0.1 -f "setup_database.sql" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $result -ForegroundColor Red
    Write-Host ""
    Write-Host "FAILED: Could not connect. Check your postgres password." -ForegroundColor Red
    exit 1
}
Write-Host "Database and user created." -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Granting schema permissions..." -ForegroundColor Yellow

$result = & $pgBin -U postgres -h 127.0.0.1 -d employee_management -f "setup_schema.sql" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $result -ForegroundColor Red
    exit 1
}
Write-Host "Schema permissions granted." -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Testing employee_admin connection..." -ForegroundColor Yellow

$env:PGPASSWORD = "password123"
$result = & $pgBin -U employee_admin -h 127.0.0.1 -d employee_management -c "SELECT 1 AS connected;" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $result -ForegroundColor Red
    Write-Host "FAILED: employee_admin cannot connect." -ForegroundColor Red
    exit 1
}
Write-Host "Connection test passed!" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Running Django migrations..." -ForegroundColor Yellow

python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "Migration failed. Make sure your virtual environment is activated." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next commands to run:"
Write-Host "  python manage.py createsuperuser"
Write-Host "  python manage.py runserver"
Write-Host ""
