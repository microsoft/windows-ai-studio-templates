# Versioning (WIP)

## Incremental patching

If the main version is not changed, we should support incremental patching, i.e. when new configs are added or new features are added, the previous created projects should support it smoothly.

This requires that if the new template will modify existing user script, ipynb etc., it should not do so and create new one instead.

## Json config patching

If the json config needs to be updated with user script change etc. and it only happens for one config, we could consider using patch. Patch will be compatible with previous versions and will look like:

Files in current template folder:

- qdq.json: the latest olive json, i.e. patch 2
- qdq.json.config: targeting patch 0, i.e. original one 
- qdq.o.json.config: original json
- qdq.p2.json.config: ux config for patch 2
- qdq.p1.json.config: ux config for patch 1
- qdq.o1.json.config: olive json for patch 1

Change in model_project.config:

```
{
    "name": "Convert to QDQ",
    "file": "qdq.json",
    "template": "huggingface/google/vit-base-patch16-224",
    "version": 1,
    "templateName": "qdq",
    "patch": 2
}
```

## Main version bump

Everything needs to be created again in this case.
