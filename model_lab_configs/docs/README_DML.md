# DML

## LLM

### Install

uv pip install zstandard  -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9

uv pip install triton-windows -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9 

uv pip install autoawq --no-deps -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9

### Conversion

uv run -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9 -m olive run --config .\phi3_5_dml_config.json

### Inference

See Non-LLM

## Non-LLM

### Install

uv venv -p cpython-3.12.9-windows-x86_64-none C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

uv pip install -r ./requirements-WCR.txt -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

uv pip install onnxruntime-directml==1.22.0 -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

uv pip install onnxruntime-genai==0.8.3 --no-deps -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

### Conversion & Inference

uv run -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML -m olive run --config .\bert_dml.json
