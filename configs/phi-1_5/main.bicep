param location string = 'eastus'
param resourcePrefix string = 'qidoninf1'
param storageAccountName string = '${resourcePrefix}storage'
param fileShareName string = '${resourcePrefix}fileshare'
param environmentName string = '${resourcePrefix}env'
param environmentStorageName string = '${resourcePrefix}envstorage'
param volumeName string = '${resourcePrefix}volume'
param acaAppName string = '${resourcePrefix}acaapp'
param containerAppLogAnalyticsName string = '${resourcePrefix}-log'

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
  name: containerAppLogAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource environment 'Microsoft.App/managedEnvironments@2023-11-02-preview' = {
  name: environmentName
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
        workloadProfileType: 'D8'
        name: 'CPU'
        minimumCount: 1
        maximumCount: 1
      }
//      {
//        workloadProfileType: 'NC24-A100'
//        name: 'GPU'
//        minimumCount: 1
//        maximumCount: 1
//      }
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
  name: environmentStorageName
  properties: {
    azureFile: {
      accountName: storageAccount.name
      accountKey: storageAccount.listKeys().keys[0].value
      shareName: fileShare.name
      accessMode: 'ReadWrite'
    }
  }
}

resource aca 'Microsoft.App/containerApps@2023-11-02-preview' = {
  name: acaAppName
  location: location
  properties: {
    environmentId: environment.id
    workloadProfileName: 'CPU'
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
          image: 'docker.io/python'
          name: 'inference-test'
          command: [
            '/bin/bash'
            '-c'
            'cd ~; git clone https://github.com/SmallBlackHole/windows-ai-studio-templates.git; cd ./windows-ai-studio-templates; git checkout qidon-inf1; cd ./configs/phi-1_5; pip install -r ./setup/requirements1.txt; python ./inference/gradio_chat1.py'
          ]
          resources: {
            cpu: 4
            memory: '16Gi'
          }
          probes: []
          volumeMounts: [
            {
              volumeName: volumeName
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
          name: volumeName
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

output STORAGE_ACCOUNT_NAME string = storageAccount.name
output FILE_SHARE_NAME string = fileShare.name
output ENV_NAME string = environment.name
output SUBSCRIPTION_ID string = subscription().subscriptionId
output TENANT_ID string = subscription().tenantId
output RESOURCE_GROUP_NAME string = resourceGroup().name
output STORAGE_CONNECTION_STRING string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=core.windows.net'
output ACA_APP_NAME string = acaAppName
