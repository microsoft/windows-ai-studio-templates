# Vision Transformer (ViT) Optimization
This folder contains examples of ViT optimization using different workflows.
- Qualcomm NPU: [with QNN execution provider in ONNX Runtime](#vit-optimization-with-qnn-execution-providers)

## Optimization Workflows
### ViT optimization with QNN execution providers
This example performs ViT optimization with QNN execution providers in one workflow. It performs the optimization pipeline:
- *Huggingface Model -> Onnx Model -> QNN Quantized Onnx Model*

Config file: [vit-base-patch16-224.json](vit-base-patch16-224.json)

## How to run
```
olive run --config <config_file>.json
```

## Metrics
| Model | Accuracy | Latency (avg) |
|-|-|-|
| Original model | | |
| Quantized model | | |