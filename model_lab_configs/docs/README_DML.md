# DML

## LLM

### Install

uv pip install zstandard  -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9

uv pip install triton-windows -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9 

uv pip install autoawq --no-deps -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9

### Conversion

uv run -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9 -m olive run --config .\phi3_5_dml_config.json

### Inference

## Non-LLM

### Install

uv pip uninstall onnxruntime-winml  -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-WCR-win32-x64-3.12.9

uv pip uninstall onnxruntime-genai-winml  -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-WCR-win32-x64-3.12.9

uv pip install onnxruntime-directml==1.22.0 -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-WCR-win32-x64-3.12.9

### Conversion & Inference

uv run -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-WCR-win32-x64-3.12.9 -m olive run --config .\bert_dml.json
