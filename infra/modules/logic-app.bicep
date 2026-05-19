@description('Name of the Logic App')
param name string

@description('Location for the resource')
param location string

@description('Tags for the resource')
param tags object = {}

@description('User-Assigned Managed Identity resource ID')
param managedIdentityId string

@description('User-Assigned Managed Identity client ID')
param managedIdentityClientId string

@description('Key Vault name')
param keyVaultName string

@description('AI Foundry endpoint')
param aiFoundryEndpoint string

@description('AI Foundry project name')
param aiProjectName string

// App Service Plan (WS1) for Logic Apps Standard
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${name}-plan'
  location: location
  tags: tags
  sku: {
    name: 'WS1'
    tier: 'WorkflowStandard'
  }
  kind: 'elastic'
  properties: {
    elasticScaleEnabled: true
    maximumElasticWorkerCount: 5
  }
}

// Storage Account for Logic Apps
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: replace('st${name}', '-', '')
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// Logic App Standard
resource logicApp 'Microsoft.Web/sites@2023-12-01' = {
  name: name
  location: location
  tags: union(tags, { 'azd-service-name': 'logic-app' })
  kind: 'functionapp,workflowapp'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      netFrameworkVersion: 'v6.0'
      appSettings: [
        {
          name: 'APP_KIND'
          value: 'workflowApp'
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'node'
        }
        {
          name: 'WEBSITE_NODE_DEFAULT_VERSION'
          value: '~18'
        }
        {
          name: 'MANAGED_IDENTITY_CLIENT_ID'
          value: managedIdentityClientId
        }
        {
          name: 'KEY_VAULT_NAME'
          value: keyVaultName
        }
        {
          name: 'AI_FOUNDRY_ENDPOINT'
          value: aiFoundryEndpoint
        }
        {
          name: 'AI_PROJECT_NAME'
          value: aiProjectName
        }
      ]
    }
  }
}

output name string = logicApp.name
output id string = logicApp.id
output defaultHostName string = logicApp.properties.defaultHostName
