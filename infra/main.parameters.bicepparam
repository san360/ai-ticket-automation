using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'ai-ticket-auto')
param location = readEnvironmentVariable('AZURE_LOCATION', 'switzerlandnorth')
