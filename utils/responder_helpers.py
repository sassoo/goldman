"""
    utils.responder_helpers
    ~~~~~~~~~~~~~~~~~~~~~~~

    Common helpers for our resource responders

    These can be used on any resource responders that need
    common funtionality when interacting with models in a
    RESTFUL like fashion.

    Things like URL validations, some store method wrapping,
    routine over-the-wire (de)serialization helpers, etc.
"""

import goldman
import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort
from schematics.types import IntType


__all__ = ['find', 'from_rest', 'to_rest']


def validate_rid(model, rid):
    """ Ensure the resource id is proper """

    rid_field = getattr(model, model.rid_field)

    if isinstance(rid_field, IntType):
        try:
            int(rid)
        except (TypeError, ValueError):
            abort(exceptions.InvalidURL(**{
                'detail': 'The resource id {} in your request is not '
                          'syntactically correct. Only numeric type '
                          'resource id\'s are allowed'.format(rid)
            }))


def find(model, rid):
    """ Find a model from the store by resource id """

    validate_rid(model, rid)

    rid_field = model.rid_field
    model = goldman.sess.store.find(model.RTYPE, rid_field, rid)

    if not model:
        abort(exceptions.DocumentNotFound)

    return model


def _from_rest_hide(model, props):
    """ Purge fields not allowed during a REST deserialization

    This is done on fields with `from_rest=False`.
    """

    hide = model.get_fields_by_prop('from_rest', False)

    for field in hide:
        try:
            del props[field]
        except KeyError:
            continue


def _from_rest_ignore(model, props):
    """ Purge fields that are completely unknown """

    fields = model.all_fields

    for prop in props.keys():
        if prop not in fields:
            del props[prop]


def _from_rest_lower(model, props):
    """ Lowercase fields requesting it during a REST deserialization """

    for field in model.to_lower:
        try:
            props[field] = props[field].lower()
        except (AttributeError, KeyError):
            continue


def _from_rest_on_create(model, props):
    """ Assign the default values when creating a model

    This is done on fields with `on_create=<value>`.
    """

    fields = model.get_fields_with_prop('on_create')

    for field in fields:
        props[field[0]] = field[1]


def _from_rest_on_update(model, props):
    """ Assign the default values when updating a model

    This is done on fields with `on_update=<value>`.
    """

    fields = model.get_fields_with_prop('on_update')

    for field in fields:
        props[field[0]] = field[1]


def from_rest(model, props):
    """ Map the REST data onto the model

    Additionally, perform the following tasks:

        * purge all fields not allowed as incoming data
        * purge all unknown fields from the incoming data
        * lowercase certain fields that need it
        * merge new data with existing & validate
            * mutate the existing model
            * abort on validation errors
            * coerce all the values
    """

    req = goldman.sess.req

    _from_rest_hide(model, props)
    _from_rest_ignore(model, props)
    _from_rest_lower(model, props)

    if req.is_posting:
        _from_rest_on_create(model, props)
    elif req.is_patching:
        _from_rest_on_update(model, props)

    model.merge(props, validate=True)


def _to_rest_hide(model, props):
    """ Purge fields not allowed during a REST serialization

    This is done on fields with `to_rest=False`.
    """

    hide = model.get_fields_by_prop('to_rest', False)

    for field in hide:
        try:
            del props[field]
        except KeyError:
            continue


def _to_rest_include(model, props, includes):
    """ Fetch the models to be included """

    includes = includes or []
    props['include'] = []

    for include in includes:
        rel = getattr(model, include)

        if hasattr(rel, 'model') and rel.model:
            props['include'].append(to_rest(rel.model))
        elif hasattr(rel, 'models') and rel.models:
            props['include'] += [to_rest(m) for m in rel.models]


def _to_rest_rels(model, props):
    """ Move the relationships to appropriate location in the props

    All to_ones should be in a to_one key while all to_manys
    should be in a to_many key.
    """

    props['to_many'] = {}
    props['to_one'] = {}

    for key in model.to_one:
        try:
            props['to_one'][key] = props.pop(key)
        except KeyError:
            continue

    for key in model.to_many:
        try:
            props['to_many'][key] = props.pop(key)
        except KeyError:
            continue


def to_rest(model, includes=None):
    """ Convert the model into a dict for serialization

    Notify schematics of the sparse fields requested while
    also forcing the resource id & resource type fields to always
    be present no matter the request. Additionally, any includes
    are implicitely added as well.

    The load the includes, hide private fields, & munge the
    relationships into a format the serializers are expecting.
    """

    sparse = goldman.sess.req.fields.get(model.rtype, [])

    if sparse:
        sparse += [model.rid_field, model.rtype_field]
        sparse += includes

    props = model.to_primitive(
        load_rels=includes,
        sparse_fields=sparse,
    )
    props['rid'] = props.pop(model.rid_field)
    props['rtype'] = props.pop(model.rtype_field)

    _to_rest_include(model, props, includes)
    _to_rest_hide(model, props)
    _to_rest_rels(model, props)

    return props
