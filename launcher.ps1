param(
    [switch]$InstallPython,
    [switch]$InstallGit
)

$ErrorActionPreference = 'Stop'

# $PSScriptRoot/$PSCommandPath requieren PS3.0+; se calculan a mano para funcionar tambien con el PowerShell 2.0 de Windows 7
$ScriptPath = $MyInvocation.MyCommand.Path
$ScriptRoot = Split-Path -Parent $ScriptPath

Set-Location -Path $ScriptRoot

# En Windows 7/Vista no hay winget: se instala Python/Git bajando el instalador oficial directamente
try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch { }

function Test-IsLegacyOS {
    $v = [Environment]::OSVersion.Version
    return ($v.Major -lt 6) -or ($v.Major -eq 6 -and $v.Minor -le 1)
}

$IsLegacyOS = Test-IsLegacyOS
$MinMajor = 3
$MinMinor = 9
if ($IsLegacyOS) { $MinMinor = 8 }
$RepoUrl  = 'https://github.com/mvillarinos/zen-template-helper.git'
$Branch   = 'main'
$PythonWingetId = 'Python.Python.3.12'
$GitWingetId    = 'Git.Git'
# Version fija (Windows 7 ya no tiene instalador oficial de Python posterior a la serie 3.8)
$LegacyPythonUrl = 'https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe'
$ModernPythonUrl = 'https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe'
# Version fija de Git para Windows para el caso sin winget (revisar de tanto en tanto si conviene actualizarla)
$LegacyGitUrl    = 'https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe'

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-WingetAvailable {
    return [bool](Get-Command winget -ErrorAction SilentlyContinue)
}

function Update-SessionPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machinePath;$userPath"
}

function Get-PythonInfo {
    $checks = @(
        @{ File = 'py'; Args = @('-3', '--version') },
        @{ File = 'python'; Args = @('--version') }
    )
    foreach ($c in $checks) {
        if (-not (Get-Command $c.File -ErrorAction SilentlyContinue)) { continue }
        try {
            $out = & $c.File @($c.Args) 2>&1
            if ($out -match 'Python (\d+)\.(\d+)') {
                return New-Object PSObject -Property @{ Major = [int]$Matches[1]; Minor = [int]$Matches[2] }
            }
        } catch { }
    }
    return $null
}

function Update-AppShortcut {
    # Se regenera en cada ejecucion para que la ruta y el icono siempre queden correctos aunque se mueva la carpeta.
    param(
        [string]$BatPath,
        [string]$IconPath,
        [string]$ShortcutPath
    )
    try {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($ShortcutPath)
        $shortcut.TargetPath = $BatPath
        $shortcut.WorkingDirectory = Split-Path $BatPath -Parent
        $shortcut.IconLocation = "$IconPath,0"
        $shortcut.WindowStyle = 1
        $shortcut.Save()
    } catch {
        Write-Host "No se pudo crear/actualizar el acceso directo: $_" -ForegroundColor Yellow
    }
}

function Invoke-FileDownload {
    param([string]$Url, [string]$Destination)
    $webClient = New-Object Net.WebClient
    $webClient.Headers.Add('User-Agent', 'zen-template-helper-launcher')
    $webClient.DownloadFile($Url, $Destination)
}

function Install-LegacyPython {
    param([bool]$IsLegacyOS)
    $url = if ($IsLegacyOS) { $LegacyPythonUrl } else { $ModernPythonUrl }
    $installer = Join-Path $env:TEMP 'zth-python-installer.exe'
    Write-Host "Descargando Python..." -ForegroundColor Cyan
    Invoke-FileDownload -Url $url -Destination $installer
    Write-Host "Instalando Python..." -ForegroundColor Cyan
    Start-Process -FilePath $installer -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1', 'Include_test=0' -Wait
    Remove-Item $installer -Force -ErrorAction SilentlyContinue
}

function Install-LegacyGit {
    $installer = Join-Path $env:TEMP 'zth-git-installer.exe'
    Write-Host "Descargando Git..." -ForegroundColor Cyan
    Invoke-FileDownload -Url $LegacyGitUrl -Destination $installer
    Write-Host "Instalando Git..." -ForegroundColor Cyan
    Start-Process -FilePath $installer -ArgumentList '/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-' -Wait
    Remove-Item $installer -Force -ErrorAction SilentlyContinue
}

