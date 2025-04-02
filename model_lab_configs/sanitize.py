from __future__ import annotations
import shutil
import subprocess
from typing import Any, Dict
from pydantic import BaseModel, TypeAdapter
import os
from enum import Enum
import copy
import pydash
import json

# Constants

class OlivePassNames:
    OnnxConversion = "OnnxConversion"
    OnnxQuantization = "OnnxQuantization"
    OnnxStaticQuantization = "OnnxStaticQuantization"
    OnnxDynamicQuantization = "OnnxDynamicQuantization"
    ModelBuilder = "ModelBuilder"

class OlivePropertyNames:
    Engine = "engine"
    Passes = "passes"
    Evaluator = "evaluator"
    Type = "type"
    ExternalData = "save_as_external_data"
    Systems = "systems"
    Accelerators = "accelerators"
    ExecutionProviders = "execution_providers"
    DataConfigs = "data_configs"

outputModelRelativePath = "./model/model.onnx"
outputModelModelBuilderPath = "./model"

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

class RuntimeEnum(Enum):
    QNN = "QNN"
    IntelNPU = "IntelNPU"

class ArchitectureEnum(Enum):
    Transformer = "Transformer"
    CNN = "CNN"
    Diffusion = "Diffusion"

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
    Upsert = "upsert"
    Delete = "delete"

class PhaseTypeEnum(Enum):
    Conversion = "Conversion"
    Quantization = "Quantization"
    Evaluation = "Evaluation"

class ReplaceTypeEnum(Enum):
    String = "string"
    Path = "path"
    PathAdd = "pathAdd"

# Global vars

class GlobalVars:  
    SomethingError = False
    @classmethod
    def hasError(cls):
        cls.SomethingError = True

    phaseToSection = {
        PhaseTypeEnum.Conversion: "Convert",
        PhaseTypeEnum.Quantization: "Quantize",
        PhaseTypeEnum.Evaluation: "Evaluate"
    }
    epToName = {
        "QNNExecutionProvider": "Qualcomm NPU",
        "OpenVINOExecutionProvider": "Intel NPU",
        "CPUExecutionProvider": "CPU",
    }
    verbose = True


# Model List

class ModelInfo(BaseModel):
    displayName: str
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

    @staticmethod
    def Read(scriptFolder: str):
        modelListFile = os.path.join(scriptFolder, "model_list.json")
        print(f"Process {modelListFile}")
        with open(modelListFile, 'r') as file:
            modelListContent = file.read()
        modelList = ModelList.model_validate_json(modelListContent, strict=True)
        modelList._file = modelListFile
        modelList._fileContent = modelListContent
        return modelList
    
    # Check after set version
    def Check(self):
        for i, model in enumerate(self.models):
            if not model.Check():
                print(f"{self._file} model {i} has error")
                GlobalVars.hasError()
        newContent = self.model_dump_json(indent=4, exclude_none=True)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)

# Parameter

