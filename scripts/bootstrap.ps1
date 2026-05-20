<#
.SYNOPSIS
    One-shot bootstrap script for AI Ticket Automation.
    Detects subscription, sets up azd, provisions infrastructure, and deploys agents.

.DESCRIPTION
    Prerequisites:
      - az login (already authenticated)
      - azd installed
      - Python 3.11+ installed

.EXAMPLE
    ./scripts/bootstrap.ps1
#>

$ErrorActionPreference = "Stop"
$repoRoot = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $repoRoot

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║         AI Ticket Automation — Bootstrap                    ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ─────────────────────────────────────────────────────────────
# 1. PREREQUISITES CHECK
# ─────────────────────────────────────────────────────────────
Write-Host "=== Step 1: Checking prerequisites ===" -ForegroundColor Yellow

$tools = @("az", "azd", "python", "docker", "git")
foreach ($tool in $tools) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error "MISSING: '$tool' is not installed or not in PATH. Install it and re-run."
        exit 1
    }
}
Write-Host "  All tools found: $($tools -join ', ')" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# 2. GATHER AZURE CONTEXT
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 2: Gathering Azure context ===" -ForegroundColor Yellow

$account = az account show --query "{id:id, tenantId:tenantId, name:name}" -o json | ConvertFrom-Json
$subscriptionId = $account.id
$tenantId = $account.tenantId

Write-Host "  Subscription: $($account.name) ($subscriptionId)"
Write-Host "  Tenant:       $tenantId"
Write-Host "  Location:     swedencentral"

# ─────────────────────────────────────────────────────────────
# 3. SETUP AZD ENVIRONMENT
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 3: Configuring azd environment ===" -ForegroundColor Yellow

$envName = "ai-ticket-automation"
$existingEnvs = azd env list --output json 2>$null | ConvertFrom-Json
$envExists = $existingEnvs | Where-Object { $_.Name -eq $envName }

if (-not $envExists) {
    azd env new $envName 2>$null
    Write-Host "  Created azd environment: $envName"
} else {
    azd env select $envName 2>$null
    Write-Host "  Selected existing azd environment: $envName"
}

azd env set AZURE_LOCATION swedencentral 2>$null
azd env set AZURE_SUBSCRIPTION_ID $subscriptionId 2>$null
azd env set AZURE_ENV_NAME $envName 2>$null

# Set infra parameters explicitly (required by azd 1.23+)
azd env config set infra.parameters.environmentName $envName 2>$null
azd env config set infra.parameters.location swedencentral 2>$null

Write-Host "  Environment configured (swedencentral, $subscriptionId)" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# 4. PROVISION & DEPLOY (azd up)
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 4: Running azd up (provision + deploy) ===" -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes..." -ForegroundColor DarkGray

azd up --no-prompt
if ($LASTEXITCODE -ne 0) {
    Write-Error "azd up failed. Check the output above for errors."
    exit 1
}
Write-Host "  Infrastructure provisioned and app deployed!" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# 5. SUMMARY
# ─────────────────────────────────────────────────────────────
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                   Bootstrap Complete!                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Infrastructure:  azd up ✓ (swedencentral)                  ║
║  Agents:          Deployed via post-provision hook           ║
║                                                              ║
║  Useful commands:                                            ║
║    azd env get-values        — view all outputs             ║
║    azd monitor               — open Application Insights    ║
║    azd down                  — tear down all resources      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green
