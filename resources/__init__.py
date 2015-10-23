"""
    resources
    ~~~~~~~~~

    Location of our different resources for Falcon.

    Resources are responsible for registering responders & tend
    to follow the same general workflows for our Mongo documents.
"""

from ..resources.base import Resource as BaseResource
from ..resources.model import Resource as ModelResource
from ..resources.models import Resource as ModelsResource


RESOURCES = [
    BaseResource,
    ModelResource,
    ModelsResource,
]
