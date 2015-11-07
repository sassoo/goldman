"""
    resources.related
    ~~~~~~~~~~~~~~~~~

    Related resource object(s) with responders.

    Get the to-one or to-many relationship by name (related)
    of the model.
"""

import goldman
import goldman.exceptions as exceptions

from ..resources.base import Resource as BaseResource
from goldman.utils.error_handlers import abort


class Resource(BaseResource):
    """ Related item(s) resource & responders """

    DESERIALIZERS = [
        goldman.JSONAPIDeserializer,
    ]

    SERIALIZERS = [
        goldman.CSVSerializer,
        goldman.JSONAPISerializer,
    ]

    def __init__(self, model):

        self.model = model
        self.rtype = model.RTYPE

        super(Resource, self).__init__()

    def on_get(self, req, resp, rid, related):
        """ Find the related model & serialize it back

        If the parent resource of the related model doesn't
        exist then abort on a 404.
        """

        if not hasattr(self.model, related):
            abort(exceptions.InvalidURL(**{
                'detail': 'The {} resource does not have a related '
                          'resource named {}. This is an error, check '
                          'your spelling & retry.'.format(self.rtype, related)
            }))

        rondr = goldman.ModelResponder(self, req, resp)
        model = rondr.find(self.rtype, rid)
        model = getattr(model, related).load()

        if isinstance(model, list):
            props = [rondr.to_rest(m, includes=req.includes) for m in model]
        elif model:
            props = rondr.to_rest(model, includes=req.includes)
        else:
            props = model

        resp.location = req.path

        resp.serialize(props)
