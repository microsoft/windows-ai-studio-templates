"""
Utility functions for the sanitize module
"""

import inspect
import json
import os
from contextlib import contextmanager
from typing import Any

import pydash

from model_lab import RuntimeEnum

from .constants import EPNames


class GlobalVars:
    errorList = []
    epToName = {
        EPNames.QNNExecutionProvider.value: "Qualcomm NPU",
        EPNames.OpenVINOExecutionProvider.value: "Intel NPU",
        EPNames.VitisAIExecutionProvider.value: "AMD NPU",
        EPNames.CPUExecutionProvider.value: "CPU",
        EPNames.CUDAExecutionProvider.value: "NVIDIA GPU",
        EPNames.NvTensorRTRTXExecutionProvider.value: "NVIDIA TRT for RTX",
    }
    # Initialize runtime to EP mappings directly
    runtimeToEp = {
        RuntimeEnum.CPU: EPNames.CPUExecutionProvider.value,
        RuntimeEnum.QNN: EPNames.QNNExecutionProvider.value,
        RuntimeEnum.IntelNPU: EPNames.OpenVINOExecutionProvider.value,
        RuntimeEnum.AMDNPU: EPNames.VitisAIExecutionProvider.value,
        RuntimeEnum.NvidiaGPU: EPNames.CUDAExecutionProvider.value,
        RuntimeEnum.NvidiaTRTRTX: EPNames.NvTensorRTRTXExecutionProvider.value,
        # Inference N/A
    }
    verbose = False
    # Initialize checks
    pathCheck = 0
    configCheck = 0
    oliveJsonCheck = 0
    ipynbCheck = 0
    gitignoreCheck = 0
    modelProjectCheck = 0
    extensionCheck = 0
    # Should align with number of LLM models
    inferenceModelCheck = 0

    olivePath = None
    oliveCheck = 0

    def Check(self, configDir: str):
        if self.configCheck != self.oliveJsonCheck:
            printError(f"Config check {self.configCheck} does not match olive json check {self.oliveJsonCheck}")
        if self.gitignoreCheck != self.modelProjectCheck - self.extensionCheck:
            printError(
                f"Gitignore check {self.gitignoreCheck} does not match model project check {self.modelProjectCheck} - {self.extensionCheck}"
            )
        # We add this test to make sure the sanity check is working: i.e. paths are checked and files are checked
        with open_ex(os.path.join(configDir, "checks.json"), "w") as file:
            json.dump(
                {
                    "pathCheck": self.pathCheck,
                    "configCheck": self.configCheck,
                    "oliveJsonCheck": self.oliveJsonCheck,
                    "ipynbCheck": self.ipynbCheck,
                    "gitignoreCheck": self.gitignoreCheck,
                    "modelProjectCheck": self.modelProjectCheck,
                    "inferenceModelCheck": self.inferenceModelCheck,
                    "extensionCheck": self.extensionCheck,
                },
                file,
                indent=4,
            )


def printProcess(msg: str):
    if GlobalVars.verbose:
        print(f"Process {msg}")


def printInfo(msg: str):
    if GlobalVars.verbose:
        print(msg)


def printTip(msg: str):
    """Print important information with special color formatting (cyan)"""
    frame = inspect.currentframe()
    if frame and frame.f_back:
        frame = frame.f_back
        filename = os.path.relpath(frame.f_code.co_filename)
        lineno = frame.f_lineno
    else:
        filename = "unknown"
        lineno = 0
    # Cyan text with file and line number, clickable in terminal
    print(f"\033[36mTip: {filename}:{lineno}: {msg}\033[0m")


def printError(msg: str):
    frame = inspect.currentframe()
    if frame and frame.f_back:
        frame = frame.f_back
        filename = os.path.relpath(frame.f_code.co_filename)
        lineno = frame.f_lineno
    else:
        filename = "unknown"
        lineno = 0
    # print all errors in the end
    GlobalVars.errorList.append((filename, lineno, msg))


def printWarning(msg: str):
    frame = inspect.currentframe()
    if frame and frame.f_back:
        frame = frame.f_back
        filename = os.path.relpath(frame.f_code.co_filename)
        lineno = frame.f_lineno
    else:
        filename = "unknown"
        lineno = 0
    # Yellow text, with file and line number, clickable in terminal
    print(f"\033[33mWARNING: {filename}:{lineno}: {msg}\033[0m")


@contextmanager
def open_ex(file_path, mode):
    # Note: The `newline` parameter has no effect when reading a file.
    file = open(file_path, mode, encoding="utf-8", newline="\n")
    try:
        yield file
    finally:
        file.close()


def checkPath(path: str, oliveJson: Any, printOnNotExist: bool = True):
    printInfo(path)
    GlobalVars.pathCheck += 1
    if pydash.get(oliveJson, path) is None:
        if printOnNotExist:
            printError(f"Not in olive json: {path}")
        return False
    return True
