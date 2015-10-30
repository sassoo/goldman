"""
    resources.item
    ~~~~~~~~~~~~~~

    Single item resource object with responders.

    This can be used directly or sub-classed for handling common
    methods against single items.
"""

import goldman
import falcon

from ..resources.base import Resource as BaseResource
from datetime import datetime as dt


class Resource(BaseResource):
    """ Single item resource & responders """

    DESERIALIZERS = [
        goldman.JSONAPIDeserializer,
    ]

    SERIALIZERS = [
        goldman.CSVSerializer,
        goldman.JSONAPISerializer,
    ]

    def __init__(self, model):

        self.model = model

        super(Resource, self).__init__()

    def on_delete(self, req, resp, rid):
        """ Delete the single item

        Upon a successful deletion an empty bodied 204
        is returned.
        """

        responder = goldman.ModelResponder(self, req, resp)
        model = responder.find(rid)

        goldman.sess.store.delete(model)

        resp.status = falcon.HTTP_204

    def on_get(self, req, resp, rid):
        """ Find the model by id & serialize it back """

        responder = goldman.ModelResponder(self, req, resp)
        model = responder.find(rid)

        resp.last_modified = model.updated
        resp.location = model.location

        resp.serialize(responder.to_rest(model))

    def on_patch(self, req, resp, rid):
        """ Deserialize the payload & update the single item """

        responder = goldman.ModelResponder(self, req, resp)
        props = req.deserialize()
        model = responder.find(rid)

        model.updated = dt.utcnow()
        responder.from_rest(model, props)

        goldman.sess.store.update(model)

        resp.last_modified = model.updated
        resp.location = model.location

        resp.serialize(responder.to_rest(model))
