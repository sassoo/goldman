"""
    resources.model
    ~~~~~~~~~~~~~~~

    Single model resource object with responders.

    This can be used directly or sub-classed for handling common
    methods against single models.
"""

import falcon
import goldman
import goldman.signals as signals

from ..resources.base import Resource as BaseResource
from goldman.utils.responder_helpers import (
    find,
    from_rest,
    to_rest_model,
)


def on_delete(resc, req, resp, rid):  # pylint: disable=unused-argument
    """ Delete the single item

    Upon a successful deletion an empty bodied 204
    is returned.
    """

    signals.responder_pre_any.send(resc.model)
    signals.responder_pre_delete.send(resc.model)

    model = find(resc.model, rid)
    goldman.sess.store.delete(model)

    resp.status = falcon.HTTP_204

    signals.responder_post_any.send(resc.model)
    signals.responder_post_delete.send(resc.model)


def on_get(resc, req, resp, rid):
    """ Find the model by id & serialize it back """

    signals.responder_pre_any.send(resc.model)
    signals.responder_pre_find.send(resc.model)

    model = find(resc.model, rid)
    props = to_rest_model(model, includes=req.includes)

    resp.last_modified = model.updated
    resp.serialize(props)

    signals.responder_post_any.send(resc.model)
    signals.responder_post_find.send(resc.model)


def on_patch(resc, req, resp, rid):
    """ Deserialize the payload & update the single item """

    signals.responder_pre_any.send(resc.model)
    signals.responder_pre_update.send(resc.model)

    props = req.deserialize()
    model = find(resc.model, rid)

    from_rest(model, props)
    goldman.sess.store.update(model)

    props = to_rest_model(model, includes=req.includes)
    resp.last_modified = model.updated
    resp.serialize(props)

    signals.responder_post_any.send(resc.model)
    signals.responder_post_update.send(resc.model)


class Resource(BaseResource):
    """ Single item resource & responders """

    DESERIALIZERS = [
        goldman.JSONAPIDeserializer,
    ]

    SERIALIZERS = [
        goldman.CSVSerializer,
        goldman.JSONAPISerializer,
    ]

    def __init__(self, model, disable=None):

        self.model = model
        self.rondrs = [on_delete, on_get, on_patch]
        self.rtype = model.RTYPE

        super(Resource, self).__init__(disable)
