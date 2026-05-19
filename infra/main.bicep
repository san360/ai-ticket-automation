targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group')
param resourceGroupName string = ''

@description('Name of the AI Foundry resource')
param aiFoundryName string = ''

@description('Name of the AI Foundry project')
param aiProjectName string = ''

@description('Name of the Logic App')
param logicAppName string = ''

@description('Name of the Key Vault')
param keyVaultName string = ''

@description('Name of the User-Assigned Managed Identity')
param managedIdentityName string = ''

@description('Name of the Container App for ServiceDesk simulator')
param containerAppName string = ''

@description('Name of the Container Registry')
param containerRegistryName string = ''

@description('Model deployment name')
param modelDeploymentName string = 'gpt-4.1-mini'

@description('Model version')
param modelVersion string = '2025-04-14'

@description('Name of the Application Insights resource')
param appInsightsName string = ''

@description('Batch size for ticket processing')
param batchSize string = '1'

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Resource group
resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourceGroup}${environmentName}'
  location: location
  tags: tags
}

// User-Assigned Managed Identity
module identity './modules/identity.bicep' = {
  name: 'identity'
  scope: rg
  params: {
    name: !empty(managedIdentityName) ? managedIdentityName : '${abbrs.managedIdentity}${resourceToken}'
    location: location
    tags: tags
  }
}

// Key Vault
module keyVault './modules/keyvault.bicep' = {
  name: 'keyvault'
  scope: rg
  params: {
    name: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVault}${resourceToken}'
    location: location
    tags: tags
    managedIdentityPrincipalId: identity.outputs.principalId
  }
}

// Application Insights
module appInsights './modules/app-insights.bicep' = {
  name: 'app-insights'
  scope: rg
  params: {
    name: !empty(appInsightsName) ? appInsightsName : 'appi-${resourceToken}'
    location: location
    tags: tags
  }
}

// AI Foundry (Cognitive Services AIServices)
module aiFoundry './modules/ai-foundry.bicep' = {
  name: 'ai-foundry'
  scope: rg
  params: {
    aiFoundryName: !empty(aiFoundryName) ? aiFoundryName : '${abbrs.aiFoundry}${resourceToken}'
    aiProjectName: !empty(aiProjectName) ? aiProjectName : '${abbrs.aiFoundry}${resourceToken}-proj'
    location: location
    tags: tags
    modelDeploymentName: modelDeploymentName
    modelVersion: modelVersion
    managedIdentityPrincipalId: identity.outputs.principalId
    appInsightsConnectionString: appInsights.outputs.connectionString
  }
}

// Container Registry
module containerRegistry './modules/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistry}${resourceToken}'
    location: location
    tags: tags
  }
}

// Container App (ServiceDesk Simulator)
module containerApp './modules/container-app.bicep' = {
  name: 'container-app'
  scope: rg
  params: {
    name: !empty(containerAppName) ? containerAppName : '${abbrs.containerApp}${resourceToken}'
    location: location
    tags: tags
  }
}

// Logic App Standard
module logicApp './modules/logic-app.bicep' = {
  name: 'logic-app'
  scope: rg
  params: {
    name: !empty(logicAppName) ? logicAppName : '${abbrs.logicApp}${resourceToken}'
    location: location
    tags: tags
    managedIdentityId: identity.outputs.id
    managedIdentityClientId: identity.outputs.clientId
    keyVaultName: keyVault.outputs.name
    aiFoundryEndpoint: aiFoundry.outputs.endpoint
    serviceDeskBaseUrl: containerApp.outputs.url
    batchSize: batchSize
    appInsightsConnectionString: appInsights.outputs.connectionString
  }
}

// Outputs for azd
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_LOCATION string = location
output AI_FOUNDRY_NAME string = aiFoundry.outputs.name
output AI_FOUNDRY_ENDPOINT string = aiFoundry.outputs.endpoint
output AI_PROJECT_NAME string = aiFoundry.outputs.projectName
output LOGIC_APP_NAME string = logicApp.outputs.name
output KEY_VAULT_NAME string = keyVault.outputs.name
output MANAGED_IDENTITY_NAME string = identity.outputs.name
output MANAGED_IDENTITY_CLIENT_ID string = identity.outputs.clientId
output CONTAINER_APP_URL string = containerApp.outputs.url
output CONTAINER_REGISTRY_LOGIN_SERVER string = containerRegistry.outputs.loginServer
output CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name
output APPINSIGHTS_CONNECTION_STRING string = appInsights.outputs.connectionString
