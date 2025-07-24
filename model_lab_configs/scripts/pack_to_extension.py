import argparse
import glob
import os
import re
import zipfile

templateFile = "resources/template.zip"
templateFileOrigin = "resources/template_origin.zip"


def zipTemplate(input, output):
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Iterate over all the files in the folder
        for root, dirs, files in os.walk(input):
            # Exclude .git folder
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                # Create the full file path
                full_path = os.path.join(root, file)
                # Add file to zip
                zipf.write(full_path, os.path.relpath(full_path, input))


def findFolder():
    user_profile = os.path.expanduser("~")
    vscode_extensions = os.path.join(user_profile, ".vscode", "extensions")
    pattern = os.path.join(vscode_extensions, "ms-windows-ai-studio.windows-ai-studio-*-*")

    folders = [f for f in glob.glob(pattern) if os.path.isdir(f)]
    if not folders:
        return None

    def extract_version(folder):
        match = re.search(r"windows-ai-studio-([0-9]+\.[0-9]+\.[0-9]+)-", folder)
        if match:
            return tuple(map(int, match.group(1).split(".")))
        return (0, 0, 0)

    folders.sort(key=extract_version, reverse=True)
    return folders[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    folder = findFolder()
    if not folder:
        print("No extension folder found.")
        exit(0)
    templateFile = os.path.join(folder, templateFile)
    templateFileOrigin = os.path.join(folder, templateFileOrigin)
    if args.restore:
        if os.path.exists(templateFileOrigin):
            if os.path.exists(templateFile):
                os.remove(templateFile)
            os.rename(templateFileOrigin, templateFile)
            print(f"Restored {templateFile} from {templateFileOrigin}")
    else:
        if not os.path.exists(templateFileOrigin):
            os.rename(templateFile, templateFileOrigin)
        input = os.path.join(os.path.dirname(__file__), "../..")
        zipTemplate(input, templateFile)
        print(f"Packed resources into {templateFile}")
