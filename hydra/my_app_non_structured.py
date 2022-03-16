import logging
from dataclasses import dataclass
from typing import List, Optional

import hydra
from hydra.core.config_store import ConfigStore
from hydra.core.hydra_config import HydraConfig
from omegaconf import MISSING, DictConfig, OmegaConf

log = logging.getLogger(__name__)

"""
    python my_app_non_structured.py
    python my_app_non_structured.py db.user=suneeta    
    python my_app_non_structured.py db.user=suneeta --config-dir conf_custom_hydra
    python my_app_non_structured.py db.user=suneeta --config-name config_hydra
    # Multi-run
    python my_app_non_structured.py db.user=suneeta schema=school,support,warehouse  --config-dir conf_custom_hydra --multirun
    # Distributed environment 
"""


@hydra.main(config_path="conf", config_name="config")
def my_app(cfg: DictConfig) -> None:
    log.info("Type of cfg is: %s", type(cfg))
    cfg_dict = OmegaConf.to_container(cfg, throw_on_missing=False, resolve=True)

    log.info("Merged Yaml:\n%s", OmegaConf.to_yaml(cfg))

    log.info(cfg.db)
    log.info(cfg.db.driver)

    log.info(HydraConfig.get().job.name)


if __name__ == "__main__":
    my_app()
