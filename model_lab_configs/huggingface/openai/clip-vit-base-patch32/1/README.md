# Openai Clip optimization

This folder contains examples of Openai Clip optimization using different workflows.

- Text and vision model QDQ for Qualcomm NPU
- QDQ for AMD NPU
- OpenVINO for Intel NPU

## Openai Clip text optimization with QDQ for Qualcomm NPU

This example performs Openai Clip optimization with QDQ in one workflow. It performs the optimization pipeline:

- *PyTorch Model -> Onnx Model -> Quantized Onnx Model*

### Evaluation result

The quantization uses 256 samples from train split of imagenet-1k dataset and the evaluations uses 256 samples from test split of imagenet-1k dataset.


| Activation Type&nbsp; | Weight Type&nbsp; | Size&nbsp; | Latency ms (avg)&nbsp; |
| --------------------- | ----------------- | ---------- | ---------------------- |
| QUInt16               | QUInt8            | 100        | 6.53724                |

## Openai Clip vision optimization with QDQ for Qualcomm NPU

This example performs Openai Clip optimization with QDQ in one workflow. It performs the optimization pipeline:

- *PyTorch Model -> Onnx Model -> Quantized Onnx Model*

### Evaluation result

The quantization uses 256 samples from train split of imagenet-1k dataset and the evaluations uses 256 samples from test split of imagenet-1k dataset.


| Activation Type&nbsp; | Weight Type&nbsp; | Size&nbsp; | Latency ms (avg)&nbsp; |
| --------------------- | ----------------- | ---------- | ---------------------- |
| QUInt16               | QUInt8            | 100        | 20.13231               |


## Openai Clip optimization with QDQ for AMD NPU

This example performs Openai Clip optimization with QDQ in one workflow. It performs the optimization pipeline:

- *PyTorch Model -> Onnx Model -> Quantized Onnx Model*

## Openai Clip optimization with OpenVINO

This example performs Openai Clip optimization with OpenVINO in one workflow for Intel NPU.
