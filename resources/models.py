"""
    resources.models
    ~~~~~~~~~~~~~~~~

    Multiple models resource object with responders.
"""

import falcon
import goldman
import goldman.signals as signals

from ..resources.base import Resource as BaseResource
from goldman.utils.responder_helpers import from_rest, to_rest


def on_get(resc, req, resp):
    """ Get the models identified by query parameters

    We return an empty list if no models are found.
    """

    signals.responder_pre_any.send(resc.model)
    signals.responder_pre_search.send(resc.model)

    model = goldman.sess.store.search(resc.rtype, **{
        'filters': req.filters,
        'pages': req.pages,
        'sorts': req.sorts,
    })

    props = [to_rest(m, includes=req.includes) for m in model]

    resp.serialize(props)

    signals.responder_post_any.send(resc.model)
    signals.responder_post_search.send(resc.model)


def on_post(resc, req, resp):
    """ Deserialize the payload & create the new single item """

    signals.responder_pre_any.send(resc.model)
    signals.responder_pre_create.send(resc.model)

    props = req.deserialize()
    model = resc.model()

    from_rest(model, props)
    goldman.sess.store.create(model)

    resp.last_modified = model.updated
    resp.location = '%s/%s' % (req.path, model.rid_value)
    resp.status = falcon.HTTP_201

    resp.serialize(to_rest(model))

    signals.responder_post_any.send(resc.model)
    signals.responder_post_create.send(resc.model)


class Resource(BaseResource):
    """ Multiple items resource & responders """

    DESERIALIZERS = [
        goldman.JSONAPIDeserializer,
    ]

    SERIALIZERS = [
        goldman.CSVSerializer,
        goldman.JSONAPISerializer,
    ]

    def __init__(self, model, disable=None):

        self.model = model
        self.rondrs = [on_get, on_post]
        self.rtype = model.RTYPE

        super(Resource, self).__init__(disable)
