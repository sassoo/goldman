"""
    resources.collection
    ~~~~~~~~~~~~~~~~~~~~

    Multiple items resource object with responders.
"""

import goldman
import falcon

from ..resources.base import Resource as BaseResource
from goldman.utils.url_helpers import rid_url


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
        self.rtype = model.RTYPE

        super(Resource, self).__init__()

    def on_get(self, req, resp):
        """ Get the models identified by query parameters

        We return an empty list if no models are found.
        """

        responder = goldman.ModelResponder(self, req, resp)

        models = goldman.sess.store.search(self.rtype, **{
            'filters': req.filters,
            'includes': req.includes,
            'pages': req.pages,
            'sorts': req.sorts,
        })

        models = [responder.to_rest(model) for model in models]

        resp.serialize(models)

    def on_post(self, req, resp):
        """ Deserialize the payload & create the new single item """

        responder = goldman.ModelResponder(self, req, resp)
        props = req.deserialize()
        model = self.model()

        responder.from_rest(model, props)
        goldman.sess.store.create(model)

        resp.last_modified = model.updated
        resp.location = rid_url(self.rtype, model.rid_val)
        resp.status = falcon.HTTP_201

        resp.serialize(responder.to_rest(model))
