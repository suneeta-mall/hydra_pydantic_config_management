#


## Hydra

### Unstructured config

```bash
cd intro
python my_app_non_structured.py
python my_app_non_structured.py db.user=suneeta    
python my_app_non_structured.py db.user=suneeta --config-dir conf_custom_hydra
python my_app_non_structured.py db.user=suneeta --config-name config_hydra
# Multi-run
python my_app_non_structured.py db.user=suneeta schema=school,support,warehouse  --config-dir conf_custom_hydra --multirun
# Distributed environment 
```


### Structured config

```bash
cd intro
python my_app.py
python my_app.py db.user=suneeta    
python my_app.py db.user=suneeta --config-dir conf_custom_hydra
# python my_app.py db.user=suneeta --config-name config_hydra
# Multi-run
python my_app.py db.user=suneeta schema=school,support,warehouse  --config-dir conf_custom_hydra --multirun
# Distributed environment like RANK
```


## Pydantic

Data class structured config example is shown [here](pydantic/model_dc.py), BaseMode structured config is [here](pydantic/model.py) and dynamic config example is [here](pydantic/dynamic.py)

## Pydantic and Hydra

```bash
cd pydra
python example.py model=resnet_v3
python example.py model=resnet_v3 +model.zoom=25
python example.py model=resnet_v2_interpolate
python example.py
python example.py model.context=512 dataset.name=IMAGENET +model.zoom=21
python example.py --config-path outputs/example/2022-03-10_12-51-45/.hydra/ --config-name config
```