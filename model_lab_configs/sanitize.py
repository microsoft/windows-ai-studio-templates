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

# Global vars

class GlobalVars:
    hasChange = False
    hasError = False


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
    section: str = ""

    def Check(self, isTemplate: bool, sectionNames: set[str] = set()):
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
        if not self.section:
            return False
        if self.section not in sectionNames:
            return False
        return True

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
        if not self.section:
            self.section = template.section


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

class ModelItem(BaseModel):
    name: str
    file: str
    template: str = ""
    version: int = -1
    templateName: str = ""

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
        return True

class ModelSPaceConfig(BaseModel):
    models: list[ModelItem]

    @staticmethod
    def Read(modelSpaceConfigFile: str):
        print(f"Process {modelSpaceConfigFile}")
        with open(modelSpaceConfigFile, 'r') as file:
            modelSpaceConfigContent = file.read()
        modelSpaceConfig = ModelSPaceConfig.model_validate_json(modelSpaceConfigContent, strict=True)
        modelSpaceConfig._file = modelSpaceConfigFile
        modelSpaceConfig._fileContent = modelSpaceConfigContent
        return modelSpaceConfig

    # after template is set
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

# Model Parameter

class Section(BaseModel):
    name: str
    description: str

    def Check(self):
        if not self.name:
            return False
        if not self.description:
            return False
        return True
    

class ModelParameter(BaseModel):
    sections: list[Section]
    parameters: list[Parameter]

    @staticmethod
    def Read(parameterFile: str):
        print(f"Process {parameterFile}")
        with open(parameterFile, 'r') as file:
            parameterContent = file.read()
        modelParameter = ModelParameter.model_validate_json(parameterContent, strict=True)
        modelParameter._file = parameterFile
        modelParameter._fileContent = parameterContent
        return modelParameter


    def Check(self, templates: Dict[str, Parameter]):
        allSectionNames = set([section.name for section in self.sections])
        for i, section in enumerate(self.sections):
            if not section.Check():
                print(f"{self._file} section {i} has error")
                GlobalVars.hasError = True

        for i, parameter in enumerate(self.parameters):
            if parameter.template:
                template = parameter.template
                if template.template not in templates:
                    print(f"{self._file} parameter {i} has wrong template")
                    GlobalVars.hasError = True
                    continue
                parameter.applyTemplate(template)
                parameter.applyTemplate(templates[template.template])

            if not parameter.Check(False, allSectionNames):
                print(f"{self._file} parameter {i} has error")
                GlobalVars.hasError = True
        
        newContent = self.model_dump_json(indent=4)
        if newContent != self._fileContent:
            with open(self._file, 'w') as file:
                file.write(newContent)
            GlobalVars.hasChange = True


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
            # set version
            allVersions = [int(name) for name in os.listdir(modelDir) if os.path.isdir(os.path.join(modelDir, name))]
            model.version = max(allVersions)
            # get model space config
            modelSpaceConfig = ModelSPaceConfig.Read(os.path.join(modelDir, f"{model.version}/modelspace.config"))
            for i, modelItem in enumerate(modelSpaceConfig.models):
                # set template
                modelItem.template = model.id
                modelItem.version = model.version
                modelItem.templateName = modelItem.file[:-5]
                # check md
                mdFile = os.path.join(modelDir, f"{model.version}/{modelItem.file}.md")
                if not os.path.exists(mdFile):
                    print(f"{mdFile} not exists")
                    GlobalVars.hasError = True
                # check parameter
                modelParameter = ModelParameter.Read(os.path.join(modelDir, f"{model.version}/{modelItem.file}.config"))
                modelParameter.Check(parameterTemplate)
                # check olive json
                oliveJsonFile = os.path.join(modelDir, f"{model.version}/{modelItem.file}")
                with open(oliveJsonFile, 'r') as file:
                    oliveJson = json.load(file)
                for i, parameter in enumerate(modelParameter.parameters):
                    if pydash.get(oliveJson, parameter.path) is None:
                        print(f"{oliveJsonFile} missing parameter {i}: {parameter.path}")
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
