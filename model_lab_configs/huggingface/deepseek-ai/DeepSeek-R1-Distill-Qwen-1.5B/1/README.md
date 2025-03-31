# DeepSeek-R1-Distill-Qwen-1.5B optimization with QNN

## **QDQ Model with 4-bit Weights & 16-bit Activations**

This workflow produces an ONNX QDQ model that is agnostic to the target hardware and accelerator, making it suitable for general inference.

### **Optimization Process**

The model is optimized using **weight-only quantization** and **activation quantization** for efficient deployment. The process includes:

1. **Weight Rotation ([QuaRot](https://arxiv.org/abs/2404.00456))**
   - Reduces outliers from weights and hidden states to enhance quantization efficiency.

2. **4-bit Per-Channel Symmetric Quantization ([GPTQ](https://arxiv.org/abs/2210.17323))**
   - Reduces transformer layer size while preserving accuracy.

3. **ONNX Graph Capture**
   - Exports the model to ONNX for further optimization.

4. **4-bit Block-wise Quantization**
   - Applies weight-only quantization to the **embedding layer** and **language modeling head**.

5. **16-bit Activation Quantization**
   - Uses 16-bit activations to balance precision and efficiency.

The final output is a **QDQ model** with **4-bit weights** and **16-bit activations**. This model also leverages [GroupQueryAttention (GQA)](https://github.com/microsoft/onnxruntime/blob/main/docs/ContribOperators.md#com.microsoft.GroupQueryAttention) for efficient long-context processing and long-sequence generation.

### **Handling Dynamic and Static Input Shapes**

NPUs require **precompiled graphs**, meaning the model must use **static input shapes**. However, **text generation** involves two distinct processing stages:

- **Prefill (Prompt Processing)**: Processes multiple tokens simultaneously.
- **Token Generation (Iteration)**: Processes one token at a time.

To support both efficiently, we create **two model instances**:
1. **Prefill model**: Optimized for batch processing.
2. **Token generation model**: Optimized for one-token-at-a-time inference.

### **Usage**

#### **Quantization Python Environment Setup**
Quantization is resource-intensive and requires GPU acceleration. In an [x64 Python environment with Olive installed](../README.md#important), install the required packages:

```bash
# Install common dependencies
pip install -r requirements.txt

# Install ONNX Runtime GPU packages
pip install "onnxruntime-gpu>=1.21.0" "onnxruntime-genai-cuda>=0.6.0"

# AutoGPTQ: Install from source (stable package may be slow for weight packing)
# Disable CUDA extension build (not required)
# Linux
export BUILD_CUDA_EXT=0
# Windows
# set BUILD_CUDA_EXT=0

# Install AutoGPTQ from source
pip install --no-build-isolation git+https://github.com/PanQiWei/AutoGPTQ.git
```

#### **Run the Quantization Config**

```bash
olive run --config qdq_config.json
```

✅ Optimized model saved in: `models/DeepSeek-R1-Distill-Qwen-1.5B`
