import argparse
import sys
import json
from utils import get_aml_client, create_dataset
from azure.ai.ml.entities import Environment, BuildContext
import re

from olive.workflows import run as olive_run
import os
import argparse
import sys

def parse_aml_config(aml_config):
    """Parse the AML config to make sure the required fields are present"""
    with open(aml_config, 'r') as file:
        aml_config = json.load(file)
    
    try:
        subscription_id = aml_config["subscription_id"]
        resource_group = aml_config["resource_group"]
        workspace_name = aml_config["workspace_name"]
        aml_compute_name = aml_config["aml_compute_name"]        
    except KeyError as e:
        print(f"KeyError: {e} not found in aml_config.json")
        sys.exit(1)

    return aml_config


def main():
    """Main function of the script."""

    # input and output arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--azure", required=False, action="store_true", help="runs the training on azure when this option is enabled")
    parser.add_argument("--aml_config", type=str, required='--azure' in sys.argv, help="aml config (update and use aml_config.json) for azure subscription/workspace details")

    args = parser.parse_args()

    # Run olive from file locally
    if not args.azure:
        file_path = os.path.join(os.getcwd(), 'finetuning/olive-config.json')
        olive_run(file_path)
    else:
        dataset_local_path = "dataset/dataset-classification.jsonl"
        dataset_name = "phi2_train_dataset"
        dataset_version = "1"
        docker_context_path = "finetuning/docker-contexts/wais_phi2_env"
        azure_olive_config_template_path = "finetuning/olive-config-azureml_template.json"
        azure_olive_config_path = "finetuning/olive-config-azureml.json"
        azure_environment_name = "wais_phi2_env"
            
        aml_config = parse_aml_config(args.aml_config)
        # Get the AML client
        ml_client = get_aml_client(aml_config["subscription_id"], aml_config["resource_group"], aml_config["workspace_name"])
        
        # Create the environment
        print("Creating the environment...")
        env_docker_context = Environment(
            build=BuildContext(path=docker_context_path),    # Path to the Docker context
            name=azure_environment_name,
            description="Environment created from a Docker context for training phi2 model using Olive.",
        )
        aml_env = ml_client.environments.create_or_update(env_docker_context)
        print("The environment {} was created successfully.".format(aml_env.name))

        # Create the dataset
        print("Creating the dataset...")

        description = "Train dataset for tone classification model."
        dataset = create_dataset(ml_client, local_path=dataset_local_path, name=dataset_name, version=dataset_version, description=description)
        print("The dataset {} was created successfully.".format(dataset.name))
        dataset_relative_path = re.split("/datastores/.*/paths/", dataset.path)[-1]

        # Update the olive-config-azureml.json
        with open(azure_olive_config_template_path, 'r') as file:
            olive_config = json.load(file)
            try:
                olive_config["azureml_client"]["aml_config_path"] = args.aml_config
                olive_config["data_configs"]["dataset_default_train"]["params_config"]["data_files"]["config"]["azureml_client"]["aml_config_path"] = args.aml_config
                olive_config["data_configs"]["dataset_default_train"]["params_config"]["data_files"]["config"]["relative_path"] = dataset_relative_path
                olive_config["systems"]["aml_system"]["config"]["aml_compute"] = aml_config["aml_compute_name"]
                olive_config["systems"]["aml_system"]["config"]["aml_environment_config"]["name"] = aml_env.name
                olive_config["systems"]["aml_system"]["config"]["aml_environment_config"]["version"] = aml_env.version
            except KeyError as e:
                print(f"KeyError: {e} not found in olive-config-azureml.json")
                sys.exit(1)

        with open(azure_olive_config_path, 'w') as file:
            json.dump(olive_config, file, indent=4)

        # Run olive from file for debug.
        file_path = os.path.join(os.getcwd(), azure_olive_config_path)
        olive_run(file_path)


if __name__ == "__main__":
    main()