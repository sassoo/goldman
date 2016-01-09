"""
    queryparams.sort
    ~~~~~~~~~~~~~~~~

    Sort resources according to one or more criteria.

    The query parameter itself follow the JSON API convention
    for sorting fields:

        jsonapi.org/format/#fetching-sorting
"""

import goldman

from goldman.exceptions import InvalidQueryParams


LINK = 'jsonapi.org/format/#fetching-sorting'
PARAM = 'sort'


class Sortable(object):
    """ Sortable object

    An instance of this object can be used to express a
    sorting critera for later use by the store or whatever.

    If the sorting field name begins with a '-' then it will sort
    in descending order, otherwise ascending.

    :param field:
        String field name to sort on. Required.
    """

    def __init__(self, field):
        """ Preserve the original field for easy compares & output """

        self.field = field.lstrip('-')
        self.raw_field = field

    @property
    def asc(self):
        """ Boolean of ascending sort preference """

        return not self.raw_field.startswith('-')

    @property
    def desc(self):
        """ Boolean of descending sort preference """

        return self.raw_field.startswith('-')

    def __eq__(self, other):
        """ Compare other Sortable objects """

        try:
            return self.raw_field == other.raw_field
        except AttributeError:
            return False

    def __repr__(self):
        """ Display the original sort with descending character """

        name = self.__class__.__name__

        return '%s(\'%s\')' % (name, self.raw_field)

    def __str__(self):
        """ Display the original sort with descending character """

        return self.raw_field


def _validate_field(param, fields):
    """ Ensure the sortable field exists on the model """

    if param.field not in fields:
        raise InvalidQueryParams(**{
            'detail': 'The sort query param value of "%s" is '
                      'invalid. That field does not exist on the '
                      'resource being requested.' % param.raw_field,
            'links': LINK,
            'parameter': PARAM,
        })


def _validate_no_rels(param, rels):
    """ Ensure the sortable field is not on a relationship """

    if param.field in rels:
        raise InvalidQueryParams(**{
            'detail': 'The sort query param value of "%s" is not '
                      'supported. Sorting on relationships is not '
                      'currently supported' % param.raw_field,
            'links': LINK,
            'parameter': PARAM,
        })


def init(req, model):
    """ Determine the sorting preference by query parameter

    Return an array of Sortable objects.
    """

    rels = model.relationships
    fields = model.all_fields

    params = req.get_param_as_list('sort') or [goldman.config.SORT]
    params = [Sortable(param.lower()) for param in params]

    for param in params:
        _validate_no_rels(param, rels)
        _validate_field(param, fields)

    return params
