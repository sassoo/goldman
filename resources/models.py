"""
    resources.collection
    ~~~~~~~~~~~~~~~~~~~~

    Multiple items resource object with responders.
"""

import goldman
import falcon

from ..resources.base import Resource as BaseResource


class Resource(BaseResource):
    """ Multiple items resource & responders """

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

    def on_get(self, req, resp):
        """ Get the models identified by query parameters

        We return an empty list if no models are found.
        """

        crud = goldman.RestResponder(req, self.model)

        models = store.search(self.model.rtype, **{
            'filters': crud.filters,
            'includes': crud.includes,
            'pages': crud.pages,
            'sorts': crud.sorts,
        })

        models = [m for m in models if m.acl_find(req.login)]
        models = [m.to_rest() for m in models]

        resp.serialize(models)

    def on_post(self, req, resp):
        """ Deserialize the payload & create the new single item """

        responder = goldman.ModelResponder(self, req, resp)
        props = req.deserialize()
        model = responder.create(props)

        resp.last_modified = model.updated
        resp.location = model.location
        resp.status = falcon.HTTP_201

        resp.serialize(responder.to_rest(model))
