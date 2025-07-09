from enum import Enum


class RuntimeEnum(Enum):
    CPU = "CPU"
    QNN = "QNN"
    IntelAny = "IntelAny"
    IntelCPU = "IntelCPU"
    IntelNPU = "IntelNPU"
    IntelGPU = "IntelGPU"
    AMDNPU = "AMDNPU"
    NvidiaGPU = "NvidiaGPU"
    NvidiaTRTRTX = "NvidiaTRTRTX"

    WCR = "WCR"
    # Inference
    QNN_LLLM = "QNN_LLM"


class RuntimeFeatureEnum(Enum):
    AutoGptq = "AutoGptq"
    Nightly = "Nightly"
    Genai = "Genai"
