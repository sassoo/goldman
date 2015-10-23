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

from goldman.utils.error_handlers import abort


class SparseField(object):
    """ Sparse fields object

    An instance of this object can be used to express a
    sparse fields preference where a particular models
    fields are limited to those requested.

    It's a nice way of limiting the response payload &
    database queries to only the fields required.

    It's done by requesting the sparse fields of a particular
    model type.

    :param rtype:
        String resource type name for pruning fields. Required.
    :param fields:
        Iterable of whitelisted string field names
    """

    def __init__(self, rtype, fields):

        fields = [field.lower() for field in fields]

        self.rtype = rtype
        self.fields = tuple(sorted(fields))

    def __eq__(self, other):

        try:
            return self.rtype == other.rtype and \
                self.fields == other.fields
        except AttributeError:
            return False

    def __repr__(self):

        return 'SparseField(\'{}\', {})'.format(self.rtype, self.fields)

    def __str__(self):

        return '{}, {}'.format(self.rtype, self.fields)


def _parse_param(key, val):
    """ Parse the query param looking for sparse fields params

    Ensure the val or what will become the sparse `fields`
    is always an array. If the query param is not a sparse
    fields query param the return None.

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


def _validate_fields(param, param_fields, model_fields):
    """ Ensure the fields exist on the model """

    for field in param_fields:
        if field not in model_fields:
            abort(exceptions.InvalidQueryParams(**{
                'detail': 'Invalid sparse fields query {}, '
                          'field {} not found'.format(param, field),
                'parameter': 'sort',
            }))


def _validate_rtype(param, param_rtype, model_rtype):
    """ Ensure the params query rtype matches the models """

    if param_rtype != model_rtype:
        allowed = 'fields[{}]'.format(model_rtype)

        abort(exceptions.InvalidQueryParams(**{
            'detail': 'Invalid sparse fields query {}, only '
                      '{} is allowed'.format(param, allowed),
            'parameter': 'fields',
        }))


def from_req(req, rtype, fields):
    """ Determine the sparse fields to limit the response to

    Return an array of SparseField objects.

    If the sparse fields don't comply with our basic rules
    then abort immediately on an InvalidQueryParam exception.

    RULES
    ~~~~~

    Currently our API framework does not support sparse
    fields on relationships.

    :param req:
        Falcon request object
    :param fields:
        Array of string model object field names
    :param rtype:
        String model object resource type
    :return:
        Array of SparseField objects
    """

    vals = []

    for key, val in req.params.items():
        try:
            param_rtype, param_fields = _parse_param(key, val)
        except (TypeError, ValueError):
            continue

        _validate_rtype(key, param_rtype, rtype)
        _validate_fields(key, param_fields, fields)

        vals.append(SparseField(rtype, param_fields))

    return vals
