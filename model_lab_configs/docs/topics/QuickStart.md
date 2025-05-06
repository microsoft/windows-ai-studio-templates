# What is model conversion
Model conversion is an integrated development environment designed to help developers and AI engineers to convert, quantize, optimize and evaluate the pre-built machine learning models on your local windows platform. It provides a simplify , end-to-end experience for working with models from sources like Hugging Face, and prepares them for efficient inference on devices powered by NPUs, GPUs and CPUs.

# What can you do in model conversion
- Create model project easily

    Start by creating a new model project using a guided template. Choose from pre-configured recipes for supported models or begin with a blank template to fully customize workflows—ideal for Hugging Face PyTorch models.0
- Run a workflow with default recipes

    Each project supports a customizable workflow that includes the everything needed for model conversion end-to-end.
- Model conversion (PyTorch to ONNX)
- Optimization and quantization (QDQ quantization for NPU acceleration with different execution providers (EPs))
- Evaluation metrics with public datasets
- Sample inference notebooks
- Exporting and sharing results
- Built-in runtime setup

    Model conversion automatically sets up a Python environment for model conversion workflow and inference, ensuring dependencies are handled per recipe.
- Track and sharing results with others

    Every run is versioned and stored in a history folder. You can re-evaluate, export or share these runs with others. 

# Prerequisites
- Snapdragon powered Copilot+ PCs running Windows 11
- 32GB+ memory
- Install VS Code extension `AI Toolkit`. Please follow https://learn.microsoft.com/en-us/windows/ai/toolkit/toolkit-getting-started?tabs=rest#install

# Create Project
Creating a project in Model Conversion is the first step toward converting, optimizing, quantizing and evaluating machine learning models . This guide walks you through the process on how to create a model project
Launch Model Conversion Open the Model Lab on the left panel. Click `Workflow`.
Start a New Project Click on “Create Project” to begin. You’ll be guided through a setup flow.
Choose a Template
Predefined Recipes : choose the base model from the supported model list such as Clip, ResNet or BERT.
Or Blank Template : Ideal for advanced users and model is not listed in base model, select from template for customizing the workflows
Enter Project Details Entering a unique Project Name and a Project Location. A new folder with the specified project name will be created in the location you selected to store the project files.
 
Notice:
Supported Models: Model Conversion currently supports a growing list of models, including top Hugging Face models in PyTorch format.
<Table of supported model name, HF PATH)
Hugging Face Compliance: If your selected model or dataset is hosted on Hugging Face, you may be prompted to accept license terms before proceeding. For xxxx dataset, you need to input your HF token to proceed. (instruction for getting the token instruction from HF) This is required to ensure legal compliance
ReadMe Access: A README file is included in each project. If you close it, you can reopen it via the workspace xxxxx


Model Conversion - Run workflow
Running a workflow in Model Conversion is the core step that transform the pre-built ML model into an optimized and quantized onnx model .  You can converting a Hugging Face PyTorch model with a pre-defined recipe. This tutorial walks you through the process on how to run a workflow.
Open Your Model Project
Xxxxxxxxxxxxxxxxxxx
Review the Workflow Configuration
Click the workflow template to view the conversion recipe.
You can edit the configuration to customize steps like:
Conversion (This step will convert your model from PyTorch into ONNX)
Quantizaiton xxxxxxxxxxx
Evaluation  
Run the Workflow
Click Run to begin the job.
A default job name will be generated using the workflow name and timestamp (e.g., bert_qdq_2025-05-06_20-45-00) for easy tracking
Track Progress
The first run may take up to 20 minutes as Model Lab installs dependencies and sets up a Python environment
A terminal view will display progress indicators to keep you informed.
View Results
Once complete, results are stored in the History tab.
You can:
View metrics and evaluation results
Export the run folder
Launch inference samples
Re-evaluate with new datasets
Notice
If your job is canceled or failed, you can click job name to view the configuration and run job again. To avoids accidental overwrites , each execution creates a new history folder with its own configuration and results.     
Compliance Alerts: If your workflow uses a gated dataset (e.g., from Hugging Face), you’ll be prompted to accept the license terms before proceeding. This is required for legal compliance (instruction for token xxxx)
Workspace Portability: All artifacts (e.g., Olive config, scripts, evaluation results) are saved in the run folder. You can export this folder to share with others or run it outside Model Lab.


History Board Help Guide
 
The History Board in Model Lab is your central dashboard for tracking, reviewing, and managing all workflow runs. Each time you run a model conversion, optimization, or evaluation, a new entry is created in the History Board—ensuring full traceability and reproducibility.
🔍 What You Can Do in the History Board
View Workflow Status
Each run is listed with a status indicator (e.g., Succeeded, Cancelled).
You can click on the status to view logs and detailed execution results 
Access Evaluation Metrics
Metrics such as accuracy, latency, and throughput are displayed alongside each run.
These are grouped with the status column for a cleaner, optimized layout 
Inspect Workflow Configuration
Click the run name to open the full configuration used for that job.
This includes the Olive config, model path, and execution provider (EP) details 
Export and Share
Use the three-dot menu under Actions to:
Export the run folder
Copy the model path
Launch inference samples 
Exported folders are portable and can be shared or reused outside Model Lab 
Re-Evaluate Models
You can re-run evaluations using different datasets or metrics directly from the History Board.
This supports iterative tuning and validation
 
Model Lab – Inference Samples Help Guide
 
After converting and optimizing your model in Model Lab, you can validate its performance and behavior using Inference Samples. This feature allows you to run sample inference directly within your local environment using the converted model and a pre-configured Python runtime.
🔄 When to Use Inference Samples
Use inference samples to:
Validate that your converted model runs correctly on your target hardware (e.g., NPU, GPU, CPU).
Compare outputs across different execution providers (EPs).
Demonstrate model behavior in a lightweight, reproducible way.
Share a working sample with teammates or integrate into a Windows app project 
🧭 How to Run Inference Samples
Navigate to the History Board
After a successful workflow run, go to the History tab in your project.
Open the Inference Sample
Click the three-dot menu next to the completed run.
Select “Inference in Samples” from the dropdown 
Choose the Python Environment
You’ll be prompted to select a Python virtual environment.
The default path is:
This environment is automatically set up by Model Lab during the first run 
Run the Sample
The sample will launch in a Jupyter notebook or script, depending on the recipe.
You can modify the input data or parameters to test different scenarios.
🧠 Tips and Best Practices
Model Compatibility: Ensure your model supports the selected EP (e.g., QNN for Qualcomm, STX for AMD, LNL for Intel).
Sample Location: Inference samples are stored alongside the run artifacts in the history folder.
Custom Inputs: You can edit the sample notebook to test with your own data.
Export and Share: Use the export option in the History Board to share the full run folder, including the inference sample 
⚠️ Known Limitations
LLM Models: Running inference for large language models (LLMs) may require high-end GPUs or cloud-based conversion. Model Lab currently supports LLMs in a limited capacity with manual steps 
Runtime Setup Time: The first-time setup of the Python environment may take up to 20 minutes. Progress indicators are shown in the terminal 

C:\Users\<your name>\.aitk\bin\model_lab_runtime\Python-CPU-win32-x64-0.0.1
 