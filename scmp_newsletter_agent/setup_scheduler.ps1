# =====================================================================
# Windows Task Scheduler Setup for SCMP Daily News Digest
# Runs the orchestrator pipeline every morning at 9:00 AM local time.
# =====================================================================

$TaskName = "SCMPDailyNewsDigest"
$PythonPath = "python.exe"
$WorkingDir = "c:\Users\HP\Desktop\Coding Playground\Antigravity"
$Arguments = "-m scmp_newsletter_agent.orchestrator --send"
$TriggerTime = "09:00"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  SCMP DAILY NEWS DIGEST: WINDOWS SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Verify python is accessible
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "[OK] Python is accessible: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[Error] Python is not found in PATH. Please verify installation." -ForegroundColor Red
    Exit
}

# 2. Define Scheduler Action, Trigger, and Settings
Write-Host "Creating scheduled task actions and triggers..." -ForegroundColor Yellow

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $Arguments -WorkingDirectory $WorkingDir
$Trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime

# Ensure task runs even if on battery power
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 3. Register the Scheduled Task (Force overwrite if exists)
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force -ErrorAction Stop
    Write-Host ""
    Write-Host "[SUCCESS] Task '$TaskName' registered successfully!" -ForegroundColor Green
    Write-Host "  Schedule:  Every day at $TriggerTime AM" -ForegroundColor Green
    Write-Host "  Directory: $WorkingDir" -ForegroundColor Green
    Write-Host "  Action:    $PythonPath $Arguments" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can manage this task in 'Task Scheduler' (taskschd.msc) on Windows." -ForegroundColor Gray
} catch {
    Write-Host "[Error] Failed to register task. Please run this script in an Administrator shell." -ForegroundColor Red
    Write-Host "Details: $_" -ForegroundColor Red
}
Write-Host "=========================================================" -ForegroundColor Cyan
