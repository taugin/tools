if ($args[0] -eq "-r") {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [INFO] Cleaning Codex processes..." -ForegroundColor Cyan

    $processes = @(Get-Process -Name "codex" -ErrorAction SilentlyContinue)

    if ($processes.Count -gt 0) {
        foreach ($process in $processes) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [KILL] PID=$($process.Id) Name=$($process.ProcessName)" -ForegroundColor Yellow
            Stop-Process -Id $process.Id -Force
        }

        Start-Sleep -Milliseconds 500
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [OK] Process cleanup completed." -ForegroundColor Green
    }
    else {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [INFO] No Codex processes found." -ForegroundColor Gray
    }

    $args = $args | Select-Object -Skip 1

    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host ""
}

$env:ALL_PROXY = "socks5h://127.0.0.1:10808"

Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [INFO] Starting Codex..." -ForegroundColor Cyan
codex @args