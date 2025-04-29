# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# Handle to the workspace
from azure.ai.ml import MLClient

# Authentication package
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

from azure.ai.ml import command
from azure.ai.ml import Input, Output


def get_aml_client(subscription_id, resource_group_name, workspace_name):
    """
    Get an Azure Machine Learning client instance.

    Args:
        subscription_id (str): The Azure subscription ID.
        resource_group_name (str): The name of the resource group.
        workspace_name (str): The name of the Azure Machine Learning workspace.

    Returns:
        MLClient: An instance of the Azure Machine Learning client.
    """
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

    # Create and return MLClient instance
    return MLClient(credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name
        )


def create_dataset(ml_client, local_path, name, version, description=""):
    """
    Creates a data asset using the specified ML client, local path, name, version, and optional description.

    Args:
        ml_client (MLClient): The ML client used to interact with the ML service.
        local_path (str): The local path of the data asset.
        name (str): The name of the data asset.
        version (str): The version of the data asset.
        description (str, optional): The description of the data asset. Defaults to "".

    Returns:
        Dataset (Dataset): Registered dataset with the given name and version.
    """

    my_data = Data(
        name=name,
        version=version,
        description=description,
        path=local_path,
        type=AssetTypes.URI_FILE,
    )
    
    ## create data asset if it doesn't already exist:
    try:
        dataset = ml_client.data.get(name=name, version=version)
        print(
            f"Data asset already exists. Name: {dataset.name}, version: {dataset.version}"
        )
    except:
        dataset = ml_client.data.create_or_update(my_data)
        print(f"Data asset created. Name: {dataset.name}, version: {dataset.version}")

    return dataset