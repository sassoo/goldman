"""
    resources.collection
    ~~~~~~~~~~~~~~~~~~~~

    Multiple items resource object with responders.
"""

import goldman
import goldman.exceptions as exceptions
import falcon

from ..resources.base import Resource as BaseResource
# from app.store import store
from datetime import datetime as dt
from goldman.utils.error_handlers import abort
from uuid import uuid4


class Resource(BaseResource):
    """ Multiple items resource & responders """

    def __init__(self, model):

        self.model = model

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

        props = req.deserialize()
        model = self.model()

        model.created = dt.utcnow()
        # model.creator = login
        model.updated = dt.utcnow()
        model.uuid = str(uuid4())

        model.from_rest(props)

        if not model.acl_create(req.login) or not model.acl_save(req.login):
            abort(exceptions.ModificationDenied)

        store.create(model)

        resp.last_modified = model.updated
        resp.location = model.location
        resp.status = falcon.HTTP_201

        resp.serialize(model.to_rest())
