from __future__ import annotations
import argparse
import re
import shutil
import subprocess
from typing import Any, Dict
from pydantic import BaseModel, TypeAdapter
import os
from enum import Enum
import copy
import pydash
import json
from pathlib import Path
from model_lab import RuntimeEnum, RuntimeFeatureEnum

# Constants

class OlivePassNames:
    OnnxConversion = "OnnxConversion"
    OnnxQuantization = "OnnxQuantization"
    OnnxStaticQuantization = "OnnxStaticQuantization"
    OnnxDynamicQuantization = "OnnxDynamicQuantization"
    ModelBuilder = "ModelBuilder"
    OpenVINOConversion = "OpenVINOConversion"


class OlivePropertyNames:
    Engine = "engine"
    Passes = "passes"
    Evaluator = "evaluator"
    Evaluators = "evaluators"
    Type = "type"
    ExternalData = "save_as_external_data"
    Systems = "systems"
    Accelerators = "accelerators"
    ExecutionProviders = "execution_providers"
    DataConfigs = "data_configs"
    Target = "target"
    CacheDir = "cache_dir"
    OutputDir = "output_dir"
    PythonEnvironmentPath = "python_environment_path"
    EvaluateInputModel = "evaluate_input_model"
    Metrics = "metrics"
    UserConfig = "user_config"


outputModelRelativePath = "\\\"./model/model.onnx\\\""
outputModelModelBuilderPath = "\\\"./model\\\""
importOnnxruntime = "import onnxruntime as ort"


# Enums

class IconEnum(Enum):
    Intel = "intel"
    Gemini = "gemini"
    OpenAI = "OpenAI"
    Microsoft = "ms"
    Meta = "meta"
    CompVis = "compvis"
    BAAI = "baai"
    tiiuae = "tiiuae"
    EleutherAI = "eleutherai"
    openlm = "openlm"
    DeepSeek = "DeepSeek"
    laion = "laion"
    qwen = "qwen"
    HuggingFace = "HuggingFace"


class ArchitectureEnum(Enum):
    Transformer = "Transformer"
    CNN = "CNN"
    Diffusion = "Diffusion"
    Others = "Others"


class ModelStatusEnum(Enum):
    Ready = "Ready"
    Coming = "Coming"
    Hide = "Hide"


class ParameterTypeEnum(Enum):
    Enum = "enum"
    Int = "int"
    Bool = "bool"
    String = "str"


class ParameterDisplayTypeEnum(Enum):
    Dropdown = "Dropdown"
    RadioGroup = "RadioGroup"


class ParameterCheckTypeEnum(Enum):
    Exist = "exist"
    NotExist = "notExist"


class ParameterActionTypeEnum(Enum):
    # Update and Insert are both upsert in runtime. Separate them for validation
    Update = "update"
    Insert = "insert"
    Delete = "delete"


class ParameterTagEnum(Enum):
    QuantizationDataset = "QuantizationDataset"
    QuantizationDatasetSubset = "QuantizationDatasetSubset"
    QuantizationDatasetSplit = "QuantizationDatasetSplit"
    EvaluationDataset = "EvaluationDataset"
    EvaluationDatasetSubset = "EvaluationDatasetSubset"
    EvaluationDatasetSplit = "EvaluationDatasetSplit"
    DependsOnDataset = "DependsOnDataset"
    ActivationType = "ActivationType"
    WeightType = "WeightType"


class PhaseTypeEnum(Enum):
    Conversion = "Conversion"
    Quantization = "Quantization"
    Evaluation = "Evaluation"


class ReplaceTypeEnum(Enum):
    String = "string"
    Path = "path"
    PathAdd = "pathAdd"


class EPNames(Enum):
    CPUExecutionProvider = "CPUExecutionProvider"
    CUDAExecutionProvider = "CUDAExecutionProvider"
    QNNExecutionProvider = "QNNExecutionProvider"
    OpenVINOExecutionProvider = "OpenVINOExecutionProvider"
    VitisAIExecutionProvider = "VitisAIExecutionProvider"


# Global vars

class GlobalVars:  
    SomethingError = False

    @classmethod
    def hasError(cls):
        cls.SomethingError = True

    epToName = {
        EPNames.QNNExecutionProvider.value: "Qualcomm NPU",
        EPNames.OpenVINOExecutionProvider.value: "Intel NPU",
        EPNames.VitisAIExecutionProvider.value: "AMD NPU",
        EPNames.CPUExecutionProvider.value: "CPU",
        EPNames.CUDAExecutionProvider.value: "NVIDIA GPU",
    }
    verbose = False
    pathCheck = 0
    configCheck = 0


# Model List

class ModelInfo(BaseModel):
    displayName: str
    discription: str = None
    icon: IconEnum
    modelLink: str
    id: str
    runtimes: list[RuntimeEnum]
    architecture: ArchitectureEnum
    status: ModelStatusEnum = ModelStatusEnum.Hide
    version: int = -1

    def Check(self):
        if not self.status:
            return False
        if self.status == ModelStatusEnum.Hide:
            return True
        
        if not self.displayName:
            return False
        if not self.modelLink:
            return False
        if not self.id and self.status == ModelStatusEnum.Ready:
            return False
        if not self.runtimes:
            return False
        if self.version == -1 and self.status == ModelStatusEnum.Ready:
            return False
        return True
        

