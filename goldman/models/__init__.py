"""
    models
    ~~~~~~

    Module containing all of our models that are typically
    accessed in a CRUD like manner.
"""

from ..models.base import Model as BaseModel
from ..models.default_schema import Model as DefaultSchemaModel
from ..models.login import Model as LoginModel


MODELS = [
    BaseModel,
    DefaultSchemaModel,
    LoginModel,
]
