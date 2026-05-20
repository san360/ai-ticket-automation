<#
.SYNOPSIS
    Post-deploy script executed by azd after service deployment.
    Automates end-to-end: Foundry agent deployment, Logic App configuration, and workflow deployment.
#>

$ErrorActionPreference = "Stop"

Write-Host "`n" -NoNewline
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " AI Ticket Automation - End-to-End Deployment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# ─────────────────────────────────────────────────────────────
# Step 0: Gather environment outputs from azd
# ─────────────────────────────────────────────────────────────
Write-Host "[0/6] Gathering environment configuration..." -ForegroundColor Yellow

$env:AI_FOUNDRY_ENDPOINT = azd env get-value AI_FOUNDRY_ENDPOINT
$env:AI_PROJECT_NAME = azd env get-value AI_PROJECT_NAME
$logicAppName = azd env get-value LOGIC_APP_NAME
$resourceGroup = azd env get-value AZURE_RESOURCE_GROUP
$serviceDeskUrl = azd env get-value CONTAINER_APP_URL
$managedIdentityClientId = azd env get-value MANAGED_IDENTITY_CLIENT_ID 2>$null
$managedIdentityResourceId = azd env get-value MANAGED_IDENTITY_RESOURCE_ID 2>$null

Write-Host "  AI Foundry Endpoint : $env:AI_FOUNDRY_ENDPOINT"
Write-Host "  AI Project Name     : $env:AI_PROJECT_NAME"
Write-Host "  Logic App           : $logicAppName"
Write-Host "  Resource Group      : $resourceGroup"
Write-Host "  ServiceDesk URL     : $serviceDeskUrl"

# Validate required values
$requiredVars = @{
    "AI_FOUNDRY_ENDPOINT" = $env:AI_FOUNDRY_ENDPOINT
    "LOGIC_APP_NAME"      = $logicAppName
    "AZURE_RESOURCE_GROUP" = $resourceGroup
    "CONTAINER_APP_URL"   = $serviceDeskUrl
}
$missing = $requiredVars.GetEnumerator() | Where-Object { [string]::IsNullOrWhiteSpace($_.Value) } | ForEach-Object { $_.Key }
if ($missing) {
    Write-Host "  ERROR: Missing required values: $($missing -join ', ')" -ForegroundColor Red
    exit 1
}

# ─────────────────────────────────────────────────────────────
# Step 1: Install Python dependencies
# ─────────────────────────────────────────────────────────────
Write-Host "`n[1/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r scripts/requirements.txt --quiet 2>&1 | Out-Null
Write-Host "  Done" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# Step 2: Deploy Foundry Agents (vector store + agents)
# ─────────────────────────────────────────────────────────────
Write-Host "`n[2/6] Deploying Foundry Agents..." -ForegroundColor Yellow
python scripts/deploy-agents.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Agent deployment failed (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}
Write-Host "  Agents deployed successfully" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# Step 3: Configure Logic App environment variables
# ─────────────────────────────────────────────────────────────
Write-Host "`n[3/6] Configuring Logic App app settings..." -ForegroundColor Yellow

$outputsFile = "scripts/deployment-outputs.env"
if (-not (Test-Path $outputsFile)) {
    Write-Host "  ERROR: deployment-outputs.env not found" -ForegroundColor Red
    exit 1
}

# Parse agent deployment outputs
$deployOutputs = @{}
Get-Content $outputsFile | ForEach-Object {
    $parts = $_ -split '=', 2
    if ($parts.Count -eq 2) { $deployOutputs[$parts[0]] = $parts[1] }
}

$classifierAgentName = $deployOutputs["CLASSIFIER_AGENT_NAME"]
$messageAgentName = $deployOutputs["MESSAGE_AGENT_NAME"]
$documentAgentName = $deployOutputs["DOCUMENT_AGENT_NAME"]
$vectorStoreId = $deployOutputs["VECTOR_STORE_ID"]

