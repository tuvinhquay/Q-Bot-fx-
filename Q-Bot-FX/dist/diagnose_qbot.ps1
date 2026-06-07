Write-Host ""
Write-Host "==============================="
Write-Host "Q-BOT-FX DIAGNOSTIC SCANNER"
Write-Host "==============================="
Write-Host ""

Write-Host "[1] Current Folder"
pwd

Write-Host ""
Write-Host "[2] Python Version"
python --version

Write-Host ""
Write-Host "[3] Environment File"
if(Test-Path ".env"){
    Write-Host ".env FOUND"
    Get-Content .env
}
else{
    Write-Host ".env NOT FOUND"
}

Write-Host ""
Write-Host "[4] Required Folders"

$dataFolders=@("data","logs","backups","runtime")

foreach($f in $dataFolders){
    if(Test-Path $f){
        Write-Host "$f OK"
    }
    else{
        Write-Host "$f MISSING"
    }
}

Write-Host ""
Write-Host "[5] MT5 Check"

python -c "import MetaTrader5 as mt5;print(mt5.initialize());print(mt5.account_info())"

Write-Host ""
Write-Host "[6] Device Health"

python -c "from backend.services.device.device_health import get_device_health;print(get_device_health().to_dict())"

Write-Host ""
Write-Host "[7] Startup Check"

python backend/main.py --once

Write-Host ""
Write-Host "[8] Search LOGGER Errors"

Get-ChildItem backend -Recurse -Filter *.py |
Select-String "LOGGER\." |
ForEach-Object {
    $_.Path + ":" + $_.LineNumber + " -> " + $_.Line
}

Write-Host ""
Write-Host "[9] Search Runtime Checker"

Get-ChildItem backend -Recurse -Filter *.py |
Select-String "check_runtime_environment"

Write-Host ""
Write-Host "[10] Build Files"

if(Test-Path "QBotFX.spec"){
    Write-Host "SPEC FOUND"
}
else{
    Write-Host "SPEC MISSING"
}

if(Test-Path "dist\QBotFX.exe"){
    Write-Host "EXE FOUND"
}
else{
    Write-Host "EXE MISSING"
}

Write-Host ""
Write-Host "==============================="
Write-Host "SCAN COMPLETE"
Write-Host "==============================="