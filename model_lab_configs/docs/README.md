# AITK Model Lab README

## FAQ

### Q: After creating a new model project, the new project's folder is not opened.
A: Please open model project folder in vscode. Model lab will load your project.

### Q: How to switch project?
A: Please close the folder in vscode. Open model projet folder you need.

### Q: It takes long time when first time running workflows?
A: This is by design. It may take 15~20 minutes for overall process, which including environment setup process. AITK model lab need to setup python environment and install dependency packages. Next time it will be much faster.

### Q: How to run inference_sample.ipynb?
A: Click **Select Kernel** at the top right of the window, then choose **Python Environment**.

Select the environment you want to use. We recommend using the Python environment we provide, located at `C:\Users\{user_name}\.aitk\bin\model_lab_runtime`. This environment already has the required dependencies installed.

The first time you run a notebook with a new kernel, you may be prompted to install **ipykernel**. Please follow the prompt to complete the installation.