class ModelList(BaseModel):
    models: list[ModelInfo]
    template_models: list[ModelInfo]
    HFDatasets: Dict[str, str]
    LoginRequiredDatasets: list[str]
    # If exist in the dict, we will use the one from dict
    # If not exist in the dict, we will use the config from json
    # - if only one value, don't need to add
    # - custom config could provide a combined list for new datasets
    DatasetSplit: Dict[str, list[str]]
    DatasetSubset: Dict[str, list[str]]

    @staticmethod
    def Read(scriptFolder: str):
        modelListFile = os.path.join(scriptFolder, "model_list.json")
        print(f"Process {modelListFile}")
        with open(modelListFile, 'r', encoding='utf-8') as file:
            modelListContent = file.read()
        modelList = ModelList.model_validate_json(modelListContent, strict=True)
        modelList._file = modelListFile
        modelList._fileContent = modelListContent
        return modelList
    
    def allModels(self):
        return self.models + self.template_models

    # Check after set version
    def Check(self):
        for i, model in enumerate(self.allModels()):
            if not model.Check():
                print(f"{self._file} model {i} has error")
                GlobalVars.hasError()
        newContent = self.model_dump_json(indent=4, exclude_none=True)
        if newContent != self._fileContent:
            with open(self._file, 'w', encoding='utf-8') as file:
                file.write(newContent)

        self.CheckDataset(self.LoginRequiredDatasets, "LoginRequiredDatasets")
        self.CheckDataset(self.DatasetSplit.keys(), "DatasetSplit")
        self.CheckDataset(self.DatasetSubset.keys(), "DatasetSubset")
    
    def CheckDataset(self, datasetKeys, name: str):
        for key in datasetKeys:
            if key not in self.HFDatasets:
                print(f"{self._file} {name} {key} not in HFDatasets")
                GlobalVars.hasError()


# Parameter

def checkPath(path: str, oliveJson: Any, printOnNotExist: bool = True):
    if GlobalVars.verbose: print(path)
    GlobalVars.pathCheck += 1
    if pydash.get(oliveJson, path) is None:
        if printOnNotExist: print(f"Not in olive json: {path}")
        return False
    return True


class ParameterCheck(BaseModel):
    type: ParameterCheckTypeEnum = None
    path: str = None

    def check(self, oliveJson: Any):
        if not self.type:
            return False
        if not self.path:
            return False
        if not checkPath(self.path, oliveJson):
            return False
        return True


class ParameterAction(BaseModel):
    type: ParameterActionTypeEnum = None
    path: str = None
    value: str | int | bool | float | Any = None

    def check(self, oliveJson: Any):
        if not self.type:
            return False
        if not self.path:
            return False
        if self.type in [ParameterActionTypeEnum.Insert, ParameterActionTypeEnum.Update] and not self.value:
            return False
        pathExist = checkPath(self.path, oliveJson, False)
        if self.type in [ParameterActionTypeEnum.Delete, ParameterActionTypeEnum.Update] and not pathExist:
            return False
        if self.type in [ParameterActionTypeEnum.Insert] and pathExist:
            return False
        return True


