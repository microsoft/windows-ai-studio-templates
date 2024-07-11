# Templates Contribution Guide

This document provide guidance for AI toolkit templates development. A template generator in the extension will help to generate project files from the templates. 

## How to add new template?
1. Add configuration for your model in [index.json](./index.json).

1. Add your template code in folder `models/<your-model-name>/`. Template files should use `.mustache` file extension if they contain dynamic content that the generator needs to process and define your dynamic content with [{{ mustache }}](https://mustache.github.io/) syntax. You can refer to the [sample template](./models/llama-v2-7b/) to add your template code.

1. Add default values for project settings in `configs/<your-model-name>/defaultProjectSettings.json` file.

1. Add `configs/<your-model-name>/templateInput.json` to include any other input used to resolve Mustache variable in the model template.

1. Ensure that all Mustache variables used in your template are defined in one of the following:
    1. `defaultProjectSettings.json`: the default project settings which might overrode by user's input.
    2. `templateInput.json`: variables not belong to user input but required to resolve in template.
    3. Pre-defined variables: Templates can reference pre-defined mustache variables which are handled specifically by the generator, including
        * `{{modelId}}`: The scaffold workflow will resolve the `modelId` according to the user's model selection.
        * `{{isLocalDataFile}}`: A boolean value that defines whether the dataset is from a local file or a HuggingFace dataset.

>  **Note**: In the new scaffold workflow, the extension will utilize [configs/projectSettings.json.mustache](./configs/projectSettings.json.mustache) to render a dynamic form for collecting user input during scaffolding. Currently, all models share the same project settings template, with variations in default values (defined in the `defaultProjectSettings.json`) for certain configuration keys between models.

## How to debug templates?
This repository will be included in the `templates` sub-folder of the extension's source code repository via Git submodules. To debug templates locally in VS Code:

1. Run `npm run build` in the templates folder to apply your changes.
1. Build your extension code and press F5 to start the AI toolkit extension locally.
1. Scaffold a fine-tuning project that uses your updated template to preview the changes.

## How to release templates?
For release, templates will be packaged into zip packages and published to GitHub releases. We will use [semantic versioning](https://semver.org/) for version control of templates packages. The version of the templates is specified in the [version.txt](./version.txt).

To release a new version of templates:
* Bump the version correctly in [version.txt](./version.txt).
    * For breaking changes in the templates, the major version should be incremented.
    * For hotfix to a specific release, increment the patch version. 

*  Update template version in `templateConfig.json` in the extension repo.

    ```json
    // templateConfig.json file content
    {
        "templateVersion": "~0.4",
        ...
    }
    ```
    > Note: The extension will maintain a template configuration that includes the compatible version of the templates. During scaffolding, the extension will download the latest version that matches the specified version.

* Trigger CD pipeline to publish the template packages and package templates in extension.
    * For each extension release, a specific version of the template will be packaged into the extension package.
    * By default, the extension will use the local template zip unless a new patch version is found.
    * If a new patch version is found
        * and doesn’t exists in local cache, generator will download the newer version from GitHub releases
        * and exists in local cache, generator will use the package from cache folder.

**What is BREAKING CHANGE for templates?**

Overall, any change to the template that makes it incompatible with older versions of AITK should be considered a breaking change. For example:

* Adding new placeholders in templates that need to update the generator to handle it.
* Removing or renaming templates.