$settings = @(
    "AI_FOUNDRY_ENDPOINT=$env:AI_FOUNDRY_ENDPOINT"
    "CLASSIFIER_AGENT_NAME=$classifierAgentName"
    "MESSAGE_AGENT_NAME=$messageAgentName"
    "DOCUMENT_AGENT_NAME=$documentAgentName"
    "SERVICEDESK_BASE_URL=$serviceDeskUrl"
    "VECTOR_STORE_ID=$vectorStoreId"
)
if ($managedIdentityClientId) {
    $settings += "MANAGED_IDENTITY_CLIENT_ID=$managedIdentityClientId"
}
if ($managedIdentityResourceId) {
    $settings += "MANAGED_IDENTITY_RESOURCE_ID=$managedIdentityResourceId"
}

az webapp config appsettings set `
    --name $logicAppName `
    --resource-group $resourceGroup `
    --settings @settings `
    --output none

Write-Host "  Configured settings:" -ForegroundColor Green
$settings | ForEach-Object { Write-Host "    $_" }

# ─────────────────────────────────────────────────────────────
# Step 4: Deploy Logic App Workflows
# ─────────────────────────────────────────────────────────────
Write-Host "`n[4/6] Deploying Logic App workflows..." -ForegroundColor Yellow

$logicAppSrc = Join-Path $PSScriptRoot ".." "src" "logic-app"
$zipPath = Join-Path $PSScriptRoot ".." "logic-app-deploy.zip"

# Create deployment ZIP preserving folder structure
if (Test-Path $zipPath) { Remove-Item $zipPath }

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) "logicapp-deploy-$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

Copy-Item (Join-Path $logicAppSrc "host.json") $tempDir
$workflowDirs = Get-ChildItem -Path $logicAppSrc -Directory |
    Where-Object { $_.Name -ne "workflow-designtime" }

foreach ($dir in $workflowDirs) {
    Copy-Item -Path $dir.FullName -Destination (Join-Path $tempDir $dir.Name) -Recurse
}

Compress-Archive -Path (Join-Path $tempDir "*") -DestinationPath $zipPath -Force
Remove-Item $tempDir -Recurse -Force

az logicapp deployment source config-zip `
    --name $logicAppName `
    --resource-group $resourceGroup `
    --src $zipPath `
    --output none

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ERROR: Workflow deployment failed" -ForegroundColor Red
    exit 1
}

Remove-Item $zipPath -ErrorAction SilentlyContinue
Write-Host "  Workflows deployed: $($workflowDirs.Name -join ', ')" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# Step 5: Set up Continuous Evaluation
# ─────────────────────────────────────────────────────────────
Write-Host "`n[5/6] Setting up continuous evaluation..." -ForegroundColor Yellow

$env:FOUNDRY_ENDPOINT = $env:AI_FOUNDRY_ENDPOINT
python scripts/run_evaluation.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "  WARNING: Continuous evaluation setup failed (exit code $LASTEXITCODE)" -ForegroundColor Yellow
    Write-Host "  You can retry manually: python scripts/run_evaluation.py" -ForegroundColor Yellow
} else {
    Write-Host "  Continuous evaluation configured successfully" -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────
# Step 6: Verify deployments
# ─────────────────────────────────────────────────────────────
Write-Host "`n[6/6] Verifying deployments..." -ForegroundColor Yellow

# Verify Container App is healthy
try {
    $healthResp = Invoke-WebRequest -Uri "$serviceDeskUrl/api/incidents" -Method GET -TimeoutSec 10 -ErrorAction Stop
    Write-Host "  Container App API  : OK ($($healthResp.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "  Container App API  : FAILED - $($_.Exception.Message)" -ForegroundColor Red
}

# Verify Logic App is accessible
$logicAppState = az webapp show --name $logicAppName --resource-group $resourceGroup --query "state" -o tsv
Write-Host "  Logic App State    : $logicAppState" -ForegroundColor $(if ($logicAppState -eq "Running") { "Green" } else { "Red" })

# ─────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " Deployment Complete!" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Classifier Agent  : $classifierAgentName"
Write-Host "  Message Agent     : $messageAgentName"
Write-Host "  Vector Store      : $vectorStoreId"
Write-Host "  ServiceDesk       : $serviceDeskUrl"
Write-Host "  Logic App         : $logicAppName (workflows: $($workflowDirs.Name -join ', '))"
Write-Host ""
