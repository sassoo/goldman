"""
    queryparams.include
    ~~~~~~~~~~~~~~~~~~~

    Determine relationship resources to include in the response
    according to one or more criteria. Documented here:

        jsonapi.org/format/#fetching-includes
"""

from goldman.exceptions import InvalidQueryParams


def _validate_no_nesting(param):
    """ Ensure the include field is not a nested relationship """

    if '.' in param:
        raise InvalidQueryParams(**{
            'detail': 'The include query param of the "%s" field '
                      'is not supported. Nested relationship '
                      'inclusions are not currently supported' % param,
            'parameter': 'include',
        })


def _validate_rels(param, rels):
    """ Ensure the include field is a relationship """

    if param not in rels:
        raise InvalidQueryParams(**{
            'detail': 'The include query param of the "%s" field '
                      'is not possible. It does not represent a '
                      'relationship field & on the primary resource '
                      '& is not eligible for inclusion as a compound '
                      'document.' % param,
            'parameter': 'include',
        })


def init(req, model):
    """ Return an array of fields to include. """

    rels = model.relationships
    params = req.get_param_as_list('include') or []
    params = [param.lower() for param in params]

    for param in params:
        _validate_no_nesting(param)
        _validate_rels(param, rels)

    return params
