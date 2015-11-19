"""
    resources.related
    ~~~~~~~~~~~~~~~~~

    Related resource object(s) with responders.

    Get the to-one or to-many relationship by name (related)
    of the model.
"""

import goldman
import goldman.exceptions as exceptions
import goldman.signals as signals

from ..resources.base import Resource as BaseResource
from goldman.utils.error_handlers import abort
from goldman.utils.responder_helpers import find, to_rest


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

        signals.responder_pre_any.send(self.model)
        signals.responder_pre_find.send(self.model)

        if not hasattr(self.model, related):
            abort(exceptions.InvalidURL(**{
                'detail': 'The {} resource does not have a related '
                          'resource named {}. This is an error, check '
                          'your spelling & retry.'.format(self.rtype, related)
            }))

        model = find(self.model, rid)
        model = getattr(model, related).load()

        if isinstance(model, list):
            props = [to_rest(m, includes=req.includes) for m in model]
        elif model:
            props = to_rest(model, includes=req.includes)
        else:
            props = model

        resp.serialize(props)

        signals.responder_post_any.send(self.model)
        signals.responder_post_find.send(self.model)
