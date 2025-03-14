# Parameters that set by sanitize.py

- model_list.json:
    + version: read from folder structure
- modelspace.config
    + template, version, templateName: same as path
    + So only name and file is needed
- *.json.config
    + For parameters with template, it will be removed so filled from templateParameters
    + For templateParameters, unset parameters will be updated from template and save in parameters
    + So normally for templateParameter, we only need to set template and path and everything else could be set from template

# Requirements

- output model use external weight ?
- no evaluate input model ?
- separate different datasets ?
