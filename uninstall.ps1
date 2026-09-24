$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

Write-Host "=== Zen Template Helper - Desinstalador ===" -ForegroundColor Green

$startMenuLink = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Zen Template Helper.lnk'
$localLink = Join-Path $PSScriptRoot 'Zen Template Helper.lnk'

foreach ($link in @($startMenuLink, $localLink)) {
    if (Test-Path $link) {
        Remove-Item $link -Force
        Write-Host "Eliminado: $link" -ForegroundColor Cyan
    }
}

# No se desinstalan Python ni Git: son herramientas del sistema, no parte de la app.
$answer = Read-Host "Tambien queres borrar todos los archivos de la aplicacion en esta carpeta? (s/n)"
if ($answer -match '^(s|si|y|yes)$') {
    Write-Host "Se eliminara la carpeta: $PSScriptRoot" -ForegroundColor Yellow

    # No se puede borrar la carpeta mientras este script sigue corriendo desde ella,
    # asi que se delega el borrado a un proceso aparte que arranca despues de salir.
    $cleanupScript = Join-Path $env:TEMP 'zth-uninstall-cleanup.bat'
    $lines = @(
        '@echo off',
        'timeout /t 2 /nobreak >nul',
        "rmdir /s /q ""$PSScriptRoot""",
        'del "%~f0"'
    )
    Set-Content -Path $cleanupScript -Value $lines -Encoding ASCII

    Start-Process -FilePath $cleanupScript -WindowStyle Hidden
    Write-Host "Listo. La carpeta se va a borrar en un par de segundos." -ForegroundColor Green
} else {
    Write-Host "Se dejaron los archivos de la aplicacion, solo se quitaron los accesos directos." -ForegroundColor Green
}

exit 0
