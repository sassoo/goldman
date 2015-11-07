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
        self.rtype = model.RTYPE

        super(Resource, self).__init__()

    def on_delete(self, req, resp, rid):
        """ Delete the single item

        Upon a successful deletion an empty bodied 204
        is returned.
        """

        rondr = goldman.ModelResponder(self, req, resp, rid=rid)
        model = rondr.find(self.rtype, rid)

        goldman.sess.store.delete(model)

        resp.status = falcon.HTTP_204

    def on_get(self, req, resp, rid):
        """ Find the model by id & serialize it back """

        rondr = goldman.ModelResponder(self, req, resp, rid=rid)
        model = rondr.find(self.rtype, rid)
        props = rondr.to_rest(model, includes=req.includes)

        resp.last_modified = model.updated
        resp.location = req.path

        resp.serialize(props)

    def on_patch(self, req, resp, rid):
        """ Deserialize the payload & update the single item """

        rondr = goldman.ModelResponder(self, req, resp, rid=rid)
        props = req.deserialize()
        model = rondr.find(self.rtype, rid)

        rondr.from_rest(model, props)
        goldman.sess.store.update(model)

        props = rondr.to_rest(model, includes=req.includes)
        resp.last_modified = model.updated
        resp.location = req.path

        resp.serialize(props)
