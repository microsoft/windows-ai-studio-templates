# Setup environment
We recommend installing env in a [virtual environment](https://docs.python.org/3/library/venv.html) or a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

Note: if you want to do inference on NPU devices with QNN EP, we recommend use [virtual environment](https://docs.python.org/3/library/venv.html). It is because inference with some model may need `arm` version python, while conda has not supported creating an arm version python venv yet.

- CPU: [Setup CPU environment](#setup-cpu-environment)
- QNN: [Setup QNN environment](#setup-qnn-environment)
- AMD: [Setup AMD environment](#setup-amd-environment)
- Intel: [Setup Intel environment](#setup-intel-environment)

## Setup CPU environment
Tips: you can directly setup NPU environment such as [Setup QNN environment](#setup-qnn-environment). It will fallback to CPU EP when process.

Alternatively, you can choose to setup a CPU environment.

Python version: 3.12.9

pip install the requirements:
```
olive-ai==0.8.0
numpy==2.2.4
onnx==1.17.0
onnxscript==0.2.3
optuna==4.2.1
pandas==2.2.3
protobuf==3.20.3
pydantic==2.11.1
pyyaml==6.0.2
torch==2.6.0
torchmetrics==1.7.0
transformers==4.50.3
tabulate==0.9.0
datasets==3.5.0
aiohttp==3.11.16
dill==0.3.8
filelock==3.18.0
fsspec==2024.12.0
huggingface-hub==0.30.1
multiprocess==0.70.16
numpy==2.2.4
packaging==24.2
pandas==2.2.3
pyarrow==19.0.1
pyyaml==6.0.2
requests==2.32.3
tqdm==4.67.1
xxhash==3.5.0
ipykernel==6.29.5
comm==0.2.2
debugpy==1.8.13
ipython==9.0.2
jupyter_client==8.6.3
jupyter_core==5.7.2
matplotlib-inline==0.1.7
nest-asyncio==1.6.0
packaging==24.2
psutil==7.0.0
pyzmq==26.3.0
tornado==6.4.2
traitlets==5.14.3
ipywidgets==8.1.5
comm==0.2.2
ipython==9.0.2
jupyterlab_widgets==3.0.13
traitlets==5.14.3
widgetsnbextension==4.0.13
onnxruntime==1.21.0
coloredlogs==15.0.1
flatbuffers==25.2.10
numpy==2.2.4
packaging==24.2
protobuf==3.20.3
sympy==1.13.1
```

## Setup QNN environment
Python version: 3.12.9

pip install the requirements:
```
olive-ai==0.8.0
numpy==2.2.4
onnx==1.17.0
onnxscript==0.2.3
optuna==4.2.1
pandas==2.2.3
protobuf==3.20.3
pydantic==2.11.1
pyyaml==6.0.2
torch==2.6.0
torchmetrics==1.7.0
transformers==4.50.3
tabulate==0.9.0
datasets==3.5.0
aiohttp==3.11.16
dill==0.3.8
filelock==3.18.0
fsspec==2024.12.0
huggingface-hub==0.30.1
multiprocess==0.70.16
numpy==2.2.4
packaging==24.2
pandas==2.2.3
pyarrow==19.0.1
pyyaml==6.0.2
requests==2.32.3
tqdm==4.67.1
xxhash==3.5.0
ipykernel==6.29.5
comm==0.2.2
debugpy==1.8.13
ipython==9.0.2
jupyter_client==8.6.3
jupyter_core==5.7.2
matplotlib-inline==0.1.7
nest-asyncio==1.6.0
packaging==24.2
psutil==7.0.0
pyzmq==26.3.0
tornado==6.4.2
traitlets==5.14.3
ipywidgets==8.1.5
comm==0.2.2
ipython==9.0.2
jupyterlab_widgets==3.0.13
traitlets==5.14.3
widgetsnbextension==4.0.13
onnxruntime-qnn==1.20.2
```

## Setup AMD environment
Python version: 3.10.9
```
```

## Setup Intel environment
Python version: 3.10.9

pip install the requirements:
```
olive-ai==0.8.0
numpy==2.2.4
onnx==1.17.0
onnxscript==0.2.3
optuna==4.2.1
pandas==2.2.3
protobuf==3.20.3
pydantic==2.11.1
pyyaml==6.0.2
torch==2.6.0
torchmetrics==1.7.0
transformers==4.50.3
tabulate==0.9.0
datasets==3.5.0
aiohttp==3.11.16
dill==0.3.8
filelock==3.18.0
fsspec==2024.12.0
huggingface-hub==0.30.1
multiprocess==0.70.16
numpy==2.2.4
packaging==24.2
pandas==2.2.3
pyarrow==19.0.1
pyyaml==6.0.2
requests==2.32.3
tqdm==4.67.1
xxhash==3.5.0
ipykernel==6.29.5
comm==0.2.2
debugpy==1.8.13
ipython==9.0.2
jupyter_client==8.6.3
jupyter_core==5.7.2
matplotlib-inline==0.1.7
nest-asyncio==1.6.0
packaging==24.2
psutil==7.0.0
pyzmq==26.3.0
tornado==6.4.2
traitlets==5.14.3
ipywidgets==8.1.5
comm==0.2.2
ipython==9.0.2
jupyterlab_widgets==3.0.13
traitlets==5.14.3
widgetsnbextension==4.0.13
onnxruntime-openvino==1.20.0
```

# install requirements for target project
Navigate to [model project folder](./README.md#model-files).
```
pip install requirements.txt
```
