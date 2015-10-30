"""
    models
    ~~~~~~

    Module containing all of our models that are typically
    accessed in a CRUD like manner.
"""

from ..models.base import Model as BaseModel
from ..models.common import Model as CommonModel


MODELS = [
    BaseModel,
    CommonModel,
]
