# BERT optimization with PTQ on NPU

This workflow performs BERT optimization on Qualcomm NPU with ONNX Runtime PTQ. It performs the optimization pipeline:

- PyTorch Model -> Onnx Model -> Static shaped Onnx Model -> Quantized Onnx Model

It requires x86 python environment on a Windows ARM machine with onnxruntime-qnn installed.