def checkPath(path: str, oliveJson: Any):
    if GlobalVars.verbose: print(path)
    if pydash.get(oliveJson, path) is None:
        print(f"Not in olive json: {path}")
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
    value: str | int | bool | float = None

    def check(self, oliveJson: Any):
        if not self.type:
            return False
        if not self.path:
            return False
        if self.type == ParameterActionTypeEnum.Upsert and not self.value:
            return False
        if not checkPath(self.path, oliveJson):
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
    name: str = None
    description: str = None
    type: ParameterTypeEnum = None
    displayNames: list[str] = None
    displayType: ParameterDisplayTypeEnum = None
    path: str = None
    values: list[str] = None
    checks: list[ParameterCheck] = None
    actions: list[list[ParameterAction]] = None
    fixed: bool = None
    # 1st level is Parameter and 2nd level is str in templates
    # always put template in the end
    template: Parameter | str = None

    def Check(self, isTemplate: bool, oliveJson: Any = None):
        if isTemplate:
            if self.template:
                return False
            return True

        if not self.name:
            return False
        #if not self.description:
        #    return False
        if not self.type:
            return False
        if self.type != ParameterTypeEnum.Bool and self.type != ParameterTypeEnum.Enum:            
            if not self.path:
                return False
            elif not checkPath(self.path, oliveJson):
                return False
            elif self.values or self.checks or self.actions or self.displayNames:
                print("Redandunt fields")
                return False
        else:
            expectedLength = 2
            lenValues = len(self.values) if self.values else 0
            lenChecks = len(self.checks) if self.checks else 0
            lenActions = len(self.actions) if self.actions else 0
            if self.type == ParameterTypeEnum.Enum:
                expectedLength = max(lenValues, lenChecks)
                if expectedLength == 0:
                    print("Enum should have values or checks")
                    return False
            
            # Display names
            if self.type == ParameterTypeEnum.Enum and self.checks and not self.displayNames:
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
            
            # path + values vs checks + actions
            if self.path and not self.checks:
                pass
            elif not self.path and lenChecks == expectedLength:
                pass
            else:
                print(f"Either Path or checks could be used")
                return False

            if (lenValues == expectedLength or (not self.values and self.type == ParameterTypeEnum.Bool)) and not self.actions:
                pass
            elif not self.values and lenActions == expectedLength:
                pass
            else:
                print(f"Either values or actions could be used")
                return False

            if self.path:
                if not checkPath(self.path, oliveJson):
                    return False
                if self.actions:
                    print("Path should not be used with actions")
                    return False
                # TODO more checks
                value = pydash.get(oliveJson, self.path)
                if self.values and value not in self.values:
                    print(f"Value {value} not in values")
                    return False
            else:
                for i, check in enumerate(self.checks):
                    if not check.check(oliveJson):
                        print(f"Check {i} has error")
                        return False
                for i, actions in enumerate(self.actions):
                    for j, action in enumerate(actions):
                        if not action.check(oliveJson):
                            print(f"Action {i} {j} has error")
                            return False
                if self.values:
                    print("Checks should not be used with values")
                    return False
        return True

    def clearValue(self):
        """
        Clear everything except template
        """
        self.name = None
        self.description = None
        self.type = None
        self.displayNames = None
        self.displayType = None
        self.path = None
        self.values = None
        self.checks = None
        self.actions = None
    
    def applyTemplate(self, template: Parameter):
        """
        Apply everything except template
        """
        if not self.name:
            self.name = template.name
        if not self.description:
            self.description = template.description
        if not self.type:
            self.type = template.type
        if not self.displayNames:
            self.displayNames = template.displayNames
        if not self.displayType:
            self.displayType = template.displayType
        if not self.path:
            self.path = template.path
        if not self.values:
            self.values = template.values
        if not self.checks:
            self.checks = template.checks
        if not self.actions:
            self.actions = template.actions


def readCheckParameterTemplate(filePath: str):
    print(f"Process {filePath}")
    with open(filePath, 'r') as file:
        fileContent = file.read()
    adapter = TypeAdapter(Dict[str, Parameter])
    parameters: Dict[str, Parameter] = adapter.validate_json(fileContent, strict=True)
    for key, parameter in parameters.items():
        if not parameter.Check(True):
            print(f"{filePath} parameter {key} has error")
            GlobalVars.hasError()
    newContent = adapter.dump_json(parameters, indent=4, exclude_none=True).decode('utf-8')
    if newContent != fileContent:
        with open(filePath, 'w') as file:
            file.write(newContent)
    return parameters

# Model

class WorkflowItem(BaseModel):
    name: str
    file: str
    template: str = None
    version: int = 0
    templateName: str = None
    phases: list[PhaseTypeEnum] = None
    useModelBuilder: bool = None

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
        if not self.phases:
            return False
        return True


