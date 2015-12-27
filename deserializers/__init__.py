"""
    deserializers
    ~~~~~~~~~~~~~

    All deserializers supported by our API
"""

from ..deserializers.base import Deserializer as BaseDeserializer
from ..deserializers.comma_sep import Deserializer as CSVDeserializer
from ..deserializers.form_data import Deserializer as FormDataDeserializer
from ..deserializers.form_urlencoded import (
    Deserializer as FormUrlEncodedDeserializer
)
from ..deserializers.json_7159 import Deserializer as JSONDeserializer
from ..deserializers.jsonapi import Deserializer as JSONAPIDeserializer


DESERIALIZERS = [
    BaseDeserializer,
    CSVDeserializer,
    FormDataDeserializer,
    FormUrlEncodedDeserializer,
    JSONDeserializer,
    JSONAPIDeserializer,
]
