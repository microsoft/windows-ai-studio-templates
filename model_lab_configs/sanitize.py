from __future__ import annotations
import shutil
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

class OlivePropertyNames:
    Engine = "engine"
    Passes = "passes"
    Evaluator = "evaluator"
    Type = "type"
    ExternalData = "save_as_external_data"

outputModelRelativePath = "./output_model/model/model.onnx"

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


class RuntimeEnum(Enum):
    QNN = "QNN"

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
    NotSet = "notSet"

class ParameterCheckTypeEnum(Enum):
    NotSet = "notSet"
    Exist = "exist"
    NotExist = "notExist"

class ParameterActionTypeEnum(Enum):
    NotSet = "notSet"
    Upsert = "upsert"
    Delete = "delete"

class PhaseTypeEnum(Enum):
    Conversion = "Conversion"
    Quantization = "Quantization"
    Evaluation = "Evaluation"

# Global vars

class GlobalVars:
    hasChange = False
    hasError = False
    phaseToSection = {
        PhaseTypeEnum.Conversion: "Convert",
        PhaseTypeEnum.Quantization: "Quantize",
        PhaseTypeEnum.Evaluation: "Evaluate"
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
    status: ModelStatusEnum = ModelStatusEnum.Coming
    version: int = -1

    def Check(self):
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
                GlobalVars.hasError = True      
        newContent = self.model_dump_json(indent=4)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)
            GlobalVars.hasChange = True

# Parameter

def checkPath(path: str, oliveJson: Any):
    if GlobalVars.verbose: print(path)
    if pydash.get(oliveJson, path) is None:
        print(f"Not in olive json: {path}")
        return False
    return True


class ParameterCheck(BaseModel):
    type: ParameterCheckTypeEnum = ParameterCheckTypeEnum.NotSet
    path: str = ""

    def check(self, oliveJson: Any):
        if self.type == ParameterCheckTypeEnum.NotSet:
            return False
        if not self.path:
            return False
        if not checkPath(self.path, oliveJson):
            return False
        return True


class ParameterAction(BaseModel):
    type: ParameterActionTypeEnum = ParameterActionTypeEnum.NotSet
    path: str = ""
    value: str | int | bool | float | None = None

    def check(self, oliveJson: Any):
        if self.type == ParameterActionTypeEnum.NotSet:
            return False
        if not self.path:
            return False
        if self.type == ParameterActionTypeEnum.Upsert and not self.value:
            return False
        if not checkPath(self.path, oliveJson):
            return False
        return True


# TODO add displayNames for values
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
    name: str = ""
    description: str = ""
    type: ParameterTypeEnum = ParameterTypeEnum.NotSet
    path: str = ""
    values: list[str] = []
    # 1st level is Parameter and 2nd level is str in templates
    template: Parameter | str = ""
    checks: list[ParameterCheck] = []
    actions: list[list[ParameterAction]] = []

    def Check(self, isTemplate: bool, oliveJson: Any = None):
        if isTemplate:
            if self.template:
                return False
            return True

        if not self.name:
            return False
        #if not self.description:
        #    return False
        if not self.type or self.type == ParameterTypeEnum.NotSet:
            return False
        if self.type != ParameterTypeEnum.Bool and self.type != ParameterTypeEnum.Enum:            
            if not self.path:
                return False
            elif not checkPath(self.path, oliveJson):
                return False
            elif self.values or self.checks or self.actions:
                return False
        else:
            expectedLength = 2
            if self.type == ParameterTypeEnum.Enum:
                expectedLength = max(len(self.values), len(self.checks), len(self.actions))
            
            if self.path and not self.checks:
                pass
            elif not self.path and len(self.checks) == expectedLength:
                pass
            else:
                print(f"Path and checks mismatch")
                return False

            if (len(self.values) == expectedLength or (not self.values and self.type == ParameterTypeEnum.Bool)) and not self.actions:
                pass
            elif not self.values and len(self.actions) == expectedLength:
                pass
            else:
                print(f"Values and actions mismatch")
                return False

            if self.path and not checkPath(self.path, oliveJson):
                return False
            for i, check in enumerate(self.checks):
                if not check.check(oliveJson):
                    print(f"Check {i} has error")
                    return False
            for i, actions in enumerate(self.actions):
                for j, action in enumerate(actions):
                    if not action.check(oliveJson):
                        print(f"Action {i} {j} has error")
                        return False                  
        return True

    def clearValue(self):
        self.name = ""
        self.description = ""
        self.type = ParameterTypeEnum.NotSet
        self.values = []
        self.path = ""
        self.actions = []
    
    # template ignored
    def applyTemplate(self, template: Parameter):
        if not self.name:
            self.name = template.name
        if not self.description:
            self.description = template.description
        if self.type == ParameterTypeEnum.NotSet:
            self.type = template.type
        if not self.values:
            self.values = template.values
        if not self.path:
            self.path = template.path
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
            GlobalVars.hasError = True
    newContent = adapter.dump_json(parameters, indent=4).decode('utf-8')
    if newContent != fileContent:
        with open(filePath, 'w') as file:
            file.write(newContent)
        GlobalVars.hasChange = True
    return parameters

# Model

class WorkflowItem(BaseModel):
    name: str
    file: str
    template: str = ""
    version: int = -1
    templateName: str = ""
    phases: list[PhaseTypeEnum] = []

    def Check(self):
        if not self.name:
            return False
        if not self.file:
            return False
        if not self.template:
            return False
        if self.version == -1:
            return False
        if not self.templateName:
            return False
        if not self.phases:
            return False
        return True

# TODO: add model metadata from model list
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
                GlobalVars.hasError = True
        
        if not self.modelInfo.Check():
            print(f"{self._file} modelInfo has error")
            GlobalVars.hasError = True

        newContent = self.model_dump_json(indent=4)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)
            GlobalVars.hasChange = True

