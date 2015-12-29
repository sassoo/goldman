"""
    serializers
    ~~~~~~~~~~~

    Location of different serializers supported by our API
"""

from ..serializers.base import Serializer as BaseSerializer
from ..serializers.comma_sep import Serializer as CSVSerializer
from ..serializers.json_7159 import Serializer as JSONSerializer
from ..serializers.jsonapi import Serializer as JSONAPISerializer


SERIALIZERS = [
    BaseSerializer,
    CSVSerializer,
    JSONSerializer,
    JSONAPISerializer,
]
