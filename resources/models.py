"""
    resources.collection
    ~~~~~~~~~~~~~~~~~~~~

    Multiple items resource object with responders.
"""

import goldman
import falcon

from ..resources.base import Resource as BaseResource
from datetime import datetime as dt
from uuid import uuid4


class Resource(BaseResource):
    """ Multiple items resource & responders """

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

    def on_get(self, req, resp):
        """ Get the models identified by query parameters

        We return an empty list if no models are found.
        """

        responder = goldman.ModelResponder(self, req, resp)

        models = goldman.sess.store.search(self.model.rtype, **{
            'filters': responder.filters,
            'includes': responder.includes,
            'pages': responder.pages,
            'sorts': responder.sorts,
        })

        models = [m for m in models if m.acl_find(req.login)]
        models = [m.to_rest() for m in models]

        resp.serialize(models)

    def on_post(self, req, resp):
        """ Deserialize the payload & create the new single item """

        responder = goldman.ModelResponder(self, req, resp)
        props = req.deserialize()
        model = self.model()

        model.created = dt.utcnow()
        model.creator = goldman.sess.login
        model.updated = dt.utcnow()
        model.rid = str(uuid4())

        responder.from_rest(model, props)
        goldman.sess.store.create(model)

        resp.last_modified = model.updated
        resp.location = model.location
        resp.status = falcon.HTTP_201

        resp.serialize(responder.to_rest(model))
