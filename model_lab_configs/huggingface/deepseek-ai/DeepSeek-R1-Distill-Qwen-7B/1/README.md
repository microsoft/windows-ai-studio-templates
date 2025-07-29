# DeepSeek-R1-Distill-Qwen-7B Model Optimization

This repository demonstrates the optimization of the [DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B) model using **post-training quantization (PTQ)** techniques. 
- OpenVINO for Intel GPU
   + This process uses OpenVINO specific passes like `OpenVINOOptimumConversion`, `OpenVINOIoUpdate` and `OpenVINOEncapsulation`

#### **Run Console-Based Chat Interface**
Execute the provided `inference_sample.ipynb` notebook.

> ⚠️ If got 6033 error, replace `genai_config.json` in `./model` folder
