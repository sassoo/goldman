"""
    resources.json_7159
    ~~~~~~~~~~~~~~~~~~~

    JSON based resource to be sub-classed with responders.
"""

import goldman

from ..resources.base import Resource as BaseResource


class Resource(BaseResource):
    """ Base JSON resource """

    DESERIALIZERS = [
        goldman.JSONDeserializer,
    ]

    SERIALIZERS = [
        goldman.JSONSerializer,
    ]
