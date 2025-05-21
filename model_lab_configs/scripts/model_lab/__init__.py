from enum import Enum

class RuntimeEnum(Enum):
    CPU = "CPU"
    QNN = "QNN"
    IntelNPU = "IntelNPU"
    AMDNPU = "AMDNPU"
    NvidiaGPU = "NvidiaGPU"
    WCR = "WCR"
    # Inference
    QNN_LLLM = "QNN_LLM"
    

class RuntimeFeatureEnum(Enum):
    AutoGptq = "AutoGptq"
    Nightly = "Nightly"
    Genai = "Genai"
