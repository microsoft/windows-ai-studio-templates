import json
import shutil
import subprocess
from pathlib import Path
import argparse

ignore_patterns = ["info.yml", "_copy.json.config"]
copied_folders = 0

def copy_folder(model, models_dir: Path, olive_recipes_dir: Path, copy_license: bool = False):
    id = model.get("id")
    version = model.get("version")
    relative_path = model.get("relativePath").replace("\\", "/")
    # make dir
    target_dir = models_dir / Path(id) / Path(str(version))
    target_dir.mkdir(parents=True, exist_ok=True)
    source_dir = olive_recipes_dir / Path(relative_path)
    # copy dir
    print(f"Copying from {source_dir} to {target_dir}")
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*ignore_patterns))
    global copied_folders
    copied_folders += 1
    if copy_license:
        license_file = source_dir.parent / "LICENSE"
        # To avoid confusion of license of recipes, license of packages in runtime etc., rename the license file to LICENSE_OF_MODEL.txt
        license_dst = target_dir / "LICENSE_OF_MODEL.txt"
        if license_file.exists() and not license_dst.exists():
            shutil.copy(license_file, license_dst)


def save_commit_id(models_dir: Path, olive_recipes_dir: Path):
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=olive_recipes_dir, capture_output=True, text=True, check=True
    )
    commit_id = result.stdout.strip()
    print(f"Current commit ID: {commit_id}")
    with open(models_dir / "commit_id.txt", "w") as f:
        f.write(commit_id)


def clean_folder(folder: Path):
    shutil.move(folder / ".keep", folder.parent / ".keep")
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True, exist_ok=True)
    shutil.move(folder.parent / ".keep", folder / ".keep")

def main():
    parser = argparse.ArgumentParser(description="Copy model folders from olive-recipes to model_lab_configs.")
    parser.add_argument("--olive-recipes-dir", type=str, help="Path to the olive-recipes directory.")
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent.parent
    if args.olive_recipes_dir:
        olive_recipes_dir = Path(args.olive_recipes_dir)
    else:
        olive_recipes_dir = root_dir.parent / "olive-recipes"
        if not olive_recipes_dir.exists():
            # Inside project, for github action
            olive_recipes_dir = root_dir / "olive-recipes"
    if not olive_recipes_dir.exists():
        raise FileNotFoundError("olive-recipes directory not found.")
    olive_configs_dir = olive_recipes_dir / ".aitk" / "configs"
    olive_list = olive_configs_dir / "model_list.json"
    models_dir = root_dir / "model_lab_configs"

    clean_folder(models_dir / "huggingface")
    clean_folder(models_dir / "extension")
    clean_folder(models_dir / "requirements")
    shutil.copytree(olive_recipes_dir / ".aitk" / "requirements", models_dir / "requirements", dirs_exist_ok=True)

    with open(olive_list, "r") as f:
        list = json.load(f)

    for model in list["models"]:
        copy_folder(model, models_dir, olive_recipes_dir, copy_license=True)
    for model in list["template_models"]:
        copy_folder(model, models_dir, olive_recipes_dir)

    shutil.copyfile(
        olive_list,
        models_dir / "model_list.json",
    )
    save_commit_id(models_dir, olive_recipes_dir)
    global copied_folders
    print(f"Copied {copied_folders} folders from olive-recipes to model_lab_configs.")


if __name__ == "__main__":
    main()
