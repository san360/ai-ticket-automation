<#
.SYNOPSIS
    One-shot bootstrap script for AI Ticket Automation.
    Detects subscription, sets up azd, provisions infrastructure, deploys agents,
    configures GitHub federation, and sets repo variables — all automatically.

.DESCRIPTION
    Prerequisites:
      - az login (already authenticated)
      - gh auth login (GitHub CLI authenticated)
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

$tools = @("az", "azd", "gh", "python", "docker", "git")
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
# 3. GATHER GITHUB CONTEXT
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 3: Gathering GitHub context ===" -ForegroundColor Yellow

$remoteUrl = git remote get-url origin
if ($remoteUrl -match "github\.com[:/]([^/]+)/([^/.]+)") {
    $gitHubOrg = $Matches[1]
    $gitHubRepo = $Matches[2]
} else {
    Write-Error "Cannot parse GitHub org/repo from remote: $remoteUrl"
    exit 1
}
Write-Host "  Repository: $gitHubOrg/$gitHubRepo"

# Verify repo exists
$repoCheck = gh repo view "$gitHubOrg/$gitHubRepo" --json name 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Repo not found. Creating..." -ForegroundColor Yellow
    gh repo create "$gitHubOrg/$gitHubRepo" --public --source . --push
} else {
    Write-Host "  Repo exists: $gitHubOrg/$gitHubRepo" -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────
# 4. PUSH LATEST CODE
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 4: Pushing latest code ===" -ForegroundColor Yellow

$hasChanges = git status --porcelain
if ($hasChanges) {
    git add -A
    git commit -m "chore: bootstrap setup" --allow-empty
    Write-Host "  Committed pending changes"
}
git push origin main 2>&1 | Out-Null
Write-Host "  Code pushed to origin/main" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# 5. SETUP AZD ENVIRONMENT
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 5: Configuring azd environment ===" -ForegroundColor Yellow

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
# 6. PROVISION & DEPLOY (azd up)
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 6: Running azd up (provision + deploy) ===" -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes..." -ForegroundColor DarkGray

azd up --no-prompt
if ($LASTEXITCODE -ne 0) {
    Write-Error "azd up failed. Check the output above for errors."
    exit 1
}
Write-Host "  Infrastructure provisioned and app deployed!" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# 7. SETUP GITHUB OIDC FEDERATION
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 7: Setting up GitHub OIDC federation ===" -ForegroundColor Yellow

$appName = "gh-deploy-$gitHubRepo"

# Check if app registration already exists
$existingApp = az ad app list --display-name $appName --query "[0].{appId:appId, id:id}" -o json 2>$null | ConvertFrom-Json
if ($existingApp -and $existingApp.appId) {
    $clientId = $existingApp.appId
    $appObjectId = $existingApp.id
    Write-Host "  App registration exists: $clientId"
} else {
    $app = az ad app create --display-name $appName --query "{appId: appId, id: id}" -o json | ConvertFrom-Json
    $clientId = $app.appId
    $appObjectId = $app.id
    Write-Host "  Created app registration: $clientId"
}

# Ensure service principal exists
$existingSp = az ad sp list --filter "appId eq '$clientId'" --query "[0].id" -o tsv 2>$null
if (-not $existingSp) {
    $sp = az ad sp create --id $clientId --query "{id: id}" -o json | ConvertFrom-Json
    $spObjectId = $sp.id
    Write-Host "  Created service principal: $spObjectId"
} else {
    $spObjectId = $existingSp
    Write-Host "  Service principal exists: $spObjectId"
}

# Add federated credentials (skip if already exists)
$existingCreds = az ad app federated-credential list --id $appObjectId --query "[].name" -o json | ConvertFrom-Json

if ("github-main" -notin $existingCreds) {
    $fedCredMain = @{
        name        = "github-main"
        issuer      = "https://token.actions.githubusercontent.com"
        subject     = "repo:${gitHubOrg}/${gitHubRepo}:ref:refs/heads/main"
        description = "GitHub Actions - main branch"
        audiences   = @("api://AzureADTokenExchange")
    } | ConvertTo-Json -Compress
    az ad app federated-credential create --id $appObjectId --parameters $fedCredMain --output none
    Write-Host "  Added federated credential: main branch"
} else {
    Write-Host "  Federated credential (main) already exists"
}

if ("github-pr" -notin $existingCreds) {
    $fedCredPR = @{
        name        = "github-pr"
        issuer      = "https://token.actions.githubusercontent.com"
        subject     = "repo:${gitHubOrg}/${gitHubRepo}:pull_request"
        description = "GitHub Actions - pull requests"
        audiences   = @("api://AzureADTokenExchange")
    } | ConvertTo-Json -Compress
    az ad app federated-credential create --id $appObjectId --parameters $fedCredPR --output none
    Write-Host "  Added federated credential: pull requests"
} else {
    Write-Host "  Federated credential (PR) already exists"
}

# Assign roles (idempotent)
az role assignment create `
    --assignee-object-id $spObjectId `
    --assignee-principal-type ServicePrincipal `
    --role "Contributor" `
    --scope "/subscriptions/$subscriptionId" `
    --output none 2>$null
az role assignment create `
    --assignee-object-id $spObjectId `
    --assignee-principal-type ServicePrincipal `
    --role "User Access Administrator" `
    --scope "/subscriptions/$subscriptionId" `
    --output none 2>$null
Write-Host "  Roles assigned (Contributor + User Access Administrator)" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────
# 8. SET GITHUB REPOSITORY VARIABLES
# ─────────────────────────────────────────────────────────────
Write-Host "`n=== Step 8: Configuring GitHub repository variables ===" -ForegroundColor Yellow

gh variable set AZURE_CLIENT_ID --body $clientId --repo "$gitHubOrg/$gitHubRepo"
gh variable set AZURE_TENANT_ID --body $tenantId --repo "$gitHubOrg/$gitHubRepo"
gh variable set AZURE_SUBSCRIPTION_ID --body $subscriptionId --repo "$gitHubOrg/$gitHubRepo"
gh variable set AZURE_ENV_NAME --body $envName --repo "$gitHubOrg/$gitHubRepo"
gh variable set AZURE_LOCATION --body "swedencentral" --repo "$gitHubOrg/$gitHubRepo"
gh variable set GPT_DEPLOYMENT --body "gpt-4.1-mini" --repo "$gitHubOrg/$gitHubRepo"

Write-Host "  GitHub variables configured:" -ForegroundColor Green
Write-Host "    AZURE_CLIENT_ID        = $clientId"
Write-Host "    AZURE_TENANT_ID        = $tenantId"
Write-Host "    AZURE_SUBSCRIPTION_ID  = $subscriptionId"
Write-Host "    AZURE_ENV_NAME         = $envName"
Write-Host "    AZURE_LOCATION         = swedencentral"
Write-Host "    GPT_DEPLOYMENT         = gpt-4.1-mini"

# ─────────────────────────────────────────────────────────────
# 9. SUMMARY
# ─────────────────────────────────────────────────────────────
Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                   Bootstrap Complete!                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Infrastructure:  azd up ✓ (swedencentral)                  ║
║  Agents:          Deployed via post-provision hook           ║
║  GitHub:          OIDC federation + repo variables ✓        ║
║  CI/CD:           Push to main triggers auto-deploy         ║
║                                                              ║
║  Useful commands:                                            ║
║    azd env get-values        — view all outputs             ║
║    azd monitor               — open Application Insights    ║
║    azd down                  — tear down all resources      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Green