class Parameter(BaseModel):
    """
    REMEMEBER to update clearValue and applyTemplate if new fields are added
    for enum type and bool type, either path + values or checks + actions

    path: path to the parameter in olive json
    values: possible values for the parameter.
        path and values are used to determine the status of the parameter
    checks: advanced method to get default value for enum or bool
    actions: actions to be performed on the parameter in template(original) olive json.
        if actions is empty, the parameter is upserted by path = selected value

    """
    # This tag is only used for the case that when we edit the json, we know the property is auto generated by sanitize.py so no need to care about it 
    autoGenerated: bool = None
    name: str = None
    tags: list[ParameterTagEnum] = None
    description: str = None
    descriptionLink: str = None
    type: ParameterTypeEnum = None
    displayNames: list[str] = None
    displayType: ParameterDisplayTypeEnum = None
    path: str = None
    values: list[str] = None
    # TODO update to expression
    selectors: list[ParameterCheck] = None
    actions: list[list[ParameterAction]] = None
    readOnly: bool | None = None
    customize: bool = None
    # 1st level is Parameter and 2nd level is str in templates
    # always put template in the end
    template: Parameter | str = None

    def Check(self, isTemplate: bool, oliveJson: Any = None, modelList: ModelList = None):
        if isTemplate:
            if self.template:
                return False
            return True

        if not self.name:
            return False
        if not self.description:
            if self.descriptionLink:
                print("Description link should not be used without description")
                return False
        if not self.type:
            return False
        if self.type != ParameterTypeEnum.Bool and self.type != ParameterTypeEnum.Enum:            
            if not self.path:
                return False
            elif not checkPath(self.path, oliveJson):
                return False
            elif self.values or self.selectors or self.actions or self.displayNames or self.customize:
                print("Redundant fields")
                return False
        else:
            expectedLength = 2
            lenValues = len(self.values) if self.values else 0
            lenChecks = len(self.selectors) if self.selectors else 0
            lenActions = len(self.actions) if self.actions else 0
            if self.type == ParameterTypeEnum.Enum:
                expectedLength = max(lenValues, lenChecks)
                if expectedLength == 0:
                    print("Enum should have values or checks")
                    return False
            
            # Display names
            if self.type == ParameterTypeEnum.Enum and self.selectors and not self.displayNames:
                print("Display names should be used with checks")
                return False

            if self.displayNames and len(self.displayNames) != expectedLength:
                print(f"Display names has wrong length {expectedLength}")
                return False
            
            # Display type
            if self.type == ParameterTypeEnum.Enum:
                if not (not self.displayType or self.displayType == ParameterDisplayTypeEnum.Dropdown or self.displayType == ParameterDisplayTypeEnum.RadioGroup):
                    print("Display type should be Dropdown or RadioGroup")
                    return False

            # customize
            if self.customize == True:
                if not (self.type == ParameterTypeEnum.Enum and self.values and not self.selectors):
                    print("Wrong customize prerequisites!")
                    return False

            # path: bool
            # path + actions: bool  
            # path + values: enum
            # path + values + actions: bool, enum
            # checks + actions: bool, enum
            if self.type == ParameterTypeEnum.Bool and self.path and not self.values and not self.selectors and not self.actions:
                pass
            elif self.type == ParameterTypeEnum.Bool and self.path and not self.values and not self.selectors and lenActions == expectedLength:
                pass
            elif self.type == ParameterTypeEnum.Enum and self.path and lenValues == expectedLength and not self.selectors and not self.actions:
                pass
            elif self.path and lenValues == expectedLength and not self.selectors and lenActions == expectedLength:
                pass
            elif not self.path and not self.values and lenChecks == expectedLength and lenActions == expectedLength:
                pass
            else:
                print(f"Invalid combination. Check comment")
                return False
            
            if self.path:
                if not checkPath(self.path, oliveJson):
                    return False
                # TODO more checks
                if self.values:
                    value = pydash.get(oliveJson, self.path)
                    if self.tags and (ParameterTagEnum.EvaluationDataset in self.tags or ParameterTagEnum.QuantizationDataset in self.tags):
                        if value != self.values[0]:
                            print(f"Value {value} not the first in values for {self.path}")
                            return False
                        for i in range(len(self.values) - 1):
                            value_in_list = self.values[i + 1]
                            if value_in_list not in modelList.DatasetSplit:
                                print(f"Value {value_in_list} not in DatasetSplit for {self.path}")
                                return False
                            if value_in_list not in modelList.DatasetSubset:
                                print(f"WARNING: Value {value_in_list} not in DatasetSubset for {self.path}. Could be acceptable if it doesn't have subset")
                    elif value not in self.values:
                        print(f"Value {value} not in values for {self.path}")
                        return False

            if self.selectors:
                for i, check in enumerate(self.selectors):
                    if not check.check(oliveJson):
                        print(f"Check {i} has error")
                        return False

            if self.actions:
                for i, actions in enumerate(self.actions):
                    for j, action in enumerate(actions):
                        if not action.check(oliveJson):
                            print(f"Action {i} {j} has error")
                            return False
        return True

    def clearValue(self):
        """
        Clear everything except template
        """
        for attr in vars(self):
            if attr != "template":
                setattr(self, attr, None)

    def applyTemplate(self, template: Parameter):
        """
        Apply everything except template
        """
        for attr, value in vars(template).items():
            if not getattr(self, attr) and attr != "template":
                setattr(self, attr, value)


def readCheckParameterTemplate(filePath: str):
    print(f"Process {filePath}")
    with open(filePath, 'r', encoding='utf-8') as file:
        fileContent = file.read()
    adapter = TypeAdapter(Dict[str, Parameter])
    parameters: Dict[str, Parameter] = adapter.validate_json(fileContent, strict=True)
    for key, parameter in parameters.items():
        if not parameter.Check(True):
            print(f"{filePath} parameter {key} has error")
            GlobalVars.hasError()
    newContent = adapter.dump_json(parameters, indent=4, exclude_none=True).decode('utf-8')
    if newContent != fileContent:
        with open(filePath, 'w', encoding='utf-8') as file:
            file.write(newContent)
    return parameters


# Model

class WorkflowItem(BaseModel):
    name: str
    file: str
    template: str = None
    version: int = 0
    templateName: str = None
    # DO NOT ADD ANYTHING ELSE HERE
    # We should add it to the *.json.config

    def Check(self):
        if not self.name:
            return False
        if not self.file:
            return False
        if '\\' in self.file:
            print("Please use / instead of \\")
            return False
        if not self.template:
            return False
        if self.version <= 0:
            return False
        if not self.templateName:
            return False
        return True


class ModelInfoProject(BaseModel):
    id: str
    displayName: str = None
    icon: IconEnum = None
    modelLink: str = None

    def Check(self, modelInfo: ModelInfo):
        if not self.id:
            return False
        if self.displayName and self.displayName != modelInfo.displayName:
            return False
        if self.icon and self.icon != modelInfo.icon:
            return False
        if self.modelLink and self.modelLink != modelInfo.modelLink:
            return False
        return True


