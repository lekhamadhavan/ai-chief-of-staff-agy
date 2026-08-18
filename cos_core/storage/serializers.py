from typing import Type, TypeVar, Any, Dict, List
import yaml
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def model_to_yaml(model: BaseModel) -> str:
    """Serializes a Pydantic model to a YAML string."""
    data = model.model_dump(mode="json")
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)

def yaml_to_model(yaml_str: str, model_cls: Type[T]) -> T:
    """Deserializes a YAML string to a Pydantic model with schema validation."""
    data = yaml.safe_load(yaml_str) or {}
    return model_cls.model_validate(data)

def model_list_to_yaml(models: List[BaseModel]) -> str:
    """Serializes a list of Pydantic models to YAML string."""
    data = [m.model_dump(mode="json") for m in models]
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)

def yaml_to_model_list(yaml_str: str, model_cls: Type[T]) -> List[T]:
    """Deserializes a YAML string containing a list to Pydantic models."""
    data = yaml.safe_load(yaml_str) or []
    if not isinstance(data, list):
        data = [data]
    return [model_cls.model_validate(item) for item in data]
