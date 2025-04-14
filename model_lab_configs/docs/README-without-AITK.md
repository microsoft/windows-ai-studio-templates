# Setup environment
We recommend installing env in a [virtual environment](https://docs.python.org/3/library/venv.html) or a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

Note: if you want to do inference on NPU devices with QNN EP, we recommend use [virtual environment](https://docs.python.org/3/library/venv.html). It is because inference with some model may need `arm` version python, while conda has not supported creating an arm version python venv yet.

- CPU: [Setup CPU environment](#setup-cpu-environment)
- QNN: [Setup QNN environment](#setup-qnn-environment)
- AMD: [Setup AMD environment](#setup-amd-environment)

## Setup CPU environment
You can directly setup NPU environment such as [Setup QNN environment](#setup-qnn-environment). It will fallback to CPU EP when process.

## Setup QNN environment
python version: 3.12.9
```
pip install olive-ai==0.8.0
pip install transformer==4.50.3
pip install onnxruntime-qnn==1.20.2
```

## Setup AMD environment
python version: 3.10.9
```
```

# install requirements for target project
Navigate to model project folder.
```
pip install requirements.txt
```
