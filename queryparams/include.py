"""
    queryparams.include
    ~~~~~~~~~~~~~~~~~~~

    Determine relationship resources to include in the response
    according to one or more criteria.
"""

import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort


def _validate_no_nesting(param, field):
    """ Ensure the include field is not a nested relationship """

    if '.' in field:
        abort(exceptions.InvalidQueryParams(**{
            'detail': '{} is not a supported include value. '
                      'Nested children inclusions are not '
                      'currently supported'.format(param),
            'parameter': 'include',
        }))


def _validate_rels(param, field, rels):
    """ Ensure the include field is a relationship """

    if field not in rels:
        abort(exceptions.InvalidQueryParams(**{
            'detail': 'Invalid include query, {} field '
                      'is not a relationship'.format(param),
            'parameter': 'include',
        }))


def from_req(req, rels):
    """ Determine the included relationships by query parameter

    Return an array of fields to include.

    If the includes don't comply with our basic rules then
    abort immediately on an InvalidQueryParam exception.

    RULES
    ~~~~~

    All includes must match on fields that are relationships
    but Currently our API framework does not support including
    on NESTED relationships.

    :param req:
        Falcon request object
    :param rels:
        Array of string model object relationship field names
    :return:
        Array of string fields
    """

    vals = req.get_param_as_list('include') or []

    for val in vals:
        field = val.lower()

        _validate_no_nesting(val, field)
        _validate_rels(val, field, rels)

    return [val.lower() for val in vals]
