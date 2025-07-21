import argparse
import os
import subprocess
from os import path

from model_lab import RuntimeEnum

# This script is used to generate the requirements-*.txt
# Usage: uv run .\install_freeze.py --python PATH_TO_RUNTIME
# They also have special comments:
# - `# pip:`: anything after it will be sent to pip command like `# pip:--no-build-isolation`
# - `# copy:`: copy from cache to folder in runtime like `# copy:a/*.dll;b;pre`, `# copy:a/*.dll;b;post`
# - `# download:`: download from release and save it to cache folder like `# download:onnxruntime-genai-cuda-0.7.0-cp39-cp39-win_amd64.whl`
uvpipInstallPrefix = "# uvpip:install"
depsPrefix = "# deps:"
cudaExtraUrl = "--extra-index-url https://download.pytorch.org/whl/cu128"
torchCudaVersion = "torch==2.7.0+cu128"
onnxruntimeWinmlVersion = f"{uvpipInstallPrefix} onnxruntime-winml==1.22.0.post1 --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ORT-Nightly/pypi/simple --no-deps;post"
onnxruntimeGenaiWinmlVersion = f"{uvpipInstallPrefix} onnxruntime-genai-winml==0.8.3 --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ORT-Nightly/pypi/simple --no-deps;post"
evaluateVersion = "evaluate==0.4.3"
scikitLearnVersion = "scikit-learn==1.6.1"


def get_requires(name: str, args):
    # TODO for this case, need to install via Model Lab first
    if name.startswith(uvpipInstallPrefix):
        name = name.split(" ")[2].strip()
    elif name.startswith(depsPrefix):
        name = name.split(":")[1].strip()

    if "#egg=" in name:
        package_name = name.split("#egg=")[1]
    elif name.startswith("./"):
        package_name = name[2:].split("-")[0].replace("_", "-")
    else:
        package_name = name.split("==")[0]  # Remove version if present
    if "[" in package_name:
        package_name = package_name.split("[")[0]
    requires = []
    try:
        output = subprocess.check_output(["uv", "pip", "show", package_name, "-p", args.python]).decode("utf-8")
        for line in output.splitlines():
            if line.startswith("Requires"):
                requires = line.split(":")[1].strip().split(", ")
                break
    except subprocess.CalledProcessError:
        pass
    return [req for req in requires if req]


