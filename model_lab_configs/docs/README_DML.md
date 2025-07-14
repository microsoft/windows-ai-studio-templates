# DML

## Install

uv pip install zstandard  -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9

uv pip install triton-windows -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9 

uv pip install autoawq --no-deps -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9

## Run

uv run -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-NvidiaGPU-win32-x64-3.10.9 -m olive run --config .\phi3_5_dml_config.json
