param defaultCommands array
param maximumInstanceCount int
param location string = resourceGroup().location

param resourceSuffix string = substring(uniqueString(resourceGroup().id), 0, 5)
param storageAccountName string = 'aistorage${resourceSuffix}'
param fileShareName string = 'aifileshare${resourceSuffix}'
param acaEnvironmentName string = 'aienv${resourceSuffix}'
param acaEnvironmentStorageName string = 'aienvstorage${resourceSuffix}'
param acaAppName string = 'aiacaapp${resourceSuffix}'
param acaLogAnalyticsName string = 'ailog${resourceSuffix}'

var defaultCommand = join(defaultCommands, '; ')

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  name: storageAccountName
  location: location
  properties: {
    largeFileSharesState: 'Enabled'
  }
}

resource defaultFileService 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    protocolSettings: {
      smb: {}
    }
    cors: {
      corsRules: []
    }
    shareDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
  }
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-01-01' = {
  parent: defaultFileService
  name: fileShareName
  properties: {
    shareQuota: 1024
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: acaLogAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource environment 'Microsoft.App/managedEnvironments@2023-11-02-preview' = {
  name: acaEnvironmentName
  location: location
  properties: {
    daprAIInstrumentationKey: null
    daprAIConnectionString: null
    vnetConfiguration: null
    openTelemetryConfiguration: null
    zoneRedundant: false
    customDomainConfiguration: {
      dnsSuffix: null
      certificateKeyVaultProperties: null
      certificateValue: null
      certificatePassword: null
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        workloadProfileType: 'Consumption'
        name: 'Consumption'
      }
      {
        workloadProfileType: 'NC24-A100'
        name: 'GPU'
        minimumCount: 0
        maximumCount: maximumInstanceCount
      }
    ]
    appInsightsConfiguration: null
    infrastructureResourceGroup: null
    peerAuthentication: {
      mtls: {
        enabled: false
      }
    }
  }
}

resource envStorage 'Microsoft.App/managedEnvironments/storages@2023-11-02-preview' = {
  parent: environment
  name: acaEnvironmentStorageName
  properties: {
    azureFile: {
      accountName: storageAccount.name
      accountKey: storageAccount.listKeys().keys[0].value
      shareName: fileShare.name
      accessMode: 'ReadWrite'
    }
  }
}

resource acaApp 'Microsoft.App/containerApps@2023-11-02-preview' = {
  name: acaAppName
  location: location
  properties: {
    environmentId: environment.id
    workloadProfileName: 'GPU'
    configuration: {
      secrets: null
      activeRevisionsMode: 'Single'
      ingress: {
        allowInsecure: false
        exposedPort: 0
        external: true
        targetPort: 7860
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
        transport: 'Auto'
      }
      registries: null
      dapr: null
      maxInactiveRevisions: 100
      service: null
    }
    template: {
      revisionSuffix: ''
      terminationGracePeriodSeconds: null
      containers: [
        {
          image: 'docker.io/pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime'
          name: acaAppName
          command: [
            '/bin/bash'
            '-c'
            defaultCommand
          ]
          resources: {
            cpu: 24
            memory: '220Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/'
                port: 7860
                scheme: 'HTTP'
              }
              initialDelaySeconds: 60
              periodSeconds: 10
              successThreshold: 1
              timeoutSeconds: 1
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/'
                port: 7860
                scheme: 'HTTP'
              }
              initialDelaySeconds: 60
              periodSeconds: 10
              failureThreshold: 3
            }
            {
              type: 'Startup'
              httpGet: {
                path: '/'
                port: 7860
                scheme: 'HTTP'
              }
              initialDelaySeconds: 60
              periodSeconds: 120
              failureThreshold: 10
            }
          ]
          volumeMounts: [
            {
              volumeName: '${fileShareName}volume'
              mountPath: '/mount'
            }
          ]
        }
      ]
      initContainers: null
      scale: {
        minReplicas: 1
        maxReplicas: 1
        rules: null
      }
      volumes: [
        {
          name: '${fileShareName}volume'
          storageType: 'AzureFile'
          storageName: envStorage.name
        }
      ]
      serviceBinds: null
    }
  }
  identity: {
    type: 'None'
  }
}

output SUBSCRIPTION_ID string = subscription().subscriptionId
output RESOURCE_GROUP_NAME string = resourceGroup().name
output STORAGE_ACCOUNT_NAME string = storageAccount.name
output FILE_SHARE_NAME string = fileShare.name
output ACA_APP_NAME string = acaApp.name
output ACA_APP_ENDPOINT string = acaApp.properties.configuration.ingress.fqdn