# --- Modo elevado: solo instala lo pedido y termina (no ejecuta la app como admin) ---
if ($InstallPython -or $InstallGit) {
    $useWinget = Test-WingetAvailable
    try {
        if ($useWinget) {
            if ($InstallPython) {
                Write-Host "Instalando Python..." -ForegroundColor Cyan
                winget install -e --id $PythonWingetId --scope machine --accept-source-agreements --accept-package-agreements
            }
            if ($InstallGit) {
                Write-Host "Instalando Git..." -ForegroundColor Cyan
                winget install -e --id $GitWingetId --scope machine --accept-source-agreements --accept-package-agreements
            }
        } else {
            if ($InstallPython) { Install-LegacyPython -IsLegacyOS $IsLegacyOS }
            if ($InstallGit) { Install-LegacyGit }
        }
    } catch {
        Write-Host "Fallo la instalacion: $_" -ForegroundColor Red
        exit 1
    }
    exit 0
}

Write-Host "=== Zen Template Helper - Launcher ===" -ForegroundColor Green

Update-AppShortcut -BatPath (Join-Path $ScriptRoot 'Instalacion.bat') -IconPath (Join-Path $ScriptRoot 'data\zen-icon.ico') -ShortcutPath (Join-Path $ScriptRoot 'Zen Template Helper.lnk')

# Tambien se agrega al menu de inicio del usuario actual (no requiere permisos de administrador)
$startMenuDir = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'
Update-AppShortcut -BatPath (Join-Path $ScriptRoot 'Instalacion.bat') -IconPath (Join-Path $ScriptRoot 'data\zen-icon.ico') -ShortcutPath (Join-Path $startMenuDir 'Zen Template Helper.lnk')

$pyInfo = Get-PythonInfo
$needPython = (-not $pyInfo) -or ($pyInfo.Major -lt $MinMajor) -or ($pyInfo.Major -eq $MinMajor -and $pyInfo.Minor -lt $MinMinor)
$needGit = -not (Get-Command git -ErrorAction SilentlyContinue)

if ($needPython) {
    Write-Host "No se encontro una version de Python $MinMajor.$MinMinor o superior." -ForegroundColor Yellow
}
if ($needGit) {
    Write-Host "No se encontro Git instalado." -ForegroundColor Yellow
}

