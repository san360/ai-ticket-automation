using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'ai-ticket-automation')
param location = readEnvironmentVariable('AZURE_LOCATION', 'swedencentral')
