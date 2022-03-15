import abc
import logging
import re
import sys
from pathlib import Path
from typing import Any, Literal, Optional, Tuple, Type, TypeVar, Union
import logging 
from hydra.core.hydra_config import HydraConfig

from omegaconf import DictConfig, OmegaConf
from pydantic import (
    BaseModel,
    BaseSettings,
    Field,
    PositiveInt,
    conint,
    constr,
    schema,
    schema_json_of,
    validator,
)
from pydantic.dataclasses import dataclass
from pydantic.env_settings import SettingsSourceCallable
from typing_extensions import Annotated

import hydra
from hydra.core.config_store import ConfigStore

log = logging.getLogger(__name__)


class Secrets(BaseSettings):
    api_key: str = Field("", env="api_key")
    token: str

    class Config:        
        env_nested_delimiter = "_"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


# https://pydantic-docs.helpmanual.io/usage/dataclasses/
# https://github.com/samuelcolvin/pydantic/issues/710
# https://stackoverflow.com/questions/62011741/pydantic-dataclass-vs-basemodel
# hydra does not work with BaseModel but pydentic dataclasses


class Dataset(BaseModel):
    name: str
    path: str
    zoom: conint(gt=18) = 19

    class Config:
        title = "Dataset"
        # max_anystr_length = 10
        allow_mutation = False
        validate_assignment = True
        anystr_lower = True
        validate_all = True
        use_enum_values = True

    @validator("path")
    def validate_path(cls, path: str) -> Path:
        p = Path(path)
        if p.exists():
            print("exist")
        return p


log.info("Dataset schema:\n%s", Dataset.schema_json(indent=2))


VBT = TypeVar("VBT", bound="VersionModel")


class VersionModel(BaseModel, abc.ABC):
    v: Literal["inf"] = Field(float("inf"), const=True)

    class Config:
        title = "Model"
        allow_mutation = False
        max_anystr_length = 10
        validate_assignment = True
        anystr_lower = True
        validate_all = True
        use_enum_values = True

    def version(self) -> float:
        return self.v

    def _next_version_model(self) -> float:
        versions = list(fake_registry.keys())
        versions.sort()
        idx = versions.index(self.v) + 1
        if idx == len(versions):
            return None
        return versions[idx]

    def next_version(self) -> BaseModel:
        next_class = fake_registry.get(self._next_version_model())
        return next_class

    @abc.abstractmethod
    def to_next(self) -> BaseModel:
        pass


class Model1(VersionModel):
    # https://pydantic-docs.helpmanual.io/usage/types/#arguments-to-constr
    type: str  # constr(to_lower=True)
    num_layers: conint(ge=3)
    width: Optional[conint(ge=0)]
    # v: float = Field(1.0, const=True)
    zoom: conint(gt=18) = 19
    v: Literal[1.0] = Field(1.0, const=True)

    # @classmethod
    # def to_next(cls, instance: Type[VBT]) -> BaseModel:
    def to_next(self) -> Optional[BaseModel]:
        next_class = self.next_version()
        if next_class != Model2:
            raise Exception("WTH")

        logging.warning("================================================")
        logging.warning("==============Migrating from 1->2 ==============")
        logging.warning("================================================")

        d = self.dict()
        d.pop("v")
        return Model2(**d)


class Model2(Model1):
    width: conint(ge=5)
    context: conint(ge=256) = 256
    # v: float = Field(2.0, const=True)
    v: Literal[2.0] = Field(2.0, const=True)

    def to_next(self) -> Optional[BaseModel]:
        next_class = self.next_version()
        if next_class != Model3:
            raise Exception("WTH")

        logging.warning("================================================")
        logging.warning("==============Migrating from 2->3 ==============")
        logging.warning("================================================")

        return Model3(
            new_context=self.context,
            num_layers=self.num_layers,
            type=self.type,
            width=self.width,
            zoom=self.zoom,
        )

class Model3(Model1):
    new_context: conint(ge=512, le=1300) = 512
    v: Literal[3.0] = Field(3.0, const=True)

    def to_next(self) -> Optional[BaseModel]:
        logging.warning("================================================")
        logging.warning("============== Latest no migration =============")
        logging.warning("================================================")

        return None




def migrate_to_latest(source_vm: VersionModel) -> VersionModel:
    version_ls = list(fake_registry.keys())
    version_ls.sort()
    source_idx = version_ls.index(source_vm.v)
    if source_idx + 1 == len(version_ls):
        return source_vm
    
    vm = source_vm
    for _ in version_ls[source_idx + 1 :]:
        vm = vm.to_next()

    return vm


class Model(BaseModel):
    # model: Union[Model1, Model2, Model3]
    
    def __new__(cls, **kwargs) -> VersionModel:
        if "v" not in kwargs:
            raise Exception("Missing version info cant handle ")
        clazz = fake_registry.get(kwargs["v"])
        current_obj = clazz(**kwargs)
        current_obj = migrate_to_latest(current_obj)
        return current_obj

    @classmethod
    def schema_json(
        cls, *, by_alias: bool = True, ref_template: str = None, **dumps_kwargs: Any
    ) -> str:
        _Models = Annotated[Union[Model1, Model2, Model3], Field(discriminator="v")]
        _schema = schema_json_of(_Models, title="Model Schema", indent=2)
        return _schema        




fake_registry = {1.0: Model1, 2.0: Model2, 3.0: Model3}


class Config(BaseModel):
    dataset: Dataset
    model: Model
    secrets: Secrets


# cs = ConfigStore.instance()
# cs.store(name="config", node=Config)
# cs.store(name="dataset", node=Dataset)
# # cs.store(name="model", node=Model)
# cs.store(group="model", name="std", node=Model)

'''
    python example.py model=resnet_v3
    python example.py model=resnet_v3 +model.zoom=25
    python example.py model=resnet_v2_interpolate
    python example.py
    python example.py model.context=512 dataset.name=IMAGENET +model.zoom=21
    python example.py --config-path outputs/example/2022-03-10_12-51-45/.hydra/ --config-name config
'''

@hydra.main(config_path="conf", config_name="config")
def experiment(cfg: Config) -> None:
    log.info("Info level message")
    
    # _Models = Annotated[Union[Model1, Model2, Model3], Field(discriminator="v")]
    # log.info(schema_json_of(_Models, title="Model Schema", indent=2))
    log.info(Model.schema_json(indent=2))
    
    Config.schema_json(indent=2)
    
    log.info(HydraConfig.get().job.name)    
    # conf = OmegaConf.load('source/example.yaml')
    OmegaConf.resolve(cfg)
    r_model = Config(**cfg)
    x_conf = OmegaConf.to_object(cfg)

    log.info(f"Title={cfg.dataset.name}, size={cfg.model.type}")
    log.info(x_conf)
    log.info(r_model)

    log.info(OmegaConf.to_yaml(cfg))


if __name__ == "__main__":
    experiment()
