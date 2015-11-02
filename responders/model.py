"""
    responders.model
    ~~~~~~~~~~~~~~~~

    Model responder mixin.

    This can be used on any resources that need common
    funtionality when interacting with models in a RESTFUL
    like fashion.

    Things like JSON API compatible query parameter processing
    URL validations, some store method wrapping, etc.
"""

import goldman
import goldman.exceptions as exceptions
import goldman.queryparams.fields as qp_fields
import goldman.queryparams.filter as qp_filter
import goldman.queryparams.include as qp_include
import goldman.queryparams.page as qp_page
import goldman.queryparams.sort as qp_sort

from goldman.utils.error_handlers import abort
from schematics.exceptions import ModelValidationError


def from_rest_hide(model, props):
    """ Purge fields not allowed during a REST deserialization

    This is done on fields with `from_rest=False`.
    """

    hide = model.get_fields_by_prop('from_rest', False)

    for field in hide:
        try:
            del props[field]
        except KeyError:
            continue

    return props


def from_rest_ignore(model, props):
    """ Purge fields that are completely unknown """

    model_fields = model.all_fields

    for prop in props.keys():
        if prop not in model_fields:
            del props[prop]

    return props


def from_rest_lower(model, props):
    """ Lowercase fields requesting it during a REST deserialization """

    for field in model.to_lowers:
        try:
            props[field] = props[field].lower()
        except (AttributeError, KeyError):
            continue

    return props


def to_rest_hide(model, props):
    """ Purge fields not allowed during a REST serialization

    This is done on fields with `to_rest=False`.
    """

    hide = model.get_fields_by_prop('to_rest', False)

    for field in hide:
        try:
            del props[field]
        except KeyError:
            continue

    return props


# pylint: disable=too-many-instance-attributes
class Responder(object):
    """ Model responder mixin """

    def __init__(self, resource, req, resp):  # pylint: disable=unused-argument
        """ Initialize all the model responder

        This responder should be passed in the same args as a
        native falcon resources responder. The responder will
        expect to find the following attributes on the resource:

        `resource.model`:
            model class (not instance)
        """

        model = resource.model
        self._model = model
        self._req = req

        # declare these here instead of in each query
        # param since they are a bit expensive.
        fields = model.all_fields
        rels = model.relationships

        self.fields = qp_fields.from_req(req)
        self.filters = qp_filter.from_req(req, fields)
        self.includes = qp_include.from_req(req, rels)
        self.pages = qp_page.from_req(req)
        self.sorts = qp_sort.from_req(req, fields, rels)

    def find(self, rtype, rid):
        """ Find a model from the store by resource id """

        rid_field = self._model.rid_field
        model = goldman.sess.store.find(rtype, rid_field, rid)

        if not model:
            abort(exceptions.DocumentNotFound)

        return model

    def from_rest(self, model, props):
        """ Map the REST data onto self

        Additionally, perform the following tasks:

            * purge all fields not allowed as incoming data
            * purge all unknown fields from the incoming data
            * lowercase certain fields that need it
            * merge new data with existing & validate
                * mutate the existing model (self)
                * abort on validation errors
                * coerce all the values
        """

        props = from_rest_hide(model, props)
        props = from_rest_ignore(model, props)
        props = from_rest_lower(model, props)

        # schematics will not auto cast these so after
        # validating we then have to cast them
        for key, val in props.items():
            setattr(model, key, val)

        try:
            model.validate()
        except ModelValidationError as errors:
            abort(model.to_exceptions(errors.messages))

        for key, val in model.to_native().items():
            setattr(model, key, val)

    def to_rest(self, model):
        """ Convert the model into a dict for serialization

        Additionally, perform the following tasks:

            * process teh sparse fields if provided
            * purge all fields never allowed as outgoing data
            * rename the resource id field to a key named `rid`
            * move the to_one relationships to a to_ones key

        :return: dict
        """

        fields = []

        if self._req.is_getting and self.fields:
            fields = [fields for f in self.fields if f.rtype == model.rtype]
            fields += ['rid', 'rtype']

        props = model.to_primitive(sparse_fields=fields)
        props = to_rest_hide(model, props)

        props['rid'] = props.pop(model.rid_field)
        # props['to_manys'] = {key: props.pop(key) for key in model.to_manys}
        props['to_ones'] = {key: props.pop(key) for key in model.to_ones}

        return props
