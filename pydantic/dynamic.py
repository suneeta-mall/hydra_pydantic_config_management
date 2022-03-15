from typing import List, Union
from pydantic import BaseModel, conint, validator

class Model(BaseModel):
    total_classes: Union[conint(ge=0), List[conint(ge=0)]]


    @validator("total_classes")
    def validate_classes(cls, total_classes: Union[conint(ge=0), List[conint(ge=0)]]) -> conint(ge=0):
        if isinstance(total_classes, List):
            return len(total_classes)
        return total_classes