class ModelProjectConfig(BaseModel):
    workflows: list[WorkflowItem]
    modelInfo: ModelInfoProject = None

    @staticmethod
    def Read(modelSpaceConfigFile: str):
        print(f"Process {modelSpaceConfigFile}")
        with open(modelSpaceConfigFile, 'r', encoding='utf-8') as file:
            modelSpaceConfigContent = file.read()
        modelSpaceConfig = ModelProjectConfig.model_validate_json(modelSpaceConfigContent, strict=True)
        modelSpaceConfig._file = modelSpaceConfigFile
        modelSpaceConfig._fileContent = modelSpaceConfigContent
        return modelSpaceConfig

    # after template is set
    def Check(self, modelInfo: ModelInfo):
        for i, model in enumerate(self.workflows):
            if not model.Check():
                print(f"{self._file} model {i} has error")
                GlobalVars.hasError()
        
        if not self.modelInfo.Check(modelInfo):
            print(f"{self._file} modelInfo has error")
            GlobalVars.hasError()

        newContent = self.model_dump_json(indent=4, exclude_none=True)
        if newContent != self._fileContent:
            with open(self._file, 'w', encoding='utf-8') as file:
                file.write(newContent)


# Model Parameter

# By default, runtime is both execute + evaluate
# This will overwrite execute
class RuntimeOverwrite(BaseModel):
    # This tag is only used for the case that when we edit the json, we know the property is auto generated by sanitize.py so no need to care about it 
    autoGenerated: bool = None,
    pyEnvPath: str = None
    executeEp: EPNames = None
    # This is usually used for EP binary generation
    evaluateUsedInExecute: bool = None

    def Check(self, oliveJson: Any):
        if not checkPath(self.pyEnvPath, oliveJson):
            return False
        return True


# toggle: usually used for on/off switch
class Section(BaseModel):
    # This tag is only used for the case that when we edit the json, we know the property is auto generated by sanitize.py so no need to care about it 
    autoGenerated: bool = None
    name: str
    phase: PhaseTypeEnum
    description: str = None
    parameters: list[Parameter]
    toggle: Parameter = None

    @staticmethod
    def datasetPathPattern(path: str): 
        return re.fullmatch(r'data_configs\[(0|[1-9]\d{0,2})\]\.load_dataset_config\.data_name', path)

    def Check(self, templates: Dict[str, Parameter], _file: str, sectionId: int, oliveJson: Any, modelList: ModelList):
        if not self.name:
            return False
        #if not self.description:
        #    return False
        # TODO add place holder for General?
        if not self.parameters and self.phase != PhaseTypeEnum.Conversion:
            return False
        
        for i, parameter in enumerate(self.parameters):
            if parameter.template:
                template = parameter.template
                if template.template not in templates:
                    print(f"{_file} section {sectionId} parameter {i} has wrong template")
                    GlobalVars.hasError()
                    continue
                parameter.clearValue()
                parameter.applyTemplate(template)
                parameter.applyTemplate(templates[template.template])
            if not parameter.Check(False, oliveJson, modelList):
                print(f"{_file} section {sectionId} parameter {i} has error")
                GlobalVars.hasError()

            # TODO move tag check into Parameter
            if Section.datasetPathPattern(parameter.path):
                if self.phase == PhaseTypeEnum.Quantization:
                    if not parameter.tags or ParameterTagEnum.QuantizationDataset not in parameter.tags:
                        print(f"{_file} section {sectionId} parameter {i} should have QuantizationDataset tag")
                        GlobalVars.hasError()
                elif self.phase == PhaseTypeEnum.Evaluation:
                    if not parameter.tags or ParameterTagEnum.EvaluationDataset not in parameter.tags:
                        print(f"{_file} section {sectionId} parameter {i} should have EvaluationDataset tag")
                        GlobalVars.hasError()
                missing_keys = [key for key in parameter.values if key not in modelList.HFDatasets]
                if missing_keys:
                    print("datasets are not in HFDatasets:", ', '.join(missing_keys))
                    GlobalVars.hasError()
            elif parameter.path.endswith("activation_type"):
                if not parameter.tags or ParameterTagEnum.ActivationType not in parameter.tags:
                    print(f"{_file} section {sectionId} parameter {i} should have ActivationType tag")
                    GlobalVars.hasError()
            elif parameter.path.endswith("weight_type"):
                if not parameter.tags or ParameterTagEnum.WeightType not in parameter.tags:
                    print(f"{_file} section {sectionId} parameter {i} should have WeightType tag")
                    GlobalVars.hasError()

        if self.toggle:
            if self.toggle.type != ParameterTypeEnum.Bool:
                print(f"{_file} section {sectionId} toggle must use bool")
                return False
            if not self.toggle.Check(False, oliveJson, modelList):
                print(f"{_file} section {sectionId} toggle has error")
                GlobalVars.hasError()

        return True
    

class ADMNPUConfig(BaseModel):
    inferenceSettings: Any = None


