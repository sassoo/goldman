"""
    resources.model
    ~~~~~~~~~~~~~~~

    Single model resource object with responders.

    This can be used directly or sub-classed for handling common
    methods against single models.
"""

import falcon
import goldman
import goldman.exceptions as exceptions
import goldman.signals as signals

from goldman.utils.responder_helpers import (
    from_rest,
    to_rest_model,
)
from schematics.types import IntType


class DeleteModelMixin(object):
    """ Resource & responders for deleting a single item """

    def on_delete(self, req, resp, rid):  # pylint: disable=unused-argument
        """ Delete the single item

        Upon a successful deletion an empty bodied 204
        is returned.
        """

        model_class = self.model
        signals.pre_req.send(model_class)
        signals.pre_req_delete.send(model_class)

        model = self.get_object(model_class, rid)
        self.perform_delete(model)

        resp.status = falcon.HTTP_204

        signals.post_req.send(model_class)
        signals.post_req_delete.send(model_class)

    @staticmethod
    def perform_delete(model):
        """ Use the goldman store to update the model """

        goldman.sess.store.delete(model)


class RetrieveModelMixin(object):
    """ Resource & responders for retrieving a single item """

    def on_get(self, req, resp, rid):
        """ Get the model by id & serialize it back """

        model_class = self.model
        signals.pre_req.send(model_class)
        signals.pre_req_get.send(model_class)

        model = self.get_object(model_class, rid)
        props = to_rest_model(model, includes=req.includes)

        resp.last_modified = model.updated
        resp.serialize(props)

        signals.post_req.send(model_class)
        signals.post_req_get.send(model_class)


class UpdateModelMixin(object):
    """ Resource & responders for updating a single item """

    def on_patch(self, req, resp, rid):
        """ Deserialize the payload & update the single item """

        model_class = self.model
        signals.pre_req.send(model_class)
        signals.pre_req_update.send(model_class)

        props = req.deserialize()
        model = self.get_object(model_class, rid)

        from_rest(model, props)
        self.perform_update(model)

        props = to_rest_model(model, includes=req.includes)
        resp.last_modified = model.updated
        resp.serialize(props)

        signals.post_req.send(model_class)
        signals.post_req_update.send(model_class)

    @staticmethod
    def perform_update(model):
        """ Use the goldman store to update the model """

        goldman.sess.store.update(model)


class BaseModelResource(BaseResource):

    @staticmethod
    def validate_rid(model, rid):
        """ Ensure the resource id is proper

        Will raise an `InvalidURL` exception if the rid isn't
        syntactically correct.

        :raises: InvalidURL
        """

        rid_field = getattr(model, model.rid_field)

        if isinstance(rid_field, IntType):
            try:
                int(rid)
            except (TypeError, ValueError):
                raise exceptions.InvalidURL(**{
                    'detail': 'The resource id {} in your request is not '
                              'syntactically correct. Only numeric type '
                              'resource id\'s are allowed'.format(rid)
                })

    def get_object(self, model_class, rid):
        """ Get a model from the store by resource id """

        self.validate_rid(model_class, rid)

        name = model_class.rid_field_name
        model = goldman.sess.store.get(model_class.RTYPE, name, rid)

        if not model:
            raise exceptions.DocumentNotFound
        return model
