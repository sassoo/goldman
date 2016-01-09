"""
    queryparams.fields
    ~~~~~~~~~~~~~~~~~~

    Limit the response to the requested sparse fields.

    The query parameter itself follows the JSON API convention
    for sparse fields:

        jsonapi.org/format/#fetching-sparse-fieldsets
        jsonapi.org/examples/#sparse-fieldsets
"""

import re

from goldman.exceptions import InvalidQueryParams
from goldman.utils.model_helpers import rtype_to_model


def _parse_param(key, val):
    """ Parse the query param looking for sparse fields params

    Ensure the `val` or what will become the sparse fields
    is always an array. If the query param is not a sparse
    fields query param then return None.

    :param key:
        the query parameter key in the request (left of =)
    :param val:
        the query parameter val in the request (right of =)
    :return:
        tuple of resource type to implement the sparse
        fields on & a array of the fields.
    """

    regex = re.compile(r'fields\[([A-Za-z]+)\]')
    match = regex.match(key)

    if match:
        if not isinstance(val, list):
            val = val.split(',')

        fields = [field.lower() for field in val]
        rtype = match.groups()[0].lower()

        return rtype, fields


def _validate_param(rtype, fields):
    """ Ensure the sparse fields exists on the models """

    try:
        # raises ValueError if not found
        model = rtype_to_model(rtype)
        model_fields = model.all_fields
    except ValueError:
        raise InvalidQueryParams(**{
            'detail': 'The sparse field query parameter provided with '
                      'a field type of "%s" is unknown' % rtype,
            'parameter': 'fields',
        })

    for field in fields:
        if field not in model_fields:
            raise InvalidQueryParams(**{
                'detail': 'The sparse field type of "%s" does not have '
                          'a field name of "%s"' % (rtype, field),
                'parameter': 'fields',
            })


def _validate_req(req):
    """ Ensure the request is a GET request

    Modification type requests could have other fields modified
    by the backend persistance layer through stored procedures or
    triggers & would need to be reported back to the client.

    In this scenario, it's best to only support sparse fields on
    requests that don't have side-effects.
    """

    if not req.is_getting:
        raise InvalidQueryParams(**{
            'detail': 'Sparse field query parameters are only '
                      'supported with GET requests',
            'parameter': 'fields',
        })


def init(req, model):  # pylint: disable=unused-argument
    """ Determine the sparse fields to limit the response to

    Return a dict where the key is the resource type (rtype) &
    the value is an array of string fields names to whitelist
    against.

    :return:
        dict
    """

    params = {}

    for key, val in req.params.items():
        try:
            rtype, fields = _parse_param(key, val)
            params[rtype] = fields
        except TypeError:
            continue

    if params:
        _validate_req(req)
        for rtype, fields in params.items():
            _validate_param(rtype, fields)
    return params
