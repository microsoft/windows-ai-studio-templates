import argparse
import os
from os import path
import subprocess
import sys
from model_lab import RuntimeEnum

# This script is used to generate the requirements-*.txt
# Usage: uv run -p PATH_TO_RUNTIME .\install_freeze.py --runtime RUNTIME --python PATH_TO_RUNTIME
# They also have special comments:
# - `# pip:`: anything after it will be sent to pip command like `# pip:--no-build-isolation`
# - `# copy:`: copy from cache to folder in runtime like `# copy:a/*.dll;b;pre`, `# copy:a/*.dll;b;post`
# - `# download:`: download from release and save it to cache folder like `# download:onnxruntime-genai-cuda-0.7.0-cp39-cp39-win_amd64.whl`

def get_requires(name, args):
    if "#egg=" in name:
        package_name = name.split("#egg=")[1]
    else:
        package_name = name.split('==')[0]  # Remove version if present
    if "[" in package_name:
        package_name = package_name.split("[")[0]
    requires = []
    try:
        output = subprocess.check_output(["uv", "pip", "show", package_name, "-p", args.python]).decode('utf-8')
        for line in output.splitlines():
            if line.startswith('Requires'):
                requires = line.split(':')[1].strip().split(', ')
                break
    except subprocess.CalledProcessError:
        pass
    return [req for req in requires if req]


def main():
    # Constants
    pre = {
        RuntimeEnum.NvidiaGPU: [
            "--extra-index-url https://download.pytorch.org/whl/cu126",
            "torch==2.6.0+cu126",
        ],
        RuntimeEnum.AMDNPU: [
            "numpy==1.26.4"
        ],
        RuntimeEnum.IntelNPU: [
            "torch==2.6.0"
        ]
    }
    shared = [
        "git+https://github.com/microsoft/Olive.git@59bfe00cbf4895c385c6fb863f3792db50b6012b#egg=olive_ai",
        "tabulate==0.9.0",
        "datasets==3.5.0",
        "ipykernel==6.29.5",
        "ipywidgets==8.1.5",
    ]
    # onnxruntime and genai go here. others should go feature
    post = {
        RuntimeEnum.CPU: [
            "torchvision==0.22.0",
            "onnxruntime==1.21.0"
        ],
        RuntimeEnum.QNN: [
            "torchvision==0.22.0",
            "onnxruntime-qnn==1.21.1"
        ],
        RuntimeEnum.IntelNPU: [
            # nncf needs torch 2.6 so torchvision is downgraded
            "torchvision==0.21.0",
            "onnxruntime-openvino==1.21.0",
            # from olive[openvino]
            "openvino==2025.1.0",
            "nncf==2.16.0",
            "optimum[openvino]==1.17.1"
        ],
        RuntimeEnum.AMDNPU: [
            "torchvision==0.22.0",
            "# onnxruntime",
            "./voe-1.5.0.dev20250417022941+g53d49594-py3-none-any.whl",
            "./onnxruntime_vitisai-1.22.0.dev20250417-cp310-cp310-win_amd64.whl",
            "# copy:onnxruntime_vitisai-1.22.0.dev20250417-cp310-cp310-win_amd64/*.dll;Lib/site-packages/onnxruntime/capi;post"
        ],
        # https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html
        RuntimeEnum.NvidiaGPU: [
            "torchvision==0.21.0+cu126",
            "onnxruntime-gpu==1.21.0",
            "onnxruntime-genai-cuda==0.7.0"
        ]
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True, help=",".join([k.value for k in RuntimeEnum]))
    parser.add_argument("--python", required=True, type=str, help="python path. TODO: input twice")
    args = parser.parse_args()
    runtime = RuntimeEnum(args.runtime)

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
    pip_freeze = subprocess.check_output(["uv", "pip", "freeze", "-p", args.python]).decode('utf-8').splitlines()
    freeze_dict = {}
    for line in pip_freeze:
        if '==' in line:
            name, version = line.split('==')
            # requires outputs lower case names
            freeze_dict[name.lower()] = version
    print(f"Installed dependencies: {freeze_dict}")

    # write result
    outputFile = path.join(path.dirname(__file__), "..", "docs", f"requirements-{args.runtime}.txt")
    with open(outputFile, "w") as f:
        for name in all:
            if name.startswith("#") or name.startswith("--") or name.startswith("./"):
                f.write(name + "\n")
                continue
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


if __name__ == "__main__":
    main()