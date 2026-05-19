@description('Name of the AI Foundry resource')
param aiFoundryName string

@description('Name of the AI Foundry project')
param aiProjectName string

@description('Location for the resource')
param location string

@description('Tags for the resource')
param tags object = {}

@description('Model deployment name')
param modelDeploymentName string

@description('Model version')
param modelVersion string

@description('Principal ID of the managed identity')
param managedIdentityPrincipalId string

// AI Foundry resource (AIServices kind)
resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: aiFoundryName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiFoundryName
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

// AI Foundry project
resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  name: aiProjectName
  parent: aiFoundry
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

// Model deployment (gpt-4.1-mini)
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: aiFoundry
  name: modelDeploymentName
  sku: {
    capacity: 10
    name: 'GlobalStandard'
  }
  properties: {
    model: {
      name: 'gpt-4.1-mini'
      format: 'OpenAI'
      version: modelVersion
    }
  }
}

// Cognitive Services OpenAI User role for managed identity on Foundry resource
resource cogServicesUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiFoundry.id, managedIdentityPrincipalId, 'Cognitive Services OpenAI User')
  scope: aiFoundry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// Cognitive Services User role for managed identity (for agent operations)
resource cogServicesContributorRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiFoundry.id, managedIdentityPrincipalId, 'Cognitive Services Contributor')
  scope: aiFoundry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68')
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output name string = aiFoundry.name
output id string = aiFoundry.id
output endpoint string = 'https://${aiFoundryName}.cognitiveservices.azure.com'
output projectName string = aiProject.name
