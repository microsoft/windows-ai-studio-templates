from pathlib import Path
from sanitize.model_info import ModelList
import shutil
import os

def main():
    root_dir = Path(__file__).parent.parent.parent
    olive_recipes_dir = root_dir.parent / "olive-recipes"
    configs_dir = olive_recipes_dir / ".aitk" / "configs"
    models_dir = root_dir / "model_lab_configs"
    list = ModelList.Read(str(configs_dir))
    
    # Define files/patterns to ignore
    ignore_patterns = ["info.yml", "_copy.json.config"]
    
    for model in list.allModels():
        if not model.relativePath:
            continue
        # make dir
        target_dir = models_dir / Path(model.id) / Path(str(model.version))
        target_dir.mkdir(parents=True, exist_ok=True)
        source_dir = olive_recipes_dir / Path(model.relativePath)
        # copy dir
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True, 
                       ignore=shutil.ignore_patterns(*ignore_patterns))

if __name__ == "__main__":
    main()