# DML

## Install

uv venv -p cpython-3.12.9-windows-x86_64-none C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

uv pip install -r ./requirements-DML.txt -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML --index-strategy unsafe-best-match

uv pip install autoawq --no-deps -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

## Conversion

https://github.com/microsoft/onnxruntime-genai/blob/main/examples/python/awq-quantized-model.py

uv run -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML -m olive run --config .\xxx.json

## Inference LLM

No change needed

## Inference Non-LLM

- comment `add_ep_for_device`
- add `providers=["DmlExecutionProvider"]`

## Result

CPU: Intel(R) Xeon(R) Silver 4108 CPU @ 1.80GHz (1.80 GHz) (2 processors)

GPU: NVIDIA GeForce RTX 2080 Ti

### model_lab_configs\huggingface\microsoft\Phi-3.5-mini-instruct\1\phi3_5_dml_config.json

Tokens per second: 66.63

### model_lab_configs\huggingface\deepseek-ai\DeepSeek-R1-Distill-Qwen-1.5B\1\deepseek_dml_config.json

Tokens per second: 57.62

### model_lab_configs\huggingface\meta-llama\Llama-3.2-1B-Instruct\1\llama3_2_dml_config.json

Tokens per second: 69.53

### model_lab_configs\huggingface\Qwen\Qwen2.5-1.5B-Instruct\1\qwen2_5_dml_config.json

Tokens per second: 50.86

### model_lab_configs\huggingface\google\vit-base-patch16-224\1\vit_base_patch16_224_dml.json

+------------+-------------------+-----------------------------+----------------+-------------------------------------------------+
| model_id   | parent_model_id   | from_pass                   |   duration_sec | metrics                                         |
+============+===================+=============================+================+=================================================+
| 152d86fb   |                   |                             |                | {                                               |
|            |                   |                             |                |   "accuracy-accuracy_score": 0.902999997138977, |
|            |                   |                             |                |   "latency-avg": 27.52956                       |
|            |                   |                             |                | }                                               |
+------------+-------------------+-----------------------------+----------------+-------------------------------------------------+
| 779a3395   | 152d86fb          | onnxconversion              |        9.56482 |                                                 |
+------------+-------------------+-----------------------------+----------------+-------------------------------------------------+
| 99b7206a   | 779a3395          | orttransformersoptimization |       10.8156  | {                                               |
|            |                   |                             |                |   "accuracy-accuracy_score": 0.902999997138977, |
|            |                   |                             |                |   "latency-avg": 5.12732                        |
|            |                   |                             |                | }                                               |
+------------+-------------------+-----------------------------+----------------+-------------------------------------------------+

### model_lab_configs\huggingface\google-bert\bert-base-multilingual-cased\1\bert-base-multilingual-cased_dml.json

+------------+-------------------+-----------------------------+----------------+--------------------------------+
| model_id   | parent_model_id   | from_pass                   |   duration_sec | metrics                        |
+============+===================+=============================+================+================================+
| 9afcc580   |                   |                             |                | {                              |
|            |                   |                             |                |   "latency-avg": 30.45582,     |
|            |                   |                             |                |   "latency-max": 41.76976,     |
|            |                   |                             |                |   "latency-min": 22.9417,      |
|            |                   |                             |                |   "throughput-avg": 42.89333,  |
|            |                   |                             |                |   "throughput-max": 49.60192,  |
|            |                   |                             |                |   "throughput-min": 34.10765   |
|            |                   |                             |                | }                              |
+------------+-------------------+-----------------------------+----------------+--------------------------------+
| 4f90bcab   | 9afcc580          | onnxconversion              |        28.5732 |                                |
+------------+-------------------+-----------------------------+----------------+--------------------------------+
| b1c9cae9   | 4f90bcab          | orttransformersoptimization |        19.7799 | {                              |
|            |                   |                             |                |   "latency-avg": 11.00075,     |
|            |                   |                             |                |   "latency-max": 12.8655,      |
|            |                   |                             |                |   "latency-min": 9.2979,       |
|            |                   |                             |                |   "throughput-avg": 98.66107,  |
|            |                   |                             |                |   "throughput-max": 110.22563, |
|            |                   |                             |                |   "throughput-min": 72.41916   |
|            |                   |                             |                | }                              |
+------------+-------------------+-----------------------------+----------------+--------------------------------+

### model_lab_configs\huggingface\Intel\bert-base-uncased-mrpc\1\bert_dml.json

+------------+-------------------+-----------------------------+----------------+--------------------------------------------------+
| model_id   | parent_model_id   | from_pass                   |   duration_sec | metrics                                          |
+============+===================+=============================+================+==================================================+
| bbda6295   |                   |                             |                | {                                                |
|            |                   |                             |                |   "accuracy-accuracy_score": 0.8999999761581421, |
|            |                   |                             |                |   "accuracy-f1_score": 0.9324324131011963,       |
|            |                   |                             |                |   "latency-avg": 32.81298                        |
|            |                   |                             |                | }                                                |
+------------+-------------------+-----------------------------+----------------+--------------------------------------------------+
| 8862acae   | bbda6295          | onnxconversion              |      0.0139849 |                                                  |
+------------+-------------------+-----------------------------+----------------+--------------------------------------------------+
| c9067f95   | 8862acae          | orttransformersoptimization |      0         | {                                                |
|            |                   |                             |                |   "accuracy-accuracy_score": 0.8999999761581421, |
|            |                   |                             |                |   "accuracy-f1_score": 0.9324324131011963,       |
|            |                   |                             |                |   "latency-avg": 9.10664                         |
|            |                   |                             |                | }                                                |
+------------+-------------------+-----------------------------+----------------+--------------------------------------------------+
