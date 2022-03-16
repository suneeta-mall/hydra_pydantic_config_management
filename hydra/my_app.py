import logging
from dataclasses import dataclass
from typing import List, Optional

import hydra
from hydra.core.config_store import ConfigStore
from hydra.core.hydra_config import HydraConfig
from omegaconf import MISSING, OmegaConf

log = logging.getLogger(__name__)


@dataclass
class DBConfig:
    user: str = MISSING
    pwd: str = MISSING
    driver: str = MISSING
    timeout: int = 100


@dataclass
class MySQLConfig(DBConfig):
    driver: str = "mysql"


@dataclass
class PostGreSQLConfig(DBConfig):
    driver: str = "postgresql"


@dataclass
class View:
    create_db: bool = False
    view: bool = MISSING


@dataclass
class Table:
    name: str = MISSING


@dataclass
class Schema:
    database: str = "school"
    tables: List[Table] = MISSING


@dataclass
class Config:
    # We can now annotate db as DBConfig which
    # improves both static and dynamic type safety.
    db: DBConfig
    ui: View
    schema: Schema


cs = ConfigStore.instance()
cs.store(name="config", node=Config)
cs.store(group="db", name="mysql", node=MySQLConfig)
cs.store(group="db", name="postgresql", node=PostGreSQLConfig)
cs.store(name="ui", node=View)
cs.store(name="schema", node=Schema)

"""
    python my_app.py
    python my_app.py db.user=suneeta    
    python my_app.py db.user=suneeta --config-dir conf_custom_hydra
    # python my_app.py db.user=suneeta --config-name config_hydra
    # Multi-run
    python my_app.py db.user=suneeta schema=school,support,warehouse  --config-dir conf_custom_hydra --multirun
    # Distributed environment like RANK
"""


@hydra.main(config_path="conf", config_name="config")
def my_app(cfg: Config) -> None:    
    log.info("Type of cfg is: %s", type(cfg))
    cfg_dict = OmegaConf.to_container(cfg, throw_on_missing=False, resolve=True)

    cfg_obj = OmegaConf.to_object(cfg)
    logging.info("type of Object is %s", type(cfg_obj))
    log.info("Merged Yaml:\n%s", OmegaConf.to_yaml(cfg))

    log.info(cfg.db)
    log.info(cfg_obj.db)
    log.info(cfg_obj.db.driver)
    log.info(cfg.db.driver)

    log.info(HydraConfig.get().job.name)

if __name__ == "__main__":
    my_app()