class ModelParameter(BaseModel):
    # SET AUTOMATICALLY
    isLLM: bool = None
    # For template using CUDA and no runtime overwrite, we need to set this so we know the target EP
    evalRuntime: EPNames = None
    # SET AUTOMATICALLY
    # This kind of config will
    # - could not disable quantization
    # - use modelbuilder for conversion
    # - output a model folder instead of model file
    useModelBuilder: str = None
    # SET AUTOMATICALLY
    # This kind of config will
    # - could not disable quantization
    # - use OpenVINOConversion for conversion
    useOpenVINOConversion: str = None
    # A SHORTCUT FOR SEVERAL PARAMETERS
    # This kind of config will
    # - setup runtimeOverwrite for CUDA EP and others
    #   + the previous EP is used for EPContextBinaryGeneator by PythonEnvironment
    # - do not support cpu evaluation
    # - setup executeRuntimeFeatures, evalRuntimeFeatures
    isQNNLLM: bool = None
    runtimeOverwrite: RuntimeOverwrite = None
    executeRuntimeFeatures: list[RuntimeFeatureEnum] = None
    evalRuntimeFeatures: list[RuntimeFeatureEnum] = None

    # it means default template does not use it
    # for Cpu, None means add
    addCpu: bool = None
    addAmdNpu: ADMNPUConfig = None

    runtime: Parameter = None
    sections: list[Section]

    @staticmethod
    def Read(parameterFile: str):
        print(f"Process {parameterFile}")
        GlobalVars.configCheck += 1
        with open(parameterFile, 'r', encoding='utf-8') as file:
            parameterContent = file.read()
        modelParameter = ModelParameter.model_validate_json(parameterContent, strict=True)
        modelParameter._file = parameterFile
        modelParameter._fileContent = parameterContent
        return modelParameter

    def Check(self, templates: Dict[str, Parameter], oliveJson: Any, modelList: ModelList):
        if not self.sections:
            print(f"{self._file} should have sections")
            GlobalVars.hasError()
            return
        
        # setup useModelBuilder
        modelBuilder = [k for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] == OlivePassNames.ModelBuilder]
        if modelBuilder:
            self.useModelBuilder = modelBuilder[0]
            self.isLLM = True

        # setup useOpenVINOConversion
        openVINOConversion = [k for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] == OlivePassNames.OpenVINOConversion]
        if openVINOConversion:
            self.useOpenVINOConversion = openVINOConversion[0]

        if self.useModelBuilder and self.useOpenVINOConversion:
            print(f"{self._file} should not have both useModelBuilder and useOpenVINOConversion")
            GlobalVars.hasError()
            return

        # TODO Add Convert section
        if self.sections[0].phase == PhaseTypeEnum.Conversion:
            self.sections = self.sections[1:]
        self.sections.insert(0, Section(
            autoGenerated=True,
            name="Convert",
            phase=PhaseTypeEnum.Conversion,
            parameters=[],
        ))
        
        if self.isQNNLLM:
            self.addCpu = False

        # Add runtime
        syskey, system = list(oliveJson[OlivePropertyNames.Systems].items())[0]
        currentEp = system[OlivePropertyNames.Accelerators][0][OlivePropertyNames.ExecutionProviders][0]
        runtimeValues = [currentEp]
        runtimeDisplayNames = [GlobalVars.epToName[currentEp]]
        runtimeActions = None
        
        if self.addAmdNpu and currentEp != EPNames.VitisAIExecutionProvider.value:
            runtimeValues.append(EPNames.VitisAIExecutionProvider)
            runtimeDisplayNames.append(GlobalVars.epToName[EPNames.VitisAIExecutionProvider.value])
            evaluatorName = oliveJson[OlivePropertyNames.Evaluator]
            if evaluatorName and self.addAmdNpu.inferenceSettings:
                if runtimeActions is None:
                    runtimeActions = [[] for _ in range(len(runtimeValues))]
                else:
                    runtimeActions.append([])
                metricsNum = len(pydash.get(oliveJson, f"{OlivePropertyNames.Evaluators}.{evaluatorName}.{OlivePropertyNames.Metrics}"))
                for i in range(metricsNum):
                    runtimeActions[-1].append(ParameterAction(
                        path=f"{OlivePropertyNames.Evaluators}.{evaluatorName}.{OlivePropertyNames.Metrics}[{i}].{OlivePropertyNames.UserConfig}",
                        type=ParameterActionTypeEnum.Insert,
                        value={
                            "inference_settings": {
                                "onnx": self.addAmdNpu.inferenceSettings,
                            }
                        }
                    ))

        # CPU always last
        if self.addCpu != False and currentEp != EPNames.CPUExecutionProvider.value:
            runtimeValues.append(EPNames.CPUExecutionProvider)
            runtimeDisplayNames.append(GlobalVars.epToName[EPNames.CPUExecutionProvider.value])
            if runtimeActions is not None:
                runtimeActions.append([])
        
        self.runtime = Parameter(
            autoGenerated=True,
            name="Evaluate on",
            type=ParameterTypeEnum.Enum,
            values=runtimeValues,
            displayNames=runtimeDisplayNames,
            path=f"{OlivePropertyNames.Systems}.{syskey}.accelerators.0.execution_providers.0",
            readOnly=False,)
        self.runtime.actions = runtimeActions
        if not self.runtime.Check(False, oliveJson, modelList):
            print(f"{self._file} runtime has error")
            GlobalVars.hasError()

        # Add runtime overwrite
        if self.isQNNLLM:
            if not system[OlivePropertyNames.Type] == "PythonEnvironment":
                print(f"{self._file}'s olive json does not use PythonEnvironment")
                GlobalVars.hasError()
            self.runtimeOverwrite = RuntimeOverwrite(
                autoGenerated=True,
                pyEnvPath=f"{OlivePropertyNames.Systems}.{syskey}.{OlivePropertyNames.PythonEnvironmentPath}",
                executeEp=EPNames.CUDAExecutionProvider,
                evaluateUsedInExecute=True,)
            if not self.runtimeOverwrite.Check(oliveJson):
                print(f"{self._file} runtime overwrite has error")
                GlobalVars.hasError()
            self.executeRuntimeFeatures = [RuntimeFeatureEnum.AutoGptq]
            self.evalRuntimeFeatures = [RuntimeFeatureEnum.Nightly]

        for i, section in enumerate(self.sections):
            # Add conversion toggle
            if section.phase == PhaseTypeEnum.Conversion:
                if self.useModelBuilder:
                    conversion = self.useModelBuilder
                elif self.useOpenVINOConversion:
                    conversion = self.useOpenVINOConversion
                else:
                    conversion = [k for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] == OlivePassNames.OnnxConversion][0]
                conversionPath = f"{OlivePropertyNames.Passes}.{conversion}"
                section.toggle = Parameter(
                    autoGenerated=True,
                    name="Convert to ONNX format",
                    type=ParameterTypeEnum.Bool,
                    path=conversionPath,
                    actions=[[], []],
                    readOnly=True)

            # Add quantization toggle
            elif section.phase == PhaseTypeEnum.Quantization:
                toggleReadOnly = None
                actions = []
                if self.useModelBuilder:
                    quantize = self.useModelBuilder
                    toggleReadOnly = True
                elif self.useOpenVINOConversion:
                    quantize = self.useOpenVINOConversion
                    toggleReadOnly = True
                else:
                    quantize = [k for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] in
                                [OlivePassNames.OnnxQuantization, OlivePassNames.OnnxStaticQuantization, OlivePassNames.OnnxDynamicQuantization]][0]
                    conversion = [(k, v) for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] == OlivePassNames.OnnxConversion][0]
                    actions = [ParameterAction(path=f"{OlivePropertyNames.Passes}", type=ParameterActionTypeEnum.Update, value={conversion[0]:conversion[1]})]
                quantizePath = f"{OlivePropertyNames.Passes}.{quantize}"
                section.toggle = Parameter(
                    autoGenerated=True,
                    name="Quantize model",
                    type=ParameterTypeEnum.Bool,
                    path=quantizePath,
                    readOnly=toggleReadOnly,
                    actions=[[], actions])

            # Add evaluation toggle
            elif section.phase == PhaseTypeEnum.Evaluation:
                action = ParameterAction(path=OlivePropertyNames.Evaluator, type=ParameterActionTypeEnum.Delete)
                section.toggle = Parameter(
                    autoGenerated=True,
                    name="Evaluate model performance",
                    type=ParameterTypeEnum.Bool,
                    path=OlivePropertyNames.Evaluator,
                    actions=[[], [action]])

            if not section.Check(templates, self._file, i, oliveJson, modelList):
                print(f"{self._file} section {i} has error")
                GlobalVars.hasError()

        # Phase check
        allPhases = [section.phase for section in self.sections]
        if len(allPhases) == 1 and allPhases[0] == PhaseTypeEnum.Conversion:
            pass
        elif len(allPhases) == 2 and allPhases[0] == PhaseTypeEnum.Conversion and allPhases[1] in [PhaseTypeEnum.Quantization, PhaseTypeEnum.Evaluation]:
            pass
        elif len(allPhases) == 3 and allPhases[0] == PhaseTypeEnum.Conversion and allPhases[1] == PhaseTypeEnum.Quantization and allPhases[2] == PhaseTypeEnum.Evaluation:
            pass
        else:
            print(f"{self._file} has wrong phases {allPhases}")
            GlobalVars.hasError()

        if PhaseTypeEnum.Evaluation in allPhases and PhaseTypeEnum.Quantization in allPhases and len(oliveJson[OlivePropertyNames.DataConfigs]) != 2:
            print(f"{self._file}'s olive json should have two data configs for evaluation")
            GlobalVars.hasError()

        newContent = self.model_dump_json(indent=4, exclude_none=True)
        if newContent != self._fileContent:
            with open(self._file, 'w', encoding='utf-8') as file:
                file.write(newContent)


