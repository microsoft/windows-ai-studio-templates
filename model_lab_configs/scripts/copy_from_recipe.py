import json
import shutil
import subprocess
from pathlib import Path

ignore_patterns = ["info.yml", "_copy.json.config"]
copied_folders = 0

def copy_folder(model, models_dir: Path, olive_recipes_dir: Path):
    id = model.get("id")
    version = model.get("version")
    relative_path = model.get("relativePath")
    # make dir
    target_dir = models_dir / Path(id) / Path(str(version))
    target_dir.mkdir(parents=True, exist_ok=True)
    source_dir = olive_recipes_dir / Path(relative_path)
    # copy dir
    print(f"Copying from {source_dir} to {target_dir}")
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*ignore_patterns))
    global copied_folders
    copied_folders += 1


def save_commit_id(models_dir: Path, olive_recipes_dir: Path):
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=olive_recipes_dir, capture_output=True, text=True, check=True
    )
    commit_id = result.stdout.strip()
    with open(models_dir / "commit_id.txt", "w") as f:
        f.write(commit_id)


def main():
    root_dir = Path(__file__).parent.parent.parent
    olive_recipes_dir = root_dir.parent / "olive-recipes"
    if not olive_recipes_dir.exists():
        olive_recipes_dir = root_dir / "olive-recipes"
        if not olive_recipes_dir.exists():
            raise FileNotFoundError("olive-recipes directory not found.")
    olive_configs_dir = olive_recipes_dir / ".aitk" / "configs"
    olive_list = olive_configs_dir / "model_list.json"
    models_dir = root_dir / "model_lab_configs"

    with open(olive_list, "r") as f:
        list = json.load(f)

    for model in list["models"]:
        copy_folder(model, models_dir, olive_recipes_dir)
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
