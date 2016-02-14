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

from goldman.utils.error_helpers import abort, mod_fail
from schematics.types import IntType


__all__ = ['find', 'from_rest', 'to_rest_model', 'to_rest_models']


def validate_rid(model, rid):
    """ Ensure the resource id is proper """

    rid_field = getattr(model, model.rid_field_name)

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

    rid_field_name = model.rid_field_name
    model = goldman.sess.store.find(model.RTYPE, rid_field_name, rid)

    if not model:
        abort(exceptions.DocumentNotFound)

    return model


def _from_rest_blank(model, props):
    """ Set empty strings to None where allowed

    This is done on fields with `allow_blank=True` which takes
    an incoming empty string & sets it to None so validations
    are skipped. This is useful on fields that aren't required
    with format validations like URLType, EmailType, etc.
    """

    blank = model.get_fields_by_prop('allow_blank', True)

    for field in blank:
        try:
            if props[field] == '':
                props[field] = None
        except KeyError:
            continue


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


def _from_rest_reject_update(model):
    """ Reject any field updates not allowed on POST

    This is done on fields with `reject_update=True`.
    """

    dirty = model.dirty_fields
    fields = model.get_fields_by_prop('reject_update', True)
    reject = []

    for field in fields:
        if field in dirty:
            reject.append(field)

    if reject:
        mod_fail('These fields cannot be updated: %s' % ', '.join(reject))


def from_rest(model, props):
    """ Map the REST data onto the model

    Additionally, perform the following tasks:

        * set all blank strings to None where needed
        * purge all fields not allowed as incoming data
        * purge all unknown fields from the incoming data
        * lowercase certain fields that need it
        * merge new data with existing & validate
            * mutate the existing model
            * abort on validation errors
            * coerce all the values
    """

    req = goldman.sess.req

    _from_rest_blank(model, props)
    _from_rest_hide(model, props)
    _from_rest_ignore(model, props)
    _from_rest_lower(model, props)

    if req.is_posting:
        _from_rest_on_create(model, props)
    elif req.is_patching:
        _from_rest_on_update(model, props)

    model.merge(props, validate=True)

    if req.is_patching:
        _from_rest_reject_update(model)


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


def _to_rest_includes(models, includes):
    """ Fetch the models to be included

    The includes should follow a few basic rules:

        * the include MUST not already be an array member
          of the included array (no dupes)

        * the include MUST not be the same as the primary
          data if the primary data is a single resource
          object (no dupes)

        * the include MUST not be an array member of the
          primary data if the primary data an array of
          resource objects (no dupes)

    Basically, each included array member should be the only
    instance of that resource object in the entire restified
    data.
    """

    included = []
    includes = includes or []

    if not isinstance(models, list):
        models = [models]

    for include in includes:
        for model in models:
            rel = getattr(model, include)

            if hasattr(rel, 'model') and rel.model:
                rel_models = [rel.model]
            elif hasattr(rel, 'models') and rel.models:
                rel_models = rel.models

            for rel_model in rel_models:
                if rel_model in models or rel_model in included:
                    continue
                else:
                    included.append(rel_model)

    for idx, val in enumerate(included):
        included[idx] = _to_rest(val)

    return included


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


def _to_rest(model, includes=None):
    """ Convert the model into a dict for serialization

    Notify schematics of the sparse fields requested while
    also forcing the resource id & resource type fields to always
    be present no matter the request. Additionally, any includes
    are implicitly added as well & automatically loaded.

    Then normalize the includes, hide private fields, & munge
    the relationships into a format the serializers are
    expecting.
    """

    includes = includes or []
    sparse = goldman.sess.req.fields.get(model.rtype, [])

    if sparse:
        sparse += [model.rid_field_name, model.rtype_field]
        sparse += includes

    props = model.to_primitive(
        load_rels=includes,
        sparse_fields=sparse,
    )

    props['rid'] = props.pop(model.rid_field_name)
    props['rtype'] = props.pop(model.rtype_field)

    _to_rest_hide(model, props)
    _to_rest_rels(model, props)

    return props


def to_rest_model(model, includes=None):
    """ Convert the single model into a dict for serialization

    :return: dict
    """

    props = {}
    props['data'] = _to_rest(model, includes=includes)
    props['included'] = _to_rest_includes(model, includes=includes)

    return props


def to_rest_models(models, includes=None):
    """ Convert the models into a dict for serialization

    models should be an array of single model objects that
    will each be serialized.

    :return: dict
    """

    props = {}
    props['data'] = []

    for model in models:
        props['data'].append(_to_rest(model, includes=includes))

    props['included'] = _to_rest_includes(models, includes=includes)

    return props