def readCheckOliveConfig(oliveJsonFile: str, modelParameter: ModelParameter):
    """
    This will set phases to modelParameter
    """
    print(f"Process {oliveJsonFile}")
    with open(oliveJsonFile, 'r', encoding='utf-8') as file:
        oliveJson = json.load(file)

    # check if engine is in oliveJson
    if OlivePropertyNames.Engine in oliveJson:
        print(f"{oliveJsonFile} has engine. Should place in the root instead")
        GlobalVars.hasError()
        return
    
    if OlivePropertyNames.Evaluator in oliveJson and not isinstance(oliveJson[OlivePropertyNames.Evaluator], str):
        print(f"{oliveJsonFile} evaluator property should be str")
        GlobalVars.hasError()
        return
    
    # check if has more than one systems and more than one accelerators
    if OlivePropertyNames.Systems not in oliveJson or len(oliveJson[OlivePropertyNames.Systems]) != 1:
        print(f"{oliveJsonFile} should have only one system")
        GlobalVars.hasError()
        return
    systemK, systemV = list(oliveJson[OlivePropertyNames.Systems].items())[0]
    accelerators = systemV[OlivePropertyNames.Accelerators]
    if len(accelerators) != 1:
        print(f"{oliveJsonFile} should have only one accelerator")
        GlobalVars.hasError()
        return
    eps = accelerators[0][OlivePropertyNames.ExecutionProviders]
    if len(eps) != 1:
        print(f"{oliveJsonFile} should have only one execution provider")
        GlobalVars.hasError()
        return
    if eps[0] not in GlobalVars.epToName:
        print(f"{oliveJsonFile} has wrong execution provider {eps[0]}")
        GlobalVars.hasError()
        return
    
    # TODO check host
    # check target
    if OlivePropertyNames.Target not in oliveJson or oliveJson[OlivePropertyNames.Target] != systemK:
        print(f"{oliveJsonFile} target should be {systemK}")
        GlobalVars.hasError()
        return

    jsonUpdated = False

    # cache / output / evaluate_input_model
    if OlivePropertyNames.CacheDir not in oliveJson or oliveJson[OlivePropertyNames.CacheDir] != "cache":
        oliveJson[OlivePropertyNames.CacheDir] = "cache"
        jsonUpdated = True

    if OlivePropertyNames.OutputDir not in oliveJson or not str(oliveJson[OlivePropertyNames.OutputDir]).startswith("model/"):
        print(f"{oliveJsonFile} should have use model/XXX as {OlivePropertyNames.OutputDir}")
        GlobalVars.hasError()

    if OlivePropertyNames.EvaluateInputModel not in oliveJson or oliveJson[OlivePropertyNames.EvaluateInputModel]:
        oliveJson[OlivePropertyNames.EvaluateInputModel] = False
        jsonUpdated = True

    # update save_as_external_data
    supportedPasses = [v for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] in 
                       [OlivePassNames.OnnxConversion, OlivePassNames.OnnxQuantization, OlivePassNames.OnnxStaticQuantization, OlivePassNames.OnnxDynamicQuantization]]
    for conversionPass in supportedPasses:
        if OlivePropertyNames.ExternalData not in conversionPass or not conversionPass[OlivePropertyNames.ExternalData]:
            conversionPass[OlivePropertyNames.ExternalData] = True
            jsonUpdated = True

    if jsonUpdated:
        with open(oliveJsonFile, 'w', encoding='utf-8') as file:
            json.dump(oliveJson, file, indent=4)
        print(f"{oliveJsonFile} has been updated")

    return oliveJson


