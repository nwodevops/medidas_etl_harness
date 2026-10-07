param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("local", "remote")]
    [string]$Environment
)

# Cambia las variables activas de Hop copiando la plantilla elegida
# (environments/<env>.json) a project-config.json -> config.variables y
# sobreponiendo DB_ORA_DW_* y DB_MYSQL_DW_* desde docs/credenciales/<env>.txt (gitignored).
# Equivalente Windows de switch-env.sh.
# Uso: .\switch-env.ps1 local   |   .\switch-env.ps1 remote

$ErrorActionPreference = "Stop"

$root     = $PSScriptRoot
$envFile  = Join-Path $root "environments\$Environment.json"
$credFile = Join-Path $root "docs\credenciales\$Environment.txt"
$projFile = Join-Path $root "project-config.json"

if (-not (Test-Path -LiteralPath $envFile)) {
    throw "No existe la plantilla: $envFile"
}

$envCfg = Get-Content -LiteralPath $envFile -Raw | ConvertFrom-Json
$vars   = @($envCfg.variables)

function Test-Placeholder {
    param([string]$Value)
    return $null -ne $Value -and $Value -match '<[^>]+>'
}

# project-config.json puede no existir todavia (lo genera este script).
if (Test-Path -LiteralPath $projFile) {
    $proj = Get-Content -LiteralPath $projFile -Raw | ConvertFrom-Json
} else {
    $proj = [pscustomobject]@{
        metadataBaseFolder         = '${PROJECT_HOME}/metadata'
        unitTestsBasePath          = '${PROJECT_HOME}'
        dataSetsCsvFolder          = '${PROJECT_HOME}/datasets'
        enforcingExecutionInHome   = $true
        parentProjectName          = 'default'
        config                     = [pscustomobject]@{ variables = @() }
    }
}

function Get-CredBlock {
    param([string[]]$Lines)
    $wanted = @{}
    foreach ($line in $Lines) {
        $line = $line.Trim()
        if ($line -eq '' -or $line.StartsWith('#')) { continue }
        $idx = $line.IndexOf(':')
        if ($idx -lt 1) { continue }
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim()
        if ($key -in @('Host', 'Port', 'Service', 'Database', 'User', 'Password')) {
            $wanted[$key] = $val
        }
    }
    return $wanted
}

# --- Overlay Oracle (antes de #Mysql) y MySQL (desde #Mysql) ----------------
if (Test-Path -LiteralPath $credFile) {
    $all = @(Get-Content -LiteralPath $credFile)
    $split = 0
    for ($i = 0; $i -lt $all.Count; $i++) {
        if ($all[$i].Trim() -match '^#\s*mysql\b') { $split = $i; break }
    }
    if ($split -lt 1) { throw "Falta el bloque #Mysql en $credFile" }
    $ora = Get-CredBlock $all[0..($split - 1)]
    $my  = Get-CredBlock $all[$split..($all.Count - 1)]
    foreach ($k in @('Host', 'Port', 'Service', 'User', 'Password')) {
        if (-not $ora.ContainsKey($k)) { throw "Falta $k en el bloque Oracle de $credFile" }
    }
    foreach ($k in @('Host', 'Port', 'Database', 'User', 'Password')) {
        if (-not $my.ContainsKey($k)) { throw "Falta $k en el bloque Mysql de $credFile" }
    }
    $overlay = @{
        DB_ORA_DW_HOST        = $ora['Host']
        DB_ORA_DW_PORT        = $ora['Port']
        DB_ORA_DW_DATABASE    = $ora['Service']
        DB_ORA_DW_USERNAME    = $ora['User']
        DB_ORA_DW_PASSWORD    = $ora['Password']
        DB_ORA_DW_URL         = "jdbc:oracle:thin:@//$($ora['Host']):$($ora['Port'])/$($ora['Service'])"
        DB_MYSQL_DW_HOST      = $my['Host']
        DB_MYSQL_DW_PORT      = $my['Port']
        DB_MYSQL_DW_DATABASE  = $my['Database']
        DB_MYSQL_DW_USERNAME  = $my['User']
        DB_MYSQL_DW_PASSWORD  = $my['Password']
    }
    foreach ($v in $vars) {
        if ($overlay.ContainsKey($v.name)) { $v.value = $overlay[$v.name] }
    }
    Write-Host "DW Oracle: $($ora['Host']):$($ora['Port'])/$($ora['Service']) user=$($ora['User'])"
    Write-Host "DW MySQL: $($my['Host']):$($my['Port'])/$($my['Database']) user=$($my['User'])"
} else {
    Write-Warning "No existe $credFile; DB_ORA_DW_* y DB_MYSQL_DW_* quedan con los placeholders de la plantilla."
}

# --- No pisar valores reales ya presentes si la plantilla trae placeholders --
$existing = @{}
foreach ($v in @($proj.config.variables)) {
    if ($v.name -and -not $existing.ContainsKey($v.name)) { $existing[$v.name] = $v }
}
$merged = foreach ($v in $vars) {
    if ((Test-Placeholder $v.value) -and $existing.ContainsKey($v.name) -and
        -not (Test-Placeholder $existing[$v.name].value)) {
        [pscustomobject]@{
            name        = $v.name
            value       = $existing[$v.name].value
            description = $v.description
        }
    } else {
        [pscustomobject]@{
            name        = $v.name
            value       = $v.value
            description = $v.description
        }
    }
}
$proj.config.variables = @($merged)

$json = $proj | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($projFile, $json, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Entorno activo: $Environment (variables copiadas a project-config.json)"
