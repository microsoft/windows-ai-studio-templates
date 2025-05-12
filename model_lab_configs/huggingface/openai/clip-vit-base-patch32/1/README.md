# Openai Clip text optimization with QDQ

This example performs Openai Clip optimization with QDQ in one workflow. It performs the optimization pipeline:

- *PyTorch Model -> Onnx Model -> Quantized Onnx Model*

## Evaluation result

The quantization uses 256 samples from train split of imagenet-1k dataset and the evaluations uses 256 samples from test split of imagenet-1k dataset.


| Activation Type&nbsp; | Weight Type&nbsp; | Size&nbsp; | Latency ms (avg)&nbsp; |
| --------------------- | ----------------- | ---------- | ---------------------- |
| QUInt16               | QUInt8            | 100        | 6.53724                |

# Openai Clip vision optimization with QDQ

This example performs Openai Clip optimization with QDQ in one workflow. It performs the optimization pipeline:

- *PyTorch Model -> Onnx Model -> Quantized Onnx Model*

## Evaluation result

The quantization uses 256 samples from train split of imagenet-1k dataset and the evaluations uses 256 samples from test split of imagenet-1k dataset.


| Activation Type&nbsp; | Weight Type&nbsp; | Size&nbsp; | Latency ms (avg)&nbsp; |
| --------------------- | ----------------- | ---------- | ---------------------- |
| QUInt16               | QUInt8            | 100        | 20.13231               |
