"""
File validation functions
"""

from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

from .constants import (
    EPNames,
    OlivePassNames,
    OlivePropertyNames,
    importOnnxgenairuntime,
    importOnnxruntime,
    outputModelIntelNPURelativePath,
    outputModelModelBuilderPath,
    outputModelRelativePath,
)
from .model_parameter import ModelParameter
from .utils import GlobalVars, open_ex, printError, printProcess, printWarning


def check_case(path: Path) -> bool:
    path = Path(path)
    try:
        abs_path = path.resolve(strict=False)
    except Exception:
        return False

    if str(path) != str(abs_path):
        printError(f"Path case mismatch: {path} vs {abs_path}")
        return False
    return True


def process_gitignore(modelVerDir: str, configDir: str):
    GlobalVars.gitignoreCheck += 1

    gitignoreFile = os.path.join(modelVerDir, ".gitignore")
    templateFile = os.path.join(configDir, "gitignore.md")
    if not os.path.exists(gitignoreFile):
        printWarning(f"{gitignoreFile} not exists. Copy the template one")
        shutil.copy(templateFile, gitignoreFile)
    else:
        # Ensure each non-empty line in template is present in the .gitignore file (exact match)
        with open_ex(gitignoreFile, "r") as file:
            gitignoreLines = [line.strip() for line in file if line.strip()]
        with open_ex(templateFile, "r") as file:
            templateLines = [line.strip() for line in file if line.strip()]
        missing = [line for line in templateLines if line not in gitignoreLines]
        for line in missing:
            printError(f"{gitignoreFile} does not have line '{line}'")


def readCheckOliveConfig(oliveJsonFile: str, modelParameter: ModelParameter):
    """
    This will set phases to modelParameter
    """
    GlobalVars.oliveJsonCheck += 1

    printProcess(oliveJsonFile)
    with open_ex(oliveJsonFile, "r") as file:
        oliveJson = json.load(file)
    # check if engine is in oliveJson
    if OlivePropertyNames.Engine in oliveJson:
        printError(f"{oliveJsonFile} has engine. Should place in the root instead")
        return
    if OlivePropertyNames.Evaluator in oliveJson and not isinstance(oliveJson[OlivePropertyNames.Evaluator], str):
        printError(f"{oliveJsonFile} evaluator property should be str")
        return
    # check if has more than one systems and more than one accelerators
    if OlivePropertyNames.Systems not in oliveJson or len(oliveJson[OlivePropertyNames.Systems]) != 1:
        printError(f"{oliveJsonFile} should have only one system")
        return
    systemK, systemV = list(oliveJson[OlivePropertyNames.Systems].items())[0]
    accelerators = systemV[OlivePropertyNames.Accelerators]
    if len(accelerators) != 1:
        printError(f"{oliveJsonFile} should have only one accelerator")
        return
    eps = accelerators[0][OlivePropertyNames.ExecutionProviders]
    if len(eps) != 1:
        printError(f"{oliveJsonFile} should have only one execution provider")
        return
    if eps[0] not in GlobalVars.epToName:
        printError(f"{oliveJsonFile} has wrong execution provider {eps[0]}")
        return

    jsonUpdated = False

    # TODO check host
    # check target
    if OlivePropertyNames.Target not in oliveJson or oliveJson[OlivePropertyNames.Target] != systemK:
        oliveJson[OlivePropertyNames.Target] = systemK
        jsonUpdated = True

    # cache / output / evaluate_input_model
    if OlivePropertyNames.CleanCache in oliveJson and oliveJson[OlivePropertyNames.CleanCache]:
        oliveJson.pop(OlivePropertyNames.CleanCache)
        jsonUpdated = True

    if OlivePropertyNames.CacheDir not in oliveJson or oliveJson[OlivePropertyNames.CacheDir] != "cache":
        oliveJson[OlivePropertyNames.CacheDir] = "cache"
        jsonUpdated = True

    if OlivePropertyNames.OutputDir not in oliveJson or not str(oliveJson[OlivePropertyNames.OutputDir]).startswith(
        "model/"
    ):
        printError(f"{oliveJsonFile} should have use model/XXX as {OlivePropertyNames.OutputDir}")

    if OlivePropertyNames.EvaluateInputModel not in oliveJson or oliveJson[OlivePropertyNames.EvaluateInputModel]:
        oliveJson[OlivePropertyNames.EvaluateInputModel] = False
        jsonUpdated = True

    # update save_as_external_data
    supportedPasses = [
        v
        for k, v in oliveJson[OlivePropertyNames.Passes].items()
        if v[OlivePropertyNames.Type]
        in [
            OlivePassNames.OnnxConversion,
            OlivePassNames.OnnxQuantization,
            OlivePassNames.OnnxStaticQuantization,
            OlivePassNames.OnnxDynamicQuantization,
        ]
    ]
    for conversionPass in supportedPasses:
        if OlivePropertyNames.ExternalData not in conversionPass or not conversionPass[OlivePropertyNames.ExternalData]:
            conversionPass[OlivePropertyNames.ExternalData] = True
            jsonUpdated = True

    if jsonUpdated:
        with open_ex(oliveJsonFile, "w") as file:
            json.dump(oliveJson, file, indent=4)
    return oliveJson


def readCheckIpynb(ipynbFile: str, modelItems: dict[str, ModelParameter]):
    """
    Note this return exists or not, not valid or not
    """
    if os.path.exists(ipynbFile):
        GlobalVars.ipynbCheck += 1

        with open_ex(ipynbFile, "r") as file:
            ipynbContent: str = file.read()
        allRuntimes: list[str] = []
        for name, modelParameter in modelItems.items():
            testPath = outputModelRelativePath
            importStr = importOnnxruntime
            if modelParameter.isLLM:
                testPath = outputModelModelBuilderPath
                importStr = importOnnxgenairuntime
            elif (
                modelParameter.runtime.values
                and len(modelParameter.runtime.values) == 1
                and modelParameter.runtime.values[0] == EPNames.OpenVINOExecutionProvider.value
            ):
                testPath = outputModelIntelNPURelativePath
            for item in [testPath, importStr]:
                if not re.search(item, ipynbContent):
                    printError(f"{ipynbFile} does not have '{item}' for {name}, please use it as input")
            if modelParameter.evalRuntime:
                runtime = GlobalVars.runtimeToEp[modelParameter.evalRuntime]
                if runtime not in allRuntimes:
                    allRuntimes.append(runtime)
            else:
                if modelParameter.runtime.values:
                    for runtime in modelParameter.runtime.values:
                        if runtime not in allRuntimes:
                            allRuntimes.append(runtime)

        targetEP = None
        if len(allRuntimes) == 2 and EPNames.CPUExecutionProvider.value in allRuntimes:
            allRuntimes.remove(EPNames.CPUExecutionProvider.value)
            targetEP = allRuntimes[0]
        elif len(allRuntimes) == 1:
            targetEP = allRuntimes[0]
        elif len(allRuntimes) > 1:
            # TODO we use QNN as default because currently we only replace this
            if EPNames.QNNExecutionProvider.value in allRuntimes:
                targetEP = EPNames.QNNExecutionProvider.value
            elif EPNames.CPUExecutionProvider.value in allRuntimes:
                targetEP = EPNames.CPUExecutionProvider.value
            else:
                targetEP = allRuntimes[0]
        if targetEP:
            targetStr = f'ExecutionProvider=\\"{targetEP}\\"'
            if ipynbContent.count(targetStr) != 1:
                printError(f"{ipynbFile} should have 1 {targetStr}")
        else:
            printError(f"{ipynbFile} has no runtime for it!")
        return True
    return False
