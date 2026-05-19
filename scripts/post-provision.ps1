<#
.SYNOPSIS
    Post-provisioning script executed by azd after infrastructure deployment.
    Deploys Foundry agents and configures Logic App settings.
#>

$ErrorActionPreference = "Stop"

Write-Host "=== Post-Provision: Deploying Foundry Agents ===" -ForegroundColor Cyan

# Get outputs from azd
$env:AI_FOUNDRY_ENDPOINT = azd env get-value AI_FOUNDRY_ENDPOINT
$env:AI_PROJECT_NAME = azd env get-value AI_PROJECT_NAME
$logicAppName = azd env get-value LOGIC_APP_NAME
$resourceGroup = azd env get-value AZURE_RESOURCE_GROUP

Write-Host "AI Foundry Endpoint: $env:AI_FOUNDRY_ENDPOINT"
Write-Host "AI Project Name: $env:AI_PROJECT_NAME"
Write-Host "Logic App: $logicAppName"

# Install Python dependencies
Write-Host "`n--- Installing Python dependencies ---" -ForegroundColor Yellow
pip install -r scripts/requirements.txt --quiet

# Deploy agents
Write-Host "`n--- Deploying Agents ---" -ForegroundColor Yellow
python scripts/deploy-agents.py

# Read deployment outputs
$outputsFile = "scripts/deployment-outputs.env"
if (Test-Path $outputsFile) {
    $outputs = Get-Content $outputsFile | ForEach-Object {
        $parts = $_ -split '=', 2
        @{ Key = $parts[0]; Value = $parts[1] }
    }

    $vectorStoreId = ($outputs | Where-Object { $_.Key -eq "VECTOR_STORE_ID" }).Value

    # Update Logic App settings
    Write-Host "`n--- Updating Logic App Configuration ---" -ForegroundColor Yellow
    $topDeskUrl = azd env get-value CONTAINER_APP_URL

    az webapp config appsettings set `
        --name $logicAppName `
        --resource-group $resourceGroup `
        --settings "VECTOR_STORE_ID=$vectorStoreId" "TOPDESK_BASE_URL=$topDeskUrl" `
        --output none

    Write-Host "Logic App configured with VECTOR_STORE_ID and TOPDESK_BASE_URL" -ForegroundColor Green
}

Write-Host "`n=== Post-Provision Complete ===" -ForegroundColor Cyan
