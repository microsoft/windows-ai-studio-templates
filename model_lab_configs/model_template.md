# Parameters that set by sanitize.py

- model_list.json:
    + version: read from folder structure
- model_project.config
    + template, version, templateName: same as path
    + phases: read from olive config
    + modelInfo: copy from model_list
    + So only name and file is needed
- *.json.config
    + For parameter, we either set every needed property except template
    + Or set template name and properties different from template in template

# Olive json Requirements

- engine not used: place everything in the root
- output model use external weight ?
- separate different datasets
    + currently no check in sanitize.py
