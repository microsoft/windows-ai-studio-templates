# BERT optimization with PTQ on NPU

This workflow performs BERT optimization on Qualcomm NPU with ONNX Runtime PTQ. It performs the optimization pipeline:

- PyTorch Model -> Onnx Model -> Static shaped Onnx Model -> Quantized Onnx Model

It requires x86 python environment on a Windows ARM machine with onnxruntime-qnn installed.

## Results

On a Snapdragon(R) X 12-core X1E80100:

|Model|Runtime|Size|Accuracy|Latency (ms)|
|-|-|-|-|-|
|Conversion Only|CPU|417 MB|0.90|50.41|
|Quantized|Qualcomm NPU|126 MB|0.90|35.50|