def readCheckIpynb(ipynbFile: str, modelItems: dict[str, ModelParameter]):
    """
    Note this return exists or not, not valid or not
    """
    if os.path.exists(ipynbFile):
        with open(ipynbFile, 'r', encoding='utf-8') as file:
            ipynbContent = file.read()
        for name, modelParameter in modelItems.items():
            testPath = outputModelRelativePath
            if modelParameter.useModelBuilder:
                testPath = outputModelModelBuilderPath
            if testPath not in ipynbContent:
                print(f"{ipynbFile} does not have '{testPath}' for {name}, please use it as input")
                GlobalVars.hasError()
            
            if not modelParameter.useModelBuilder and importOnnxruntime not in ipynbContent:
                print(f"{ipynbFile} does not have '{importOnnxruntime}' for {name}, please use it as import")
                GlobalVars.hasError()
            
        return True
    return False


# Copy

class Replacement(BaseModel):
    find: str
    replace: str | Any
    type: ReplaceTypeEnum = ReplaceTypeEnum.String


class Copy(BaseModel):
    src: str
    dst: str
    replacements: list[Replacement] = None


class CopyConfig(BaseModel):
    copies: list[Copy] = None

    def process(self, modelVerDir: str):
        if not self.copies:
            return
        for copy in self.copies:
            src = os.path.join(modelVerDir, copy.src)
            dst = os.path.join(modelVerDir, copy.dst)
            if not os.path.exists(src):
                print(f"{src} does not exist")
                GlobalVars.hasError()
                continue
            shutil.copy(src, dst)
            if copy.replacements:
                stringReplacements = [repl for repl in copy.replacements if repl.type == ReplaceTypeEnum.String]
                if stringReplacements:
                    with open(dst, 'r', encoding='utf-8') as file:
                        content = file.read()
                    for replacement in stringReplacements:
                        if GlobalVars.verbose: print(replacement.find)
                        if replacement.find not in content:
                            print(f"Not in dst file {dst}: {replacement.find}")
                            GlobalVars.hasError()
                            continue
                        content = content.replace(replacement.find, replacement.replace)
                    with open(dst, 'w', encoding='utf-8') as file:
                        file.write(content)
                pathReplacements = [repl for repl in copy.replacements if repl.type == ReplaceTypeEnum.Path or repl.type == ReplaceTypeEnum.PathAdd]
                if pathReplacements:
                    with open(dst, 'r', encoding='utf-8') as file:
                        jsonObj = json.load(file)
                    for replacement in pathReplacements:
                        if GlobalVars.verbose: print(replacement.find)
                        target = pydash.get(jsonObj, replacement.find)
                        if replacement.type == ReplaceTypeEnum.Path and target is None or replacement.type == ReplaceTypeEnum.PathAdd and target:
                            print(f"Not match type in dst json {dst}: {replacement.find}")
                            GlobalVars.hasError()
                            continue
                        pydash.set_(jsonObj, replacement.find, replacement.replace)
                    with open(dst, 'w', encoding='utf-8') as file:
                        json.dump(jsonObj, file, indent=4)


def check_case(path: Path) -> bool:
    path = Path(path)
    try:
        abs_path = path.resolve(strict=False)
    except Exception:
        return False

    if str(path) != str(abs_path):
        print(str(path))
        print(str(abs_path))
        return False
    return True


