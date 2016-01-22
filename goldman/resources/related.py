"""
    resources.related
    ~~~~~~~~~~~~~~~~~

    Related resource object(s) with responders.

    Get the to-one or to-many relationship by name (related)
    of the model.
"""

import goldman
import goldman.signals as signals

from ..resources.base import Resource as BaseResource
from goldman.exceptions import InvalidURL
from goldman.utils.error_helpers import abort
from goldman.utils.responder_helpers import (
    find,
    to_rest_model,
    to_rest_models,
)


class Resource(BaseResource):
    """ Related item(s) resource & responders """

    DESERIALIZERS = [
        goldman.JsonApiDeserializer,
    ]

    SERIALIZERS = [
        goldman.CsvSerializer,
        goldman.JsonApiSerializer,
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

        signals.pre_req.send(self.model)
        signals.pre_req_find.send(self.model)

        if not hasattr(self.model, related):
            abort(InvalidURL(**{
                'detail': 'The "%s" resource does not have a related '
                          'resource named "%s". This is an error, check '
                          'your spelling & retry.' % (self.rtype, related)
            }))

        model = find(self.model, rid)
        try:
            model_related = getattr(model, related).load()
        except AttributeError:
            model_related = None

        if isinstance(model_related, list):
            props = to_rest_models(model_related, includes=req.includes)
        elif model:
            props = to_rest_model(model_related, includes=req.includes)
        else:
            props = model_related

        resp.serialize(props)

        signals.post_req.send(self.model)
        signals.post_req_find.send(self.model)
