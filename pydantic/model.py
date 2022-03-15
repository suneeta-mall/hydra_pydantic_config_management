import logging
import sys
from pathlib import Path
from typing import Optional, Tuple, Union

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


log = logging.getLogger(__name__)


class Dataset(BaseModel):
    name: str
    path: str

    @validator("path")
    def validate_path(cls, path: str) -> Path:
        if Path(path).exists():
            print("exist")
        return Path(path)

    class Config:
        title = "Dataset"
        max_anystr_length = 10
        allow_mutation = False
        validate_assignment = True
        anystr_lower = True
        validate_all = True
        use_enum_values = True        


class Model(BaseModel):
    type: str
    num_layers: conint(ge=3)
    width: Optional[conint(ge=0)]

    @validator("type")
    def validate_supported_type(cls, type: str) -> str:
        if type not in ["alex", "le"]:
            raise ValueError(f"'type' canonly be [alex, le] got: {type}")
        return type


class Secrets(BaseSettings):
    api_key: str = Field("", env="api_key")
    token: str

    class Config:
        # case_sensitive = True
        env_nested_delimiter = "_"

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


class Config(BaseModel):
    dataset: Dataset
    model: Model
    secret: Secrets







if __name__ == "__main__":    
    print(Config.schema_json(indent=2))