param(
    [switch]$InstallPython,
    [switch]$InstallGit
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

$MinMajor = 3
$MinMinor = 9
$RepoUrl  = 'https://github.com/mvillarinos/zen-template-helper.git'
$Branch   = 'main'
$PythonWingetId = 'Python.Python.3.12'
$GitWingetId    = 'Git.Git'

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
                return [PSCustomObject]@{ Major = [int]$Matches[1]; Minor = [int]$Matches[2] }
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

# --- Modo elevado: solo instala lo pedido y termina (no ejecuta la app como admin) ---
if ($InstallPython -or $InstallGit) {
    if (-not (Test-WingetAvailable)) {
        Write-Host "winget no esta disponible en este equipo. Instala Python y/o Git manualmente." -ForegroundColor Red
        exit 1
    }
    if ($InstallPython) {
        Write-Host "Instalando Python..." -ForegroundColor Cyan
        winget install -e --id $PythonWingetId --scope machine --accept-source-agreements --accept-package-agreements
    }
    if ($InstallGit) {
        Write-Host "Instalando Git..." -ForegroundColor Cyan
        winget install -e --id $GitWingetId --scope machine --accept-source-agreements --accept-package-agreements
    }
    exit 0
}

Write-Host "=== Zen Template Helper - Launcher ===" -ForegroundColor Green

Update-AppShortcut -BatPath (Join-Path $PSScriptRoot 'Instalación.bat') -IconPath (Join-Path $PSScriptRoot 'data\zen-icon.ico') -ShortcutPath (Join-Path $PSScriptRoot 'Zen Template Helper.lnk')

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
    if (-not (Test-WingetAvailable)) {
        Write-Host "winget no esta disponible. Instala Python (python.org) y Git (git-scm.com) manualmente y volve a ejecutar el launcher." -ForegroundColor Red
        exit 1
    }

    if (Test-IsAdmin) {
        if ($needPython) {
            Write-Host "Instalando Python..." -ForegroundColor Cyan
            winget install -e --id $PythonWingetId --scope machine --accept-source-agreements --accept-package-agreements
        }
        if ($needGit) {
            Write-Host "Instalando Git..." -ForegroundColor Cyan
            winget install -e --id $GitWingetId --scope machine --accept-source-agreements --accept-package-agreements
        }
    } else {
        $installArgs = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"")
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
try {
    if (-not (Test-Path '.git')) {
        Write-Host "Conectando el proyecto con el repositorio de origen..." -ForegroundColor Cyan
        git init | Out-Null
        git remote add origin $RepoUrl 2>$null
        git fetch origin $Branch 2>&1 | Write-Host
        git checkout -B $Branch "origin/$Branch" 2>&1 | Write-Host
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
} catch {
    Write-Host "No se pudo actualizar el proyecto (sin conexion?). Se continua con la version local." -ForegroundColor Yellow
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

Start-Process -FilePath $pythonwExe -ArgumentList '"src\zen-template-helper.py"' -WorkingDirectory $PSScriptRoot
exit 0
