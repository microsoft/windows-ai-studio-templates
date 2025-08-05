import shutil
from pathlib import Path
import json

ignore_patterns = ["info.yml", "_copy.json.config"]

def copy_folder(model, models_dir: Path, olive_recipes_dir: Path):
    id = model.get("id")
    version = model.get("version")
    relative_path = model.get("relativePath")
    # make dir
    target_dir = models_dir / Path(id) / Path(str(version))
    target_dir.mkdir(parents=True, exist_ok=True)
    source_dir = olive_recipes_dir / Path(relative_path)
    # copy dir
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns(*ignore_patterns))

def main():
    root_dir = Path(__file__).parent.parent.parent
    olive_recipes_dir = root_dir.parent / "olive-recipes"
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


if __name__ == "__main__":
    main()
