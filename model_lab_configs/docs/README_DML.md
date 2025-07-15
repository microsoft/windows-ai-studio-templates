# DML

## Install

uv venv -p cpython-3.12.9-windows-x86_64-none C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

uv pip install -r ./requirements-DML.txt -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML --index-strategy unsafe-best-match

uv pip install autoawq --no-deps -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

## Conversion

uv run -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML -m olive run --config .\bert_dml.json

## Inference LLM

No change needed

## Inference Non-LLM

- comment `add_ep_for_device`
- add `providers=["DmlExecutionProvider"]`
