# Create Dataset for AI Toolkit

This guide provides instructions on how to generate a basic dataset for an AI toolkit in the VS Code dataset format.

## Overview

This repository contains code to help you create a dataset for fine-tuning and evaluating AI models. The dataset will be formatted to be compatible with AI toolkits used within Visual Studio Code.

## Sample Dataset File

A sample dataset for the AI toolkit is provided in the `dataset.jsonl` file. You can use this as a reference for formatting your own dataset.

## Sample Dataset Creation Script

1. **Prerequisites**

   Before you begin, ensure you have the following installed:

   - Python 3.x
   - Python Dependencies in `requirements.txt`

      ```sh
      pip install -r requirements.txt
      ```

1. **Add Your Custom Data Generation Logic**:

    Replace the sample code in `create_dataset.py` with your custom data generation logic.

1. **Generate the Dataset**:

    To create a synthetic dataset, run the `create_dataset.py` script:

    ```sh
    python create_dataset.py
    ```