class ModelProjectConfig(BaseModel):
    workflows: list[WorkflowItem]
    modelInfo: ModelInfo = None

    @staticmethod
    def Read(modelSpaceConfigFile: str):
        print(f"Process {modelSpaceConfigFile}")
        with open(modelSpaceConfigFile, 'r') as file:
            modelSpaceConfigContent = file.read()
        modelSpaceConfig = ModelProjectConfig.model_validate_json(modelSpaceConfigContent, strict=True)
        modelSpaceConfig._file = modelSpaceConfigFile
        modelSpaceConfig._fileContent = modelSpaceConfigContent
        return modelSpaceConfig

    # after template is set
    def Check(self):
        for i, model in enumerate(self.workflows):
            if not model.Check():
                print(f"{self._file} model {i} has error")
                GlobalVars.hasError()
        
        if not self.modelInfo.Check():
            print(f"{self._file} modelInfo has error")
            GlobalVars.hasError()

        newContent = self.model_dump_json(indent=4, exclude_none=True)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)

# Model Parameter

# toggle: usually used for on/off switch
class Section(BaseModel):
    name: str
    description: str = None
    parameters: list[Parameter]
    toggle: Parameter = None

    def Check(self, templates: Dict[str, Parameter], _file: str, sectionId: int, oliveJson: Any):
        if not self.name:
            return False
        #if not self.description:
        #    return False
        # TODO add place holder for General, Convert ?
        if not self.parameters:
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
            if not parameter.Check(False, oliveJson):
                print(f"{_file} section {sectionId} parameter {i} has error")
                GlobalVars.hasError()
        
        if self.toggle:
            if self.toggle.type != ParameterTypeEnum.Bool:
                print(f"{_file} section {sectionId} toggle must use bool")
                return False
            if not self.toggle.Check(False, oliveJson):
                print(f"{_file} section {sectionId} toggle has error")
                GlobalVars.hasError()

        return True
    

class ModelParameter(BaseModel):
    runtime: Parameter = None
    sections: list[Section]

    @staticmethod
    def Read(parameterFile: str):
        print(f"Process {parameterFile}")
        with open(parameterFile, 'r') as file:
            parameterContent = file.read()
        modelParameter = ModelParameter.model_validate_json(parameterContent, strict=True)
        modelParameter._file = parameterFile
        modelParameter._fileContent = parameterContent
        return modelParameter


    def Check(self, templates: Dict[str, Parameter], modelItem: WorkflowItem, oliveJson: Any):
        # Check sections to match phases
        # TODO hardcoded (with additional conversion phase)
        if len(self.sections) != len(modelItem.phases) - 1:
            print(f"{self._file} has wrong sections compared with phases {modelItem.phases}")
            GlobalVars.hasError()
        
        # Add runtime
        syskey, system = list(oliveJson[OlivePropertyNames.Systems].items())[0]
        currentEp = system[OlivePropertyNames.Accelerators][0][OlivePropertyNames.ExecutionProviders][0]
        self.runtime = Parameter(
            name="Evaluate on",
            type=ParameterTypeEnum.Enum,
            values=[currentEp],
            displayNames=[GlobalVars.epToName[currentEp]],
            path=f"{OlivePropertyNames.Systems}.{syskey}.accelerators.0.execution_providers.0",
            fixed=False,)
        if not self.runtime.Check(False, oliveJson):
            print(f"{self._file} runtime has error")
            GlobalVars.hasError()

        for i, section in enumerate(self.sections):
            # TODO hardcoded name for UI
            if section.name != GlobalVars.phaseToSection[modelItem.phases[i + 1]]:
                section.name = GlobalVars.phaseToSection[modelItem.phases[i + 1]]
                print(f"{self._file} section {i} has wrong name {section.name} compared with phase {modelItem.phases[i]}")
            
            # Set quantization toggle
            if section.name == GlobalVars.phaseToSection[PhaseTypeEnum.Quantization]:
                if modelItem.useModelBuilder:
                    # TODO modelbuilder
                    modelBuilder = [k for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] in [OlivePassNames.ModelBuilder]]
                    modelBuilderPath = f"{OlivePropertyNames.Passes}.{modelBuilder[0]}"
                    section.toggle = Parameter(
                        name="Quantize model",
                        type=ParameterTypeEnum.Bool,
                        fixed=True,
                        checks=[ParameterCheck(type=ParameterCheckTypeEnum.Exist, path=modelBuilderPath), ParameterCheck(type=ParameterCheckTypeEnum.NotExist, path=modelBuilderPath)],
                        actions=[[], []])
                else:
                    quantize = [k for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] in [OlivePassNames.OnnxQuantization, OlivePassNames.OnnxStaticQuantization, OlivePassNames.OnnxDynamicQuantization]]
                    quantizePath = f"{OlivePropertyNames.Passes}.{quantize[0]}"
                    not_conversion = [k for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] not in [OlivePassNames.OnnxConversion]]
                    actions = [ParameterAction(path=f"{OlivePropertyNames.Passes}.{k}", type=ParameterActionTypeEnum.Delete) for k in not_conversion]
                    section.toggle = Parameter(
                        name="Quantize model",
                        type=ParameterTypeEnum.Bool,
                        checks=[ParameterCheck(type=ParameterCheckTypeEnum.Exist, path=quantizePath), ParameterCheck(type=ParameterCheckTypeEnum.NotExist, path=quantizePath)],
                        actions=[[], actions])

            # Set evaluation toggle
            elif section.name == GlobalVars.phaseToSection[PhaseTypeEnum.Evaluation]:
                action = ParameterAction(path=OlivePropertyNames.Evaluator, type=ParameterActionTypeEnum.Delete)
                section.toggle = Parameter(
                    name="Evaluate model performance",
                    type=ParameterTypeEnum.Bool,
                    checks=[ParameterCheck(type=ParameterCheckTypeEnum.Exist, path=OlivePropertyNames.Evaluator), ParameterCheck(type=ParameterCheckTypeEnum.NotExist, path=OlivePropertyNames.Evaluator)],
                    actions=[[], [action]])

            if not section.Check(templates, self._file, i, oliveJson):
                print(f"{self._file} section {i} has error")
                GlobalVars.hasError()

        newContent = self.model_dump_json(indent=4, exclude_none=True)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)

