"""
    resources
    ~~~~~~~~~

    Location of our different resources for Falcon.

    Resources are responsible for registering responders & tend
    to follow the same general workflows for our Mongo documents.
"""

from ..resources.base import Resource as BaseResource
from ..resources.json_7159 import Resource as JSONResource
from ..resources.model import Resource as ModelResource
from ..resources.models import Resource as ModelsResource
from ..resources.related import Resource as RelatedResource
from ..resources.s3_model import Resource as S3ModelResource
from ..resources.s3_model_image import Resource as S3ModelImageResource


RESOURCES = [
    BaseResource,
    JSONResource,
    ModelResource,
    ModelsResource,
    RelatedResource,
    S3ModelResource,
    S3ModelImageResource,
]
