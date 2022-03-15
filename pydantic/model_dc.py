import logging
import sys
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, conint, validator
from pydantic.dataclasses import dataclass


log = logging.getLogger(__name__)


@dataclass
class Dataset:
    name: str
    path: str

    @validator("path")
    def validate_path(cls, path: str) -> Path:
        if Path(path).exists():
            print("exist")
        return Path(path)


@dataclass
class Model:
    type: str
    num_layers: conint(ge=3)
    width: Optional[conint(ge=0)]

    @validator("type")
    def validate_supported_type(cls, type: str) -> str:
        if type not in ["alex", "le"]:
            raise ValueError(f"'type' canonly be [alex, le] got: {type}")
        return type


@dataclass
class Config:
    dataset: Dataset
    model: Model