def readCheckOliveConfig(oliveJsonFile: str, modelItem: WorkflowItem):
    print(f"Process {oliveJsonFile}")
    with open(oliveJsonFile, 'r') as file:
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
    
    # check if has more than one systems
    if OlivePropertyNames.Systems not in oliveJson or len(oliveJson[OlivePropertyNames.Systems]) != 1:
        print(f"{oliveJsonFile} should have only one system")
        GlobalVars.hasError()
        return
    accelerators = list(oliveJson[OlivePropertyNames.Systems].items())[0][1][OlivePropertyNames.Accelerators]
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

    # get phases from oliveJson
    phases = []
    all_passes = [v[OlivePropertyNames.Type] for _, v in oliveJson[OlivePropertyNames.Passes].items()]

    if modelItem.useModelBuilder:
        if OlivePassNames.ModelBuilder not in all_passes or OlivePassNames.OnnxConversion in all_passes:
            print(f"{oliveJsonFile} missing ModelBuilder phase")
            GlobalVars.hasError()
            return
        phases.append(PhaseTypeEnum.Conversion)
        phases.append(PhaseTypeEnum.Quantization)
    else:
        if OlivePassNames.OnnxConversion in all_passes:
            phases.append(PhaseTypeEnum.Conversion)
        if OlivePassNames.OnnxQuantization in all_passes or OlivePassNames.OnnxStaticQuantization in all_passes or OlivePassNames.OnnxDynamicQuantization in all_passes:
            phases.append(PhaseTypeEnum.Quantization)
    if OlivePropertyNames.Evaluator in oliveJson and oliveJson[OlivePropertyNames.Evaluator]:
        phases.append(PhaseTypeEnum.Evaluation)
    # TODO hardcoded
    if PhaseTypeEnum.Conversion != phases[0]:
        print(f"{oliveJsonFile} missing Conversion phase")
        GlobalVars.hasError()
    if PhaseTypeEnum.Quantization != phases[1]:
        print(f"{oliveJsonFile} missing Quantization phase")
        GlobalVars.hasError()
    modelItem.phases = phases
    
    # check evaluation
    if PhaseTypeEnum.Evaluation in modelItem.phases:
        if PhaseTypeEnum.Quantization in modelItem.phases and len(oliveJson[OlivePropertyNames.DataConfigs]) == 1:
            print(f"{oliveJsonFile} should have two data configs for evaluation")
            GlobalVars.hasError()

    jsonUpdated = False

    # update save_as_external_data
    if modelItem.useModelBuilder:
        pass
    else:
        conversionPass = [v for k, v in oliveJson[OlivePropertyNames.Passes].items() if v[OlivePropertyNames.Type] == OlivePassNames.OnnxConversion][0]
        if OlivePropertyNames.ExternalData not in conversionPass or not conversionPass[OlivePropertyNames.ExternalData]:
            conversionPass[OlivePropertyNames.ExternalData] = True
            jsonUpdated = True

        lastPass = [v for k, v in oliveJson[OlivePropertyNames.Passes].items()][-1]
        if OlivePropertyNames.ExternalData not in lastPass or not lastPass[OlivePropertyNames.ExternalData]:
            lastPass[OlivePropertyNames.ExternalData] = True
            jsonUpdated = True

    if jsonUpdated:
        with open(oliveJsonFile, 'w') as file:
            json.dump(oliveJson, file, indent=4)
        print(f"{oliveJsonFile} has been updated")

    return oliveJson


