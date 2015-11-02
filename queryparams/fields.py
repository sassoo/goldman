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

        name = self.__class__.__name__

        return '{}(\'{}\', {})'.format(name, self.rtype, self.fields)

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


def from_req(req):
    """ Determine the sparse fields to limit the response to

    Return an array of SparseField objects.

    :param req:
        Falcon request object
    :return:
        Array of SparseField objects
    """

    vals = []

    for key, val in req.params.items():
        try:
            param_rtype, param_fields = _parse_param(key, val)
        except (TypeError, ValueError):
            continue

        vals.append(SparseField(param_rtype, param_fields))

    return vals