if ($needPython -or $needGit) {
    $answer = Read-Host "Faltan componentes requeridos. Deseas instalarlos ahora? (s/n)"
    if ($answer -notmatch '^(s|si|y|yes)$') {
        Write-Host "Instalacion cancelada. No se puede continuar sin estos componentes." -ForegroundColor Red
        exit 1
    }

    $useWinget = Test-WingetAvailable
    if (-not $useWinget) {
        Write-Host "winget no esta disponible (comun en Windows 7). Se descargaran los instaladores oficiales de Python y Git directamente." -ForegroundColor Yellow
    }

    if (Test-IsAdmin) {
        try {
            if ($useWinget) {
                if ($needPython) {
                    Write-Host "Instalando Python..." -ForegroundColor Cyan
                    winget install -e --id $PythonWingetId --scope machine --accept-source-agreements --accept-package-agreements
                }
                if ($needGit) {
                    Write-Host "Instalando Git..." -ForegroundColor Cyan
                    winget install -e --id $GitWingetId --scope machine --accept-source-agreements --accept-package-agreements
                }
            } else {
                if ($needPython) { Install-LegacyPython -IsLegacyOS $IsLegacyOS }
                if ($needGit) { Install-LegacyGit }
            }
        } catch {
            Write-Host "Fallo la instalacion: $_" -ForegroundColor Red
            exit 1
        }
    } else {
        $installArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$ScriptPath`"")
        if ($needPython) { $installArgs += '-InstallPython' }
        if ($needGit) { $installArgs += '-InstallGit' }

        Write-Host "Se solicitaran permisos de administrador para instalar los componentes faltantes..." -ForegroundColor Cyan
        $proc = Start-Process -FilePath 'powershell.exe' -ArgumentList $installArgs -Verb RunAs -Wait -PassThru
        if ($proc.ExitCode -ne 0) {
            Write-Host "La instalacion no se completo correctamente (codigo $($proc.ExitCode))." -ForegroundColor Red
            exit 1
        }
    }

    Update-SessionPath

    $pyInfo = Get-PythonInfo
    $needPython = (-not $pyInfo) -or ($pyInfo.Major -lt $MinMajor) -or ($pyInfo.Major -eq $MinMajor -and $pyInfo.Minor -lt $MinMinor)
    $needGit = -not (Get-Command git -ErrorAction SilentlyContinue)

    if ($needPython -or $needGit) {
        Write-Host "No se pudo verificar la instalacion. Cerra esta ventana y volve a ejecutar el launcher (puede requerir reiniciar sesion de Windows para actualizar el PATH)." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Python: OK ($($pyInfo.Major).$($pyInfo.Minor)) - Git: OK" -ForegroundColor Green

# --- Conectar/actualizar el repositorio de origen (sin pedir credenciales, repo publico) ---
# git escribe mensajes normales por stderr; con ErrorActionPreference=Stop eso cortaba el bloque aunque no hubiera error real.
$previousEAP = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    if (-not (Test-Path '.git')) {
        Write-Host "Conectando el proyecto con el repositorio de origen..." -ForegroundColor Cyan
        git init | Out-Null
        git remote add origin $RepoUrl 2>&1 | Write-Host
        git fetch origin $Branch 2>&1 | Write-Host
        if ($LASTEXITCODE -ne 0) { throw "git fetch fallo (codigo $LASTEXITCODE)" }
        git checkout -B $Branch "origin/$Branch" 2>&1 | Write-Host
        if ($LASTEXITCODE -ne 0) { throw "git checkout fallo (codigo $LASTEXITCODE)" }
    } else {
        $currentUrl = (git remote get-url origin 2>$null)
        if ($currentUrl -ne $RepoUrl) {
            if ($currentUrl) {
                git remote set-url origin $RepoUrl | Out-Null
            } else {
                git remote add origin $RepoUrl | Out-Null
            }
        }
    }
    Write-Host "Buscando actualizaciones..." -ForegroundColor Cyan
    git pull origin $Branch 2>&1 | Write-Host
    if ($LASTEXITCODE -ne 0) { throw "git pull fallo (codigo $LASTEXITCODE)" }
} catch {
    Write-Host "No se pudo actualizar el proyecto (sin conexion?). Se continua con la version local." -ForegroundColor Yellow
    Write-Host "Detalle: $_" -ForegroundColor DarkYellow
} finally {
    $ErrorActionPreference = $previousEAP
}

# --- Ejecutar la aplicacion ---
Write-Host "Iniciando Zen Template Helper..." -ForegroundColor Green

$pythonExe = $null
try { $pythonExe = & py -3 -c "import sys; print(sys.executable)" 2>$null } catch { }
if (-not $pythonExe) {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { $pythonExe = $cmd.Source }
}
if (-not $pythonExe) {
    Write-Host "No se encontro el ejecutable de Python." -ForegroundColor Red
    exit 1
}

$pythonwExe = Join-Path (Split-Path $pythonExe -Parent) 'pythonw.exe'
if (-not (Test-Path $pythonwExe)) { $pythonwExe = $pythonExe }

$logPath = Join-Path $ScriptRoot 'launcher-app-error.log'
if (Test-Path $logPath) { Remove-Item $logPath -Force }

$proc = Start-Process -FilePath $pythonwExe -ArgumentList '"src\zen-template-helper.py"' -WorkingDirectory $ScriptRoot -PassThru -RedirectStandardError $logPath
Start-Sleep -Seconds 2

if ($proc.HasExited -and $proc.ExitCode -ne 0) {
    Write-Host "La aplicacion se cerro inesperadamente (codigo $($proc.ExitCode))." -ForegroundColor Red
    if ((Test-Path $logPath) -and (Get-Item $logPath).Length -gt 0) {
        Write-Host "--- Detalle del error ---" -ForegroundColor Yellow
        Get-Content $logPath | Write-Host
    }
    exit 1
}

exit 0
