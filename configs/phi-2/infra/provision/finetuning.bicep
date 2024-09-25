param defaultCommands array
param maximumInstanceCount int
param timeout int
param location string = resourceGroup().location

param resourceSuffix string = substring(uniqueString(resourceGroup().id), 0, 5)
param storageAccountName string = 'aistorage${resourceSuffix}'
param fileShareName string = 'aifileshare${resourceSuffix}'
param acaEnvironmentName string = 'aienv${resourceSuffix}'
param acaEnvironmentStorageName string = 'aienvstorage${resourceSuffix}'
param acaJobName string = 'aiacajob${resourceSuffix}'
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

resource acajob 'Microsoft.App/jobs@2023-11-02-preview' = {
  name: acaJobName
  location: location
  properties: {
    environmentId: environment.id
    workloadProfileName: 'GPU'
    configuration: {
      secrets: null
      triggerType: 'Manual'
      replicaTimeout: timeout
      replicaRetryLimit: 0
      manualTriggerConfig: {
        replicaCompletionCount: 1
        parallelism: 1
      }
      scheduleTriggerConfig: null
      eventTriggerConfig: null
      registries: null
    }
    template: {
      containers: [
        {
          image: 'docker.io/pytorch/pytorch:2.4.0-cuda12.4-cudnn9-runtime'
          name: acaJobName
          command: [
            '/bin/bash'
            '-c'
            defaultCommand
          ]
          resources: {
            cpu: 24
            memory: '220Gi'
          }
          volumeMounts: [
            {
              volumeName: '${fileShareName}volume'
              mountPath: '/mount'
            }
          ]
        }
      ]
      initContainers: null
      volumes: [
        {
          name: '${fileShareName}volume'
          storageType: 'AzureFile'
          storageName: envStorage.name
        }
      ]
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
output ACA_JOB_NAME string = acajob.name
output COMMANDS array = defaultCommands
