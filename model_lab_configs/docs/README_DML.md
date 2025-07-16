# DML

## Install

for evaluate_input_model = true, this is needed as it evaluates original model which will run on CUDA.

```
uv venv -p cpython-3.12.9-windows-x86_64-none C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML

uv pip install -r ./requirements-DML.txt -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML --index-strategy unsafe-best-match

uv pip install autoawq --no-deps -p C:\Users\hualxie\.aitk\bin\model_lab_runtime\Python-DML
```

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

### model_lab_configs\huggingface\laion\CLIP-ViT-B-32-laion2B-s34B-b79K\1\laion_clip_dml.json

+------------+-------------------+-----------------------------+----------------+-----------------------------+
| model_id   | parent_model_id   | from_pass                   |   duration_sec | metrics                     |
+============+===================+=============================+================+=============================+
| 2c3c7790   |                   |                             |                | {                           |
|            |                   |                             |                |   "accuracy-accuracy": 1.0, |
|            |                   |                             |                |   "latency-avg": 59.82747,  |
|            |                   |                             |                |   "latency-p90": 71.94618   |
|            |                   |                             |                | }                           |
+------------+-------------------+-----------------------------+----------------+-----------------------------+
| 2affadfb   | 2c3c7790          | onnxconversion              |        18.7062 |                             |
+------------+-------------------+-----------------------------+----------------+-----------------------------+
| 92b86161   | 2affadfb          | orttransformersoptimization |        26.0375 | {                           |
|            |                   |                             |                |   "accuracy-accuracy": 1.0, |
|            |                   |                             |                |   "latency-avg": 5.69329,   |
|            |                   |                             |                |   "latency-p90": 7.03943    |
|            |                   |                             |                | }                           |
+------------+-------------------+-----------------------------+----------------+-----------------------------+

### model_lab_configs\huggingface\microsoft\resnet-50\1\resnet_dml.json

+------------+-------------------+--------------------+----------------+--------------------------------------------------+
| model_id   | parent_model_id   | from_pass          |   duration_sec | metrics                                          |
+============+===================+====================+================+==================================================+
| 912fb5a6   |                   |                    |                | {                                                |
|            |                   |                    |                |   "accuracy-accuracy_score": 0.9430000185966492, |
|            |                   |                    |                |   "latency-avg": 31.00325                        |
|            |                   |                    |                | }                                                |
+------------+-------------------+--------------------+----------------+--------------------------------------------------+
| 8b420e53   | 912fb5a6          | onnxconversion     |      0.0156729 |                                                  |
+------------+-------------------+--------------------+----------------+--------------------------------------------------+
| 81216919   | 8b420e53          | onnxfloattofloat16 |      0.0159111 | {                                                |
|            |                   |                    |                |   "accuracy-accuracy_score": 0.9440000057220459, |
|            |                   |                    |                |   "latency-avg": 3.81625                         |
|            |                   |                    |                | }                                                |
+------------+-------------------+--------------------+----------------+--------------------------------------------------+

### model_lab_configs\huggingface\openai\clip-vit-base-patch16\1\openai_clip_dml.json

+------------+-------------------+-----------------------------+----------------+--------------------------------+
| model_id   | parent_model_id   | from_pass                   |   duration_sec | metrics                        |
+============+===================+=============================+================+================================+
| 6532d6d6   |                   |                             |                | {                              |
|            |                   |                             |                |   "accuracy-accuracy": 1.0,    |
|            |                   |                             |                |   "latency-avg": 69.14089,     |
|            |                   |                             |                |   "latency-max": 81.38998,     |
|            |                   |                             |                |   "latency-min": 62.42493,     |
|            |                   |                             |                |   "throughput-avg": 13.42695,  |
|            |                   |                             |                |   "throughput-max": 15.5861,   |
|            |                   |                             |                |   "throughput-min": 9.5068     |
|            |                   |                             |                | }                              |
+------------+-------------------+-----------------------------+----------------+--------------------------------+
| ed6e9c28   | 6532d6d6          | onnxconversion              |        20.1503 |                                |
+------------+-------------------+-----------------------------+----------------+--------------------------------+
| 29793dca   | ed6e9c28          | orttransformersoptimization |        23.9136 | {                              |
|            |                   |                             |                |   "accuracy-accuracy": 1.0,    |
|            |                   |                             |                |   "latency-avg": 9.89795,      |
|            |                   |                             |                |   "latency-max": 12.665,       |
|            |                   |                             |                |   "latency-min": 7.68,         |
|            |                   |                             |                |   "throughput-avg": 107.76594, |
|            |                   |                             |                |   "throughput-max": 134.78542, |
|            |                   |                             |                |   "throughput-min": 96.9415    |
|            |                   |                             |                | }                              |
+------------+-------------------+-----------------------------+----------------+--------------------------------+

### model_lab_configs\huggingface\openai\clip-vit-base-patch32\1\openai_clip_dml.json

+------------+-------------------+-----------------------------+----------------+--------------------------------+
| model_id   | parent_model_id   | from_pass                   |   duration_sec | metrics                        |
+============+===================+=============================+================+================================+
| 57615e23   |                   |                             |                | {                              |
|            |                   |                             |                |   "accuracy-accuracy": 1.0,    |
|            |                   |                             |                |   "latency-avg": 76.82118,     |
|            |                   |                             |                |   "latency-max": 88.12714,     |
|            |                   |                             |                |   "latency-min": 61.09002,     |
|            |                   |                             |                |   "throughput-avg": 12.45977,  |
|            |                   |                             |                |   "throughput-max": 14.9671,   |
|            |                   |                             |                |   "throughput-min": 8.01081    |
|            |                   |                             |                | }                              |
+------------+-------------------+-----------------------------+----------------+--------------------------------+
| 799be411   | 57615e23          | onnxconversion              |        20.16   |                                |
+------------+-------------------+-----------------------------+----------------+--------------------------------+
| beb26980   | 799be411          | orttransformersoptimization |        24.4395 | {                              |
|            |                   |                             |                |   "accuracy-accuracy": 1.0,    |
|            |                   |                             |                |   "latency-avg": 7.91565,      |
|            |                   |                             |                |   "latency-max": 8.0933,       |
|            |                   |                             |                |   "latency-min": 7.4151,       |
|            |                   |                             |                |   "throughput-avg": 116.37339, |
|            |                   |                             |                |   "throughput-max": 144.73456, |
|            |                   |                             |                |   "throughput-min": 46.94064   |
|            |                   |                             |                | }                              |
+------------+-------------------+-----------------------------+----------------+--------------------------------+