def main():
    # Constants
    # if from git: "git+https://github.com/microsoft/Olive.git@COMMIT_ID#egg=olive_ai
    oliveAi = "olive-ai==0.9.1"
    torchVision = "torchvision==0.22.0"
    pre = {
        RuntimeEnum.NvidiaGPU: [
            cudaExtraUrl,
            torchCudaVersion,
        ],
        RuntimeEnum.WCR_CUDA: [
            cudaExtraUrl,
            torchCudaVersion,
        ],
        RuntimeEnum.IntelNPU: [
            "torch==2.6.0",
        ],
    }
    shared = [
        # sticking to ONNX IR version 10 which can still be consumed by ORT v1.22.0
        "onnx==1.17.0",
        oliveAi,
        "tabulate==0.9.0",
        "datasets==3.5.0",
        "ipykernel==6.29.5",
        "ipywidgets==8.1.5",
    ]
    # torchvision, onnxruntime and genai go here. others should go feature
    post = {
        RuntimeEnum.QNN: [
            torchVision,
            "onnxruntime-qnn==1.21.1",
            "# uvpip:install onnxruntime-genai==0.7.0 --no-deps;post",
        ],
        RuntimeEnum.IntelNPU: [
            # nncf needs torch 2.6 so torchvision is downgraded
            "torchvision==0.21.0",
            # onnxruntime-openvino see below
            # use this to track depedencies
            "onnxruntime==1.21.0",
            # from olive[openvino]
            "openvino==2025.1.0",
            "nncf==2.16.0",
            "optimum[openvino]==1.24.0",
            # optimum-intel==1.15.0: depends on onnxruntime so we need to use a separate venv
            "onnxruntime-genai==0.7.0",
        ],
        # https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html
        RuntimeEnum.NvidiaGPU: [
            "torchvision==0.22.0+cu128",
            "onnxruntime-gpu==1.21.0",
            "onnxruntime-genai-cuda==0.7.0",
        ],
        RuntimeEnum.WCR: [
            torchVision,
            onnxruntimeWinmlVersion,
            onnxruntimeGenaiWinmlVersion,
            evaluateVersion,
            scikitLearnVersion,
        ],
        RuntimeEnum.WCR_CUDA: [
            "torchvision==0.22.0+cu128",
            onnxruntimeWinmlVersion,
            onnxruntimeGenaiWinmlVersion,
            evaluateVersion,
            scikitLearnVersion,
        ],
        RuntimeEnum.QNN_LLLM: [
            "ipykernel==6.29.5",
            "ipywidgets==8.1.5",
            "# deps:onnxruntime-winml",
            onnxruntimeGenaiWinmlVersion,
        ],
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", "-r", default="", help=",".join([k.value for k in RuntimeEnum]))
    parser.add_argument("--python", "-p", required=True, type=str, help="python path. TODO: input twice")
    args = parser.parse_args()

    if not args.runtime:
        pythonSegs = args.python.split("-")
        args.runtime = pythonSegs[-4]
        print(args.runtime)

    runtime = RuntimeEnum(args.runtime)
    onlyInference = False
    if runtime in [RuntimeEnum.QNN_LLLM]:
        onlyInference = True

    # prepare file
    configs_dir = path.dirname(path.dirname(__file__))
    temp_dir = path.join(configs_dir, "scripts", "model_lab", "__pycache__")
    os.makedirs(temp_dir, exist_ok=True)
    temp_req = path.join(temp_dir, "temp_req.txt")
    all: list[str] = []
    with open(temp_req, "w") as f:
        if runtime in pre:
            for line in pre[runtime]:
                f.write(line + "\n")
                all.append(line)

                # remove olive
                if line.endswith("egg=olive_ai") or line.startswith("olive-ai=="):
                    shared = shared[1:]
        if not onlyInference:
            for line in shared:
                f.write(line + "\n")
                all.append(line)
        if runtime in post:
            for line in post[runtime]:
                f.write(line + "\n")
                all.append(line)

    # Install
    print(f"Installing dependencies: {temp_req}")
    result = subprocess.run(["uv", "pip", "install", "-r", temp_req, "-p", args.python], text=True)

    # Get freeze
    pip_freeze = subprocess.check_output(["uv", "pip", "freeze", "-p", args.python]).decode("utf-8").splitlines()
    freeze_dict = {}
    for line in pip_freeze:
        if "==" in line:
            name, version = line.split("==")
            # requires outputs lower case names
            freeze_dict[name.lower()] = version
    print(f"Installed dependencies: {freeze_dict}")

    # write result
    outputFile = path.join(path.dirname(__file__), "..", "docs", f"requirements-{args.runtime}.txt")
    with open(outputFile, "w", newline="\n") as f:
        for name in all:
            if (
                name.startswith("#") and not name.startswith(uvpipInstallPrefix) and not name.startswith(depsPrefix)
            ) or name.startswith("--"):
                f.write(name + "\n")
                continue
            if not name.startswith("#"):
                f.write("# " + name + "\n")
            f.write(name + "\n")
            requires = get_requires(name, args)
            print(f"Requires for {name}: {requires}")
            for req in requires:
                if req in freeze_dict:
                    f.write(f"{req}=={freeze_dict[req]}\n")
                else:
                    newReq = req.replace("-", "_")
                    if newReq in freeze_dict:
                        f.write(f"{newReq}=={freeze_dict[newReq]}\n")
                    else:
                        raise Exception(f"Cannot find {req} in pip freeze")

    # remove duplicate lines from output file
    with open(outputFile, "r") as f:
        lines = f.readlines()
    unique_lines = list(dict.fromkeys(lines))  # Preserve order and remove duplicates
    with open(outputFile, "w", newline="\n") as f:
        f.writelines(unique_lines)


if __name__ == "__main__":
    main()
