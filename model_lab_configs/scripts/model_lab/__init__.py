from enum import Enum

class RuntimeEnum(Enum):
    CPU = "CPU"
    QNN = "QNN"
    IntelNPU = "IntelNPU"
    AMDNPU = "AMDNPU"
    NvidiaGPU = "NvidiaGPU"
    # Inference
    WCR = "WCR"
    

class RuntimeFeatureEnum(Enum):
    AutoGptq = "AutoGptq"
    Nightly = "Nightly"
    Genai = "Genai"
