"""
    queryparams.include
    ~~~~~~~~~~~~~~~~~~~

    Determine relationship resources to include in the response
    according to one or more criteria. Documented here:

        jsonapi.org/format/#fetching-includes
"""

import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort


def _validate_no_nesting(param):
    """ Ensure the include field is not a nested relationship """

    if '.' in param:
        abort(exceptions.InvalidQueryParams(**{
            'detail': '{} is not a supported include value. '
                      'Nested children inclusions are not '
                      'currently supported'.format(param),
            'parameter': 'include',
        }))


def _validate_rels(param, rels):
    """ Ensure the include field is a relationship """

    if param not in rels:
        abort(exceptions.InvalidQueryParams(**{
            'detail': 'Invalid include query, {} field '
                      'is not a relationship'.format(param),
            'parameter': 'include',
        }))


def from_req(req):
    """ Return an array of fields to include. """

    vals = req.get_param_as_list('include') or []

    return [val.lower() for val in vals]


def validate(req, model):
    """ include query param model based validations """

    rels = model.relationships

    for param in req.includes:
        _validate_no_nesting(param)
        _validate_rels(param, rels)
