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

    def __init__(self, model):

        self.model = model
        self.rtype = model.RTYPE

        super(Resource, self).__init__()

    def on_get(self, req, resp):
        """ Get the models identified by query parameters

        We return an empty list if no models are found.
        """

        rondr = goldman.ModelResponder(self, req, resp)
        model = goldman.sess.store.search(self.rtype, **{
            'filters': req.filters,
            'pages': req.pages,
            'sorts': req.sorts,
        })

        props = [rondr.to_rest(m, includes=req.includes) for m in model]
        resp.location = req.path

        resp.serialize(props)

    def on_post(self, req, resp):
        """ Deserialize the payload & create the new single item """

        rondr = goldman.ModelResponder(self, req, resp)
        props = req.deserialize()
        model = self.model()

        rondr.from_rest(model, props)
        goldman.sess.store.create(model)

        resp.last_modified = model.updated
        resp.location = req.path + '/' + model.rid_value
        resp.status = falcon.HTTP_201

        resp.serialize(rondr.to_rest(model))
