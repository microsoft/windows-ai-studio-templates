# ResNet optimization with QNN execution providers

This example performs ResNet optimization with QNN execution providers in one workflow. It performs the optimization pipeline:

- *PyTorch Model -> Onnx Model -> QNN Quantized Onnx Model*

## Evaluation result

| Activation Type | Weight Type | Accuracy | Latency (avg) |
|-----------------|-------------|----------|---------|
| QUInt16         | QUInt8      |  0.78515625      | 2.53724 ms  |
