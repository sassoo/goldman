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

    signals.pre_req.send(resc.model)
    signals.pre_req_delete.send(resc.model)

    model = find(resc.model, rid)
    goldman.sess.store.delete(model)

    resp.status = falcon.HTTP_204

    signals.post_req.send(resc.model)
    signals.post_req_delete.send(resc.model)


def on_get(resc, req, resp, rid):
    """ Find the model by id & serialize it back """

    signals.pre_req.send(resc.model)
    signals.pre_req_find.send(resc.model)

    model = find(resc.model, rid)
    props = to_rest_model(model, includes=req.includes)

    resp.last_modified = model.updated
    resp.serialize(props)

    signals.post_req.send(resc.model)
    signals.post_req_find.send(resc.model)


def on_patch(resc, req, resp, rid):
    """ Deserialize the payload & update the single item """

    signals.pre_req.send(resc.model)
    signals.pre_req_update.send(resc.model)

    props = req.deserialize()
    model = find(resc.model, rid)

    from_rest(model, props)
    goldman.sess.store.update(model)

    props = to_rest_model(model, includes=req.includes)
    resp.last_modified = model.updated
    resp.serialize(props)

    signals.post_req.send(resc.model)
    signals.post_req_update.send(resc.model)


class Resource(BaseResource):
    """ Single item resource & responders """

    DESERIALIZERS = [
        goldman.JsonApiDeserializer,
    ]

    SERIALIZERS = [
        goldman.CsvSerializer,
        goldman.JsonApiSerializer,
    ]

    def __init__(self, model, disable=None):

        self.model = model
        self.rondrs = [on_delete, on_get, on_patch]
        self.rtype = model.RTYPE

        super(Resource, self).__init__(disable)
