# Qwen2.5-7B-Instruct Model Optimization

This repository demonstrates the optimization of the [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) model using **post-training quantization (PTQ)** techniques.
- OpenVINO for Intel GPU
   + This process uses OpenVINO specific passes like `OpenVINOOptimumConversion`, `OpenVINOIoUpdate` and `OpenVINOEncapsulation`

### **Inference**

#### **Run Console-Based Chat Interface**
Execute the provided `inference_sample.ipynb` notebook.
