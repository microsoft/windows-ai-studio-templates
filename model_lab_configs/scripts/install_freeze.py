import argparse
from os import path
import subprocess
import sys

def get_requires(name):
    package_name = name.split('==')[0]  # Remove version if present
    requires = []
    try:
        output = subprocess.check_output([sys.executable, "-Im", "pip", "show", package_name]).decode('utf-8')
        for line in output.splitlines():
            if line.startswith('Requires'):
                requires = line.split(':')[1].strip().split(', ')
                break
    except subprocess.CalledProcessError:
        pass
    return [req for req in requires if req]


def main():
    # Constants
    shared = [
        "olive-ai==0.8.0",
        "tabulate==0.9.0",
        "datasets==3.5.0",
        "ipykernel==6.29.5",
        "ipywidgets==8.1.5",
    ]
    specific = {
        "CPU": ["onnxruntime==1.21.0"],
        "QNN": ["onnxruntime-qnn==1.20.2"],
        "IntelNPU": ["onnxruntime-openvino==1.20.0"],
        "AMDNPU": [],
        "NvidiaGPU": ["onnxruntime-gpu==1.21.0", "onnxruntime-genai-cuda==0.7.0", "auto-gptq==0.7.1"]
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True, help=",".join(specific.keys()))
    args = parser.parse_args()

    # Install
    all = shared + specific[args.runtime]
    print(f"Installing dependencies: {all}")
    result = subprocess.run([sys.executable, "-Im", "pip", "install", "--no-warn-script-location"] + all, text=True)

    # Get freeze
    pip_freeze = subprocess.check_output([sys.executable, "-Im", "pip", "freeze"]).decode('utf-8').splitlines()
    freeze_dict = {}
    for line in pip_freeze:
        if '==' in line:
            name, version = line.split('==')
            # requires outputs lower case names
            freeze_dict[name.lower()] = version
    print(f"Installed dependencies: {freeze_dict}")


    # write result
    outputFile = path.join(path.dirname(__file__), "docs", f"requirements-{args.runtime}.txt")
    with open(outputFile, "w") as f:
        for name in all:
            f.write("# " + name + "\n")
            f.write(name + "\n")
            requires = get_requires(name)
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