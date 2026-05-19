<#
.SYNOPSIS
    Sets up GitHub OIDC federation for automated Azure deployments.
    Creates an Entra ID app registration with federated credentials
    and assigns Contributor + User Access Administrator on the subscription.

.PARAMETER GitHubOrg
    GitHub organization or username (e.g., "san360")

.PARAMETER GitHubRepo
    GitHub repository name (e.g., "ai-ticket-automation")

.PARAMETER SubscriptionId
    Azure subscription ID to grant access to

.PARAMETER Location
    Azure region (e.g., "swedencentral")

.EXAMPLE
    ./setup-github-federation.ps1 -GitHubOrg "san360" -GitHubRepo "ai-ticket-automation" -SubscriptionId "<sub-id>" -Location "swedencentral"
#>

param(
    [Parameter(Mandatory)] [string] $GitHubOrg,
    [Parameter(Mandatory)] [string] $GitHubRepo,
    [Parameter(Mandatory)] [string] $SubscriptionId,
    [Parameter(Mandatory)] [string] $Location
)

$ErrorActionPreference = "Stop"
$appName = "gh-deploy-$GitHubRepo"

Write-Host "=== GitHub OIDC Federation Setup ===" -ForegroundColor Cyan
Write-Host "App Name: $appName"
Write-Host "Repository: $GitHubOrg/$GitHubRepo"
Write-Host "Subscription: $SubscriptionId"

# 1. Create Entra ID App Registration
Write-Host "`n--- Creating App Registration ---" -ForegroundColor Yellow
$app = az ad app create --display-name $appName --query "{appId: appId, id: id}" -o json | ConvertFrom-Json
$clientId = $app.appId
$appObjectId = $app.id
Write-Host "  App ID (Client ID): $clientId"

# 2. Create Service Principal
Write-Host "`n--- Creating Service Principal ---" -ForegroundColor Yellow
$sp = az ad sp create --id $clientId --query "{id: id}" -o json | ConvertFrom-Json
$spObjectId = $sp.id
Write-Host "  Service Principal Object ID: $spObjectId"

# 3. Add Federated Credential for main branch
Write-Host "`n--- Adding Federated Credential (main branch) ---" -ForegroundColor Yellow
$fedCredMain = @{
    name        = "github-main"
    issuer      = "https://token.actions.githubusercontent.com"
    subject     = "repo:${GitHubOrg}/${GitHubRepo}:ref:refs/heads/main"
    description = "GitHub Actions - main branch"
    audiences   = @("api://AzureADTokenExchange")
} | ConvertTo-Json -Compress

az ad app federated-credential create --id $appObjectId --parameters $fedCredMain
Write-Host "  Added: main branch credential"

# 4. Add Federated Credential for pull requests
Write-Host "`n--- Adding Federated Credential (pull requests) ---" -ForegroundColor Yellow
$fedCredPR = @{
    name        = "github-pr"
    issuer      = "https://token.actions.githubusercontent.com"
    subject     = "repo:${GitHubOrg}/${GitHubRepo}:pull_request"
    description = "GitHub Actions - pull requests"
    audiences   = @("api://AzureADTokenExchange")
} | ConvertTo-Json -Compress

az ad app federated-credential create --id $appObjectId --parameters $fedCredPR
Write-Host "  Added: pull request credential"

# 5. Assign Contributor role on subscription
Write-Host "`n--- Assigning Roles ---" -ForegroundColor Yellow
az role assignment create `
    --assignee-object-id $spObjectId `
    --assignee-principal-type ServicePrincipal `
    --role "Contributor" `
    --scope "/subscriptions/$SubscriptionId" `
    --output none
Write-Host "  Assigned: Contributor"

# 6. Assign User Access Administrator (for RBAC assignments in Bicep)
az role assignment create `
    --assignee-object-id $spObjectId `
    --assignee-principal-type ServicePrincipal `
    --role "User Access Administrator" `
    --scope "/subscriptions/$SubscriptionId" `
    --output none
Write-Host "  Assigned: User Access Administrator"

# 7. Output GitHub repository variables to configure
Write-Host "`n=== Configure these GitHub Repository Variables ===" -ForegroundColor Green
Write-Host @"

  Variable Name              Value
  -------------------------  -----------------------------------------
  AZURE_CLIENT_ID            $clientId
  AZURE_TENANT_ID            $(az account show --query tenantId -o tsv)
  AZURE_SUBSCRIPTION_ID      $SubscriptionId
  AZURE_ENV_NAME             ai-ticket-automation
  AZURE_LOCATION             $Location

  Set them via GitHub UI (Settings > Secrets and variables > Actions > Variables)
  or via CLI:

    gh variable set AZURE_CLIENT_ID --body "$clientId"
    gh variable set AZURE_TENANT_ID --body "$(az account show --query tenantId -o tsv)"
    gh variable set AZURE_SUBSCRIPTION_ID --body "$SubscriptionId"
    gh variable set AZURE_ENV_NAME --body "ai-ticket-automation"
    gh variable set AZURE_LOCATION --body "$Location"

"@

Write-Host "=== Federation Setup Complete ===" -ForegroundColor Green
