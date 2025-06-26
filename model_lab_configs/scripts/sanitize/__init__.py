"""
Sanitize module for Windows AI Studio model configurations
"""

from .constants import *
from .utils import (
    GlobalVars,
    printProcess,
    printInfo,
    printError,
    printWarning,
    open_ex,
    checkPath,
)
from .base import BaseModelClass
from .model_info import ModelInfo, ModelList
from .parameters import (
    Parameter,
    ParameterCheck,
    ParameterAction,
    readCheckParameterTemplate,
)
from .project_config import WorkflowItem, ModelInfoProject, ModelProjectConfig
from .model_parameter import (
    RuntimeOverwrite,
    Section,
    ADMNPUConfig,
    DebugInfo,
    ModelParameter,
)
from .copy_config import Replacement, Copy, CopyConfig
from .file_validation import (
    check_case,
    process_gitignore,
    readCheckOliveConfig,
    readCheckIpynb,
)
from .main import main

# Public API - defines what gets imported with "from sanitize import *"
# This list controls the module's public interface and prevents internal
# implementation details from being accidentally imported
__all__ = [
    # Constants - Enums and constant values from constants.py
    "IconEnum",
    "ArchitectureEnum",
    "ModelStatusEnum",
    "ParameterTypeEnum",
    "ParameterDisplayTypeEnum",
    "ParameterCheckTypeEnum",
    "ParameterActionTypeEnum",
    "ParameterTagEnum",
    "PhaseTypeEnum",
    "ReplaceTypeEnum",
    "EPNames",
    "OlivePassNames",
    "OlivePropertyNames",
    "outputModelRelativePath",
    "outputModelIntelNPURelativePath",
    "outputModelModelBuilderPath",
    "importOnnxruntime",
    "importOnnxgenairuntime",
    
    # Utils - Global variables and utility functions
    "GlobalVars",
    "printProcess",
    "printInfo",
    "printError",
    "printWarning",
    "open_ex",
    "checkPath",
    
    # Base - Base classes for models
    "BaseModelClass",
    
    # Model Info - Model information and listing classes
    "ModelInfo",
    "ModelList",
    
    # Parameters - Parameter validation and template handling
    "Parameter",
    "ParameterCheck",
    "ParameterAction",
    "readCheckParameterTemplate",
    
    # Project Config - Project configuration classes
    "WorkflowItem",
    "ModelInfoProject",
    "ModelProjectConfig",
    
    # Model Parameter - Model parameter configuration classes
    "RuntimeOverwrite",
    "Section",
    "ADMNPUConfig",
    "DebugInfo",
    "ModelParameter",
    
    # Copy Config - File copying configuration classes
    "Replacement",
    "Copy",
    "CopyConfig",
    
    # File Validation - File validation and processing functions
    "check_case",
    "process_gitignore",
    "readCheckOliveConfig",
    "readCheckIpynb",
    
    # Main - Main entry point function
    "main",
]
