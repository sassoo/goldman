"""
    resources.item
    ~~~~~~~~~~~~~~

    Single item resource object with responders.

    This can be used directly or sub-classed for handling common
    methods against single items. Approved methods are currently:

        DELETE, GET, PATCH, POST
"""

import goldman
import goldman.exceptions as exceptions
import falcon

from ..resources.base import Resource as BaseResource
# from app.store import store
from goldman.utils.error_handlers import abort
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

    def __init__(self, model, store):

        self.model = model
        self.store = store

        super(Resource, self).__init__()

    def on_delete(self, req, resp, uuid):
        """ Delete the single item

        Upon a successful deletion an empty bodied 204
        is returned.
        """

        model = goldman.RestResponder(req, self.model).find(uuid)

        if not model.acl_delete(req.login):
            abort(exceptions.ModificationDenied)

        self.store.delete(model)

        resp.status = falcon.HTTP_204

    def on_get(self, req, resp, uuid):
        """ Find the model by id & serialize it back """

        rest = goldman.RestResponder(req, self.model)
        model = rest.find(self.store, uuid)

        resp.last_modified = model.updated
        resp.location = model.location

        resp.serialize(rest.to_rest(model))

    def on_patch(self, req, resp, uuid):
        """ Deserialize the payload & update the single item """

        model = goldman.RestResponder(req, self.model).find(uuid)

        props = req.deserialize()
        model.updated = dt.utcnow()

        model.from_rest(props)

        if not model.acl_update(req.login) or not model.acl_save(req.login):
            abort(exceptions.ModificationDenied)

        self.store.update(model)

        resp.last_modified = model.updated
        resp.location = model.location

        resp.serialize(model.to_rest())