def main():
    # need to resolve due to d:\ vs D:\
    configDir = str(Path(os.path.dirname(os.path.dirname(__file__))).resolve(strict=False))
    # get model list
    modelList = ModelList.Read(configDir)
    # check parameter template
    parameterTemplate = readCheckParameterTemplate(os.path.join(configDir, "parameter_template.json"))
    # check each model
    for model in modelList.allModels():
        if model.id and model.status == ModelStatusEnum.Ready:
            modelDir = os.path.join(configDir, model.id)

            if not check_case(modelDir):
                print(f"Model folder does not exist, or check if case matches between model.id {model.id} and model folder.")
                GlobalVars.hasError()

            # get all versions
            allVersions = [int(name) for name in os.listdir(modelDir) if os.path.isdir(os.path.join(modelDir, name))]
            allVersions.sort()            
            model.version = allVersions[-1]
            # check if version is continuous
            if allVersions[0] != 1 or allVersions[-1] != len(allVersions):
                print(f"{modelDir} has wrong versions {allVersions}")
                GlobalVars.hasError()

            # process each version
            for version in allVersions:
                # deep copy model for version usage
                modelInVersion = copy.deepcopy(model)
                modelInVersion.version = version
                modelVerDir = os.path.join(modelDir, str(version))
                # process copy
                copyConfigFile = os.path.join(modelVerDir, "_copy.json.config")
                if os.path.exists(copyConfigFile):
                    with open(copyConfigFile, 'r', encoding="utf-8") as file:
                        copyConfigContent = file.read()
                    copyConfig = CopyConfig.model_validate_json(copyConfigContent, strict=True)
                    copyConfig.process(modelVerDir)

                # get model space config
                modelSpaceConfig = ModelProjectConfig.Read(os.path.join(modelVerDir, "model_project.config"))
                # check md
                mdFile = os.path.join(modelVerDir, "README.md")
                if not os.path.exists(mdFile):
                    print(f"{mdFile} not exists")
                    GlobalVars.hasError()
                # check requirement.txt
                requirementFile = os.path.join(modelVerDir, "requirements.txt")
                if not os.path.exists(requirementFile):
                    print(f"{requirementFile} not exists. Copy the template one")
                    GlobalVars.hasError()
                    shutil.copy(os.path.join(configDir, "requirements.md"), requirementFile)
                # copy .gitignore
                gitignoreFile = os.path.join(modelVerDir, ".gitignore")
                if not os.path.exists(gitignoreFile):
                    print(f"{gitignoreFile} not exists. Copy the template one")
                # always replace with latest
                shutil.copy(os.path.join(configDir, "gitignore.md"), os.path.join(modelVerDir, ".gitignore"))
                # check ipynb
                sharedIpynbFile = os.path.join(modelVerDir, "inference_sample.ipynb")
                hasSharedIpynb = os.path.exists(sharedIpynbFile)
                workflowsAgainstShared: dict[str, ModelParameter] = {}
                
                if modelSpaceConfig.modelInfo:
                    modelSpaceConfig.modelInfo.id = modelInVersion.id
                else:
                    modelSpaceConfig.modelInfo = ModelInfoProject(id=modelInVersion.id)
                for i, modelItem in enumerate(modelSpaceConfig.workflows):
                    # set template
                    modelItem.template = model.id
                    modelItem.version = modelInVersion.version
                    modelItem.templateName = os.path.basename(modelItem.file)[:-5]

                    # read parameter
                    modelParameter = ModelParameter.Read(os.path.join(modelVerDir, f"{modelItem.file}.config"))

                    # check olive json
                    oliveJsonFile = os.path.join(modelVerDir, modelItem.file)
                    oliveJson = readCheckOliveConfig(oliveJsonFile, modelParameter)

                    # check parameter
                    modelParameter.Check(parameterTemplate, oliveJson, modelList)

                    # check ipynb
                    ipynbFile = os.path.join(modelVerDir, f"{modelItem.templateName}_inference_sample.ipynb")
                    hasSpecialIpynb = readCheckIpynb(ipynbFile, {modelItem.name: modelParameter})
                    if not hasSpecialIpynb:
                        if not hasSharedIpynb:
                            print(f"{ipynbFile} nor {sharedIpynbFile} not exists.")
                            GlobalVars.hasError()
                        else:
                            workflowsAgainstShared[modelItem.name] = modelParameter
                readCheckIpynb(sharedIpynbFile, workflowsAgainstShared)
                    
                modelSpaceConfig.Check(modelInVersion)
    modelList.Check()

    errorMsg = ''

    print(f"Total {GlobalVars.configCheck} config files checked with total {GlobalVars.pathCheck} path checks")
    # We add this test to make sure the sanity check is working: i.e. paths are checked and files are checked
    # So the numbers need to be updated whenever the config files change
    if GlobalVars.pathCheck != 207 or GlobalVars.configCheck != 17:
        errorMsg += "Please update line above to reflect config changes!\n"

    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=configDir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # If the output is not empty, there are uncommitted changes
    if bool(result.stdout.strip()):
        errorMsg += "Please commit changes!\n"
    if GlobalVars.SomethingError:
        errorMsg += "Please fix errors!\n"
    if errorMsg:
        raise BaseException(errorMsg)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Check model lab configs")
    argparser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    args = argparser.parse_args()
    GlobalVars.verbose = args.verbose
    main()
