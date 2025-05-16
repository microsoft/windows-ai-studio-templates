import argparse
import os
from os import path
import subprocess
import sys
from model_lab import RuntimeEnum

# This script is used to generate the requirements-*.txt
# Usage: uv run .\install_freeze.py --python PATH_TO_RUNTIME
# They also have special comments:
# - `# pip:`: anything after it will be sent to pip command like `# pip:--no-build-isolation`
# - `# copy:`: copy from cache to folder in runtime like `# copy:a/*.dll;b;pre`, `# copy:a/*.dll;b;post`
# - `# download:`: download from release and save it to cache folder like `# download:onnxruntime-genai-cuda-0.7.0-cp39-cp39-win_amd64.whl`

def get_requires(name, args):
    if "#egg=" in name:
        package_name = name.split("#egg=")[1]
    elif name.startswith("./"):
        package_name = name[2:].split("-")[0].replace("_", "-")
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
    # if from git: "git+https://github.com/microsoft/Olive.git@COMMIT_ID#egg=olive_ai
    oliveAi = "olive-ai==0.9.1"
    torchVision = "torchvision==0.22.0"
    pre = {
        RuntimeEnum.NvidiaGPU: [
            "--extra-index-url https://download.pytorch.org/whl/cu126",
            "torch==2.6.0+cu126",
        ],
        RuntimeEnum.AMDNPU: [
            "numpy==1.26.4",
        ],
        RuntimeEnum.IntelNPU: [
            "torch==2.6.0",
        ],
    }
    shared = [
        oliveAi,
        "tabulate==0.9.0",
        "datasets==3.5.0",
        "ipykernel==6.29.5",
        "ipywidgets==8.1.5",
    ]
    # torchvision, onnxruntime and genai go here. others should go feature
    post = {
        RuntimeEnum.CPU: [
            torchVision,
            "onnxruntime==1.21.0",
            "onnxruntime-genai==0.7.0",
        ],
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
            # optimum-intel==1.15.0: depends on onnxruntime so we need to uninstall first
            #"# uvpip:uninstall onnxruntime;post",
            # uninstall first to fix incomplete installation issue
            #"# uvpip:uninstall onnxruntime-openvino;post",
            #"# uvpip:install ./onnxruntime_openvino-1.22.0-cp312-cp312-win_amd64.whl;post",
            #"# uvpip:install ./onnxruntime_genai-0.9.0.dev0-cp312-cp312-win_amd64.whl --no-deps;post"
            "onnxruntime-genai==0.7.0",
        ],
        RuntimeEnum.AMDNPU: [
            torchVision,
            "# onnxruntime",
            "./voe-1.5.0.dev20250501191909+g87eb429ad-py3-none-any.whl",
            "./onnxruntime_vitisai-1.22.0.dev20250501-cp310-cp310-win_amd64.whl",
            "# copy:wcr_05022025/*.dll;Lib/site-packages/onnxruntime/capi;post",
            "# uvpip:install ./onnxruntime_genai-0.7.0.dev0-cp310-cp310-win_amd64.whl --no-deps;post",
        ],
        # https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html
        RuntimeEnum.NvidiaGPU: [
            "torchvision==0.21.0+cu126",
            "onnxruntime-gpu==1.21.0",
            "onnxruntime-genai-cuda==0.7.0",
        ],
        RuntimeEnum.WCR: [
            torchVision,
            "./onnxruntime_winml-1.22.0-cp312-cp312-win_amd64.whl",
            "./onnxruntime_genai_winml-0.9.0.dev0-cp312-cp312-win_amd64.whl",
            "evaluate==0.4.3",
            "scikit-learn==1.6.1",
        ],
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default="", help=",".join([k.value for k in RuntimeEnum]))
    parser.add_argument("--python", "-p", required=True, type=str, help="python path. TODO: input twice")
    args = parser.parse_args()

    if not args.runtime:
        pythonSegs = args.python.split("-")
        args.runtime = pythonSegs[-4]
        print(args.runtime)

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

                # remove olive
                if line.endswith("egg=olive_ai") or line.startswith("olive-ai=="):
                    shared = shared[1:]
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
            if name.startswith("#") or name.startswith("--"):
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