def readCheckIpynb(ipynbFile: str, modelItem: WorkflowItem = None):
    """
    Note this return exists or not, not valid or not
    """
    if os.path.exists(ipynbFile):
        with open(ipynbFile, 'r', encoding='utf-8') as file:
            ipynbContent = file.read()
        testPath = outputModelRelativePath
        if modelItem and modelItem.useModelBuilder:
            testPath = outputModelModelBuilderPath
        if testPath not in ipynbContent:
            print(f"{ipynbFile} does not have '{outputModelRelativePath}', please use it as input")
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


def main():
    configDir = os.path.dirname(__file__)
    # get model list
    modelList = ModelList.Read(configDir)
    # check parameter template
    parameterTemplate = readCheckParameterTemplate(os.path.join(configDir, "parameter_template.json"))
    # check each model
    for model in modelList.models:
        if model.id and model.status == ModelStatusEnum.Ready:
            modelDir = os.path.join(configDir, model.id)
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
                    with open(copyConfigFile, 'r') as file:
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
                sharedIpynb = readCheckIpynb(sharedIpynbFile)
                
                modelSpaceConfig.modelInfo = modelInVersion
                for i, modelItem in enumerate(modelSpaceConfig.workflows):
                    # set template
                    modelItem.template = model.id
                    modelItem.version = modelInVersion.version
                    modelItem.templateName = os.path.basename(modelItem.file)[:-5]

                    # check olive json
                    oliveJsonFile = os.path.join(modelVerDir, modelItem.file)
                    oliveJson = readCheckOliveConfig(oliveJsonFile, modelItem)

                    # check parameter
                    # read parameter
                    modelParameter = ModelParameter.Read(os.path.join(modelVerDir, f"{modelItem.file}.config"))
                    modelParameter.Check(parameterTemplate, modelItem, oliveJson)

                    # check ipynb
                    if not sharedIpynb:
                        ipynbFile = os.path.join(modelVerDir, f"{modelItem.templateName}_inference_sample.ipynb")
                        if not readCheckIpynb(ipynbFile, modelItem):
                            print(f"{ipynbFile} nor {sharedIpynbFile} not exists.")
                            GlobalVars.hasError()
                    
                modelSpaceConfig.Check()
    modelList.Check()

    errorMsg = ''
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=configDir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # If the output is not empty, there are uncommitted changes
    if bool(result.stdout.strip()):
        errorMsg += "Please commit changes!"
    if GlobalVars.SomethingError:
        errorMsg += "Please fix errors!"
    if errorMsg:
        raise BaseException(errorMsg)

if __name__ == '__main__':
    main()