# Model Parameter

# toggle: usually used for on/off switch
class Section(BaseModel):
    name: str
    description: str = ""
    parameters: list[Parameter]
    toggle: Parameter | None = None

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
                    GlobalVars.hasError = True
                    continue
                parameter.clearValue()
                parameter.applyTemplate(template)
                parameter.applyTemplate(templates[template.template])
            if not parameter.Check(False, oliveJson):
                print(f"{_file} section {sectionId} parameter {i} has error")
                GlobalVars.hasError = True
        
        if self.toggle:
            if self.toggle.type != ParameterTypeEnum.Bool:
                print(f"{_file} section {sectionId} toggle must use bool")
                return False
            if not self.toggle.Check(False, oliveJson):
                print(f"{_file} section {sectionId} toggle has error")
                GlobalVars.hasError = True

        return True
    

class ModelParameter(BaseModel):
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
            GlobalVars.hasError = True

        for i, section in enumerate(self.sections):
            # TODO hardcoded name for UI
            if section.name != GlobalVars.phaseToSection[modelItem.phases[i + 1]]:
                section.name = GlobalVars.phaseToSection[modelItem.phases[i + 1]]
                print(f"{self._file} section {i} has wrong name {section.name} compared with phase {modelItem.phases[i]}")
            
            # Set quantization toggle
            if section.name == GlobalVars.phaseToSection[PhaseTypeEnum.Quantization]:
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
                GlobalVars.hasError = True          

        newContent = self.model_dump_json(indent=4)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)
            GlobalVars.hasChange = True

def readCheckOliveConfig(oliveJsonFile: str, modelItem: WorkflowItem):
    print(f"Process {oliveJsonFile}")
    with open(oliveJsonFile, 'r') as file:
        oliveJson = json.load(file)
    
    # check if engine is in oliveJson
    if OlivePropertyNames.Engine in oliveJson:
        print(f"{oliveJsonFile} has engine. Should place in the root instead")
        GlobalVars.hasError = True
        return
    
    if OlivePropertyNames.Evaluator in oliveJson and not isinstance(oliveJson[OlivePropertyNames.Evaluator], str):
        print(f"{oliveJsonFile} evaluator property should be str")
        GlobalVars.hasError = True
        return

    # get phases from oliveJson
    phases = []
    all_passes = [v[OlivePropertyNames.Type] for _, v in oliveJson[OlivePropertyNames.Passes].items()]
    if OlivePassNames.OnnxConversion in all_passes:
        phases.append(PhaseTypeEnum.Conversion)
    if OlivePassNames.OnnxQuantization in all_passes or OlivePassNames.OnnxStaticQuantization in all_passes or OlivePassNames.OnnxDynamicQuantization in all_passes:
        phases.append(PhaseTypeEnum.Quantization)
    if OlivePropertyNames.Evaluator in oliveJson and oliveJson[OlivePropertyNames.Evaluator]:
        phases.append(PhaseTypeEnum.Evaluation)
    # TODO hardcoded
    if PhaseTypeEnum.Conversion != phases[0]:
        print(f"{oliveJsonFile} missing Conversion phase")
        GlobalVars.hasError = True
    if PhaseTypeEnum.Quantization != phases[1]:
        print(f"{oliveJsonFile} missing Quantization phase")
        GlobalVars.hasError = True
    modelItem.phases = phases
    
    jsonUpdated = False

    # update save_as_external_data
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
        GlobalVars.hasChange = True

    return oliveJson


def readCheckIpynb(ipynbFile: str):
    """
    Note this return exists or not, not valid or not
    """
    if os.path.exists(ipynbFile):
        with open(ipynbFile, 'r') as file:
            ipynbContent = file.read()
        if outputModelRelativePath not in ipynbContent:
            print(f"{ipynbFile} does not have '{outputModelRelativePath}', please use it as input")
            GlobalVars.hasError = True
        return True
    return False


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
                GlobalVars.hasError = True

            # process each version
            for version in allVersions:
                # deep copy model for version usage
                modelInVersion = copy.deepcopy(model)
                modelInVersion.version = version
                modelVerDir = os.path.join(modelDir, str(version))
                # get model space config
                modelSpaceConfig = ModelProjectConfig.Read(os.path.join(modelVerDir, "model_project.config"))
                # check md
                mdFile = os.path.join(modelVerDir, "README.md")
                if not os.path.exists(mdFile):
                    print(f"{mdFile} not exists")
                    GlobalVars.hasError = True
                # check requirement.txt
                requirementFile = os.path.join(modelVerDir, "requirements.txt")
                if not os.path.exists(requirementFile):
                    print(f"{requirementFile} not exists. Copy the template one")
                    GlobalVars.hasError = True
                    shutil.copy(os.path.join(configDir, "requirements.md"), requirementFile)
                # copy .gitignore
                gitignoreFile = os.path.join(modelVerDir, ".gitignore")
                if not os.path.exists(gitignoreFile):
                    print(f"{gitignoreFile} not exists. Copy the template one")
                    GlobalVars.hasChange = True
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
                    modelItem.templateName = modelItem.file[:-5]

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
                        if not readCheckIpynb(ipynbFile):
                            print(f"{ipynbFile} nor {sharedIpynbFile} not exists.")
                            GlobalVars.hasError = True
                    
                modelSpaceConfig.Check()
    modelList.Check()
    if GlobalVars.hasChange:
        print("Please commit changes")
    if GlobalVars.hasError:
        print("Please fix errors")
    if GlobalVars.hasChange or GlobalVars.hasError:
        raise


if __name__ == '__main__':
    main()
