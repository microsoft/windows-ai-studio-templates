from __future__ import annotations
from typing import Dict
from pydantic import BaseModel, TypeAdapter
import os
from enum import Enum
import copy
import pydash
import json

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
    NotSet = "notSet"

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

class Parameter(BaseModel):
    name: str = ""
    description: str = ""
    type: ParameterTypeEnum = ParameterTypeEnum.NotSet
    values: list[str] = []
    # 1st level is Parameter and 2nd level is str in templates
    template: Parameter | str = None
    path: str = ""

    def Check(self, isTemplate: bool):
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
        if self.type == ParameterTypeEnum.Enum and not self.values:
            return False
        if not self.path:
            return False
        return True

    def clearValue(self):
        self.name = ""
        self.description = ""
        self.type = ParameterTypeEnum.NotSet
        self.values = []
        self.path = ""
    
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

class Section(BaseModel):
    name: str
    description: str = ""
    parameters: list[Parameter]

    def Check(self, templates: Dict[str, Parameter], _file: str, sectionId: int):
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


    def Check(self, templates: Dict[str, Parameter], modelItem: WorkflowItem):
        # TODO hardcoded
        if len(self.sections) != len(modelItem.phases) - 1:
            print(f"{self._file} has wrong sections compared with phases {modelItem.phases}")
            GlobalVars.hasError = True

        for i, section in enumerate(self.sections):
            # TODO hardcoded
            if section.name != GlobalVars.phaseToSection[modelItem.phases[i + 1]]:
                print(f"{self._file} section {i} has wrong name {section.name} compared with phase {modelItem.phases[i]}")
                GlobalVars.hasError = True
            if not section.Check(templates, self._file, i):
                print(f"{self._file} section {i} has error")
                GlobalVars.hasError = True
        
        newContent = self.model_dump_json(indent=4)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)
            GlobalVars.hasChange = True

def checkOliveConfig(oliveJsonFile: str, modelParameter: ModelParameter, modelItem: WorkflowItem):
    with open(oliveJsonFile, 'r') as file:
        oliveJson = json.load(file)
    for si, section in enumerate(modelParameter.sections):
        for i, parameter in enumerate(section.parameters):
            if pydash.get(oliveJson, parameter.path) is None:
                print(f"{oliveJsonFile} missing section {si} parameter {i}: {parameter.path}")
                GlobalVars.hasError = True
    
    if "engine" in oliveJson:
        print(f"{oliveJsonFile} has engine. Should place in the root instead")
        GlobalVars.hasError = True
        return

    # get phases from oliveJson
    phases = []
    all_passes = [v["type"] for _, v in oliveJson["passes"].items()]
    if "OnnxConversion" in all_passes:
        phases.append(PhaseTypeEnum.Conversion)
    if "OnnxQuantization" in all_passes or "OnnxStaticQuantization" in all_passes or "OnnxDynamicQuantization" in all_passes:
        phases.append(PhaseTypeEnum.Quantization)
    if "evaluator" in oliveJson and oliveJson["evaluator"]:
        phases.append(PhaseTypeEnum.Evaluation)
    # TODO hardcoded
    if PhaseTypeEnum.Conversion not in phases:
        print(f"{oliveJsonFile} missing Conversion phase")
        GlobalVars.hasError = True
    if PhaseTypeEnum.Quantization not in phases:
        print(f"{oliveJsonFile} missing Quantization phase")
        GlobalVars.hasError = True
    modelItem.phases = phases


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
                # get model space config
                modelSpaceConfig = ModelProjectConfig.Read(os.path.join(modelDir, f"{modelInVersion.version}/model_project.config"))
                # check md
                mdFile = os.path.join(modelDir, f"{modelInVersion.version}/README.md")
                if not os.path.exists(mdFile):
                    print(f"{mdFile} not exists")
                    GlobalVars.hasError = True
                
                modelSpaceConfig.modelInfo = modelInVersion
                for i, modelItem in enumerate(modelSpaceConfig.workflows):
                    # set template
                    modelItem.template = model.id
                    modelItem.version = modelInVersion.version
                    modelItem.templateName = modelItem.file[:-5]

                    # read parameter
                    modelParameter = ModelParameter.Read(os.path.join(modelDir, f"{modelInVersion.version}/{modelItem.file}.config"))

                    # check olive json
                    oliveJsonFile = os.path.join(modelDir, f"{modelInVersion.version}/{modelItem.file}")
                    checkOliveConfig(oliveJsonFile, modelParameter, modelItem)

                    # check parameter
                    modelParameter.Check(parameterTemplate, modelItem)     
                    
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
