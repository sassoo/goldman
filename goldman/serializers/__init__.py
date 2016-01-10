"""
    serializers
    ~~~~~~~~~~~

    Location of different serializers supported by our API
"""

from ..serializers.base import Serializer as BaseSerializer
from ..serializers.comma_sep import Serializer as CsvSerializer
from ..serializers.json_7159 import Serializer as JsonSerializer
from ..serializers.jsonapi import Serializer as JsonApiSerializer


SERIALIZERS = [
    BaseSerializer,
    CsvSerializer,
    JsonSerializer,
    JsonApiSerializer,
]
