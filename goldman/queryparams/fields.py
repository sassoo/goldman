"""
    queryparams.fields
    ~~~~~~~~~~~~~~~~~~

    Limit the response to the requested sparse fields.

    The query parameter itself follows the JSON API convention
    for sparse fields:

        jsonapi.org/format/#fetching-sparse-fieldsets
        jsonapi.org/examples/#sparse-fieldsets
"""

import goldman.exceptions as exceptions
import re

from goldman.utils.error_helpers import abort
from goldman.utils.model_helpers import rtype_to_model


def _parse_param(key, val):
    """ Parse the query param looking for sparse fields params

    Ensure the val or what will become the sparse `fields`
    is always an array. If the query param is not a sparse
    fields query param then return None.

    :param key:
        The query parameter to the left of the equal sign
    :param val:
        The query parameter to the right of the equal sign
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
        model = rtype_to_model(rtype)
        model_fields = model.all_fields
    except AttributeError:
        abort(exceptions.InvalidQueryParams(**{
            'detail': 'The sparse field query parameter you provided '
                      'with a field type of {} is unknown'.format(rtype),
            'parameter': 'fields',
        }))

    for field in fields:
        if field not in model_fields:
            abort(exceptions.InvalidQueryParams(**{
                'detail': 'The sparse field type of {} does not have '
                          'a field name of {}'.format(rtype, field),
                'parameter': 'fields',
            }))


def _validate_req(req):
    """ Ensure the request is a GET request

    Modification type requests could have other fields modified
    by the backend persistance layer through stored procedures or
    triggers & would need to be reported back to the client.

    In this scenario, it's best to only support sparse fields on
    requests that don't have side-effects.
    """

    if not req.is_getting:
        abort(exceptions.InvalidQueryParams(**{
            'detail': 'Sparse field query parameters are only '
                      'supported with GET requests',
            'parameter': 'fields',
        }))


def init(req, model):  # pylint: disable=unused-argument
    """ Determine the sparse fields to limit the response to

    Return a dict where the key is the resource type (rtype) &
    the value is an array of string fields names to whitelist
    against.

    :param req:
        Falcon request object
    :return:
        dict
    """

    params = {}

    for key, val in req.params.items():
        try:
            rtype, fields = _parse_param(key, val)
            params[rtype] = [field for field in fields]
        except TypeError:
            continue

    if params:
        _validate_req(req)

    for rtype, fields in params.items():
        _validate_param(rtype, fields)

    return params
