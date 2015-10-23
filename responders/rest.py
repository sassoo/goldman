"""
    responders.rest
    ~~~~~~~~~~~~~~~

    Model responder mixin.

    This can be used on any resources that need common
    funtionality when interacting with models in a RESTFUL
    like fashion.

    Things like JSON API compatible query parameter processing
    URL validations, some store method wrapping, etc.
"""

import goldman.exceptions as exceptions
import goldman.queryparams.fields as fields
import goldman.queryparams.filter as filtr
import goldman.queryparams.include as include
import goldman.queryparams.page as page
import goldman.queryparams.sort as sort

from goldman.utils.error_handlers import abort
from goldman.utils.str_helpers import str_to_uuid
from schematics.exceptions import ModelValidationError
from schematics.types import EmailType


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
    """ Lowercase fields requesting it during a REST deserialization

    This is done on fields with `lower=True`.
    """

    email = model.get_fields_by_class(EmailType)
    lower = model.get_fields_by_prop('lower', True) + email

    for field in lower:
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


class Responder(object):
    """ Model responder mixin """

    def __init__(self, req, model):
        """ Initialize all the REST supported query params

        The model that is passed in should be a class object
        of the model & not an instance so it shouldn't be used
        beyond intialization.
        """

        self._login = req.login
        self._model = model

        model_fields = model.all_fields
        model_rels = model.relationships
        model_rtype = model.rtype

        self.fields = fields.from_req(req, model_rtype, model_fields)
        self.filters = filtr.from_req(req, model_fields)
        self.includes = include.from_req(req, model_rels)
        self.pages = page.from_req(req)
        self.sorts = sort.from_req(req, model_fields, model_rels)

    @staticmethod
    def validate_uuid(uuid):
        """ Ensure the UUID is syntactically proper """

        try:
            str_to_uuid(uuid)
        except ValueError:
            abort(exceptions.InvalidURL(**{
                'detail': 'The resource requested in your URL '
                          'is not a valid UUID. Please fix it.',
                'links': 'en.wikipedia.org/wiki/Universally_unique_identifier',
            }))

    def find(self, store, uuid):
        """ Find a model from the store by uuid """

        self.validate_uuid(uuid)

        model = store.find(self._model, uuid)

        if not model:
            abort(exceptions.DocumentNotFound)
        elif not model.acl_find(self._login):
            abort(exceptions.ReadDenied)

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

            * purge all fields not allowed as outgoing data

        :return: dict
        """

        props = model.to_primitive()
        props = to_rest_hide(model, props)

        return props
