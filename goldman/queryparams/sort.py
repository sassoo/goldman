"""
    queryparams.sort
    ~~~~~~~~~~~~~~~~

    Sort resources according to one or more criteria.
"""

import goldman
import goldman.exceptions as exceptions

from goldman.utils.error_helpers import abort


class Sortable(object):
    """ Filter object

    An instance of this object can be used to express a
    sorting critera for later use by the store or whatever.

    If the sorting field name begins with a '-' then it will sort
    in descending order, otherwise ascending.

    :param field:
        String field name to sort on. Required.
    """

    def __init__(self, field):
        """ Preserve the original field for easy compares & output """

        self._field = field.lower()
        self.field = self._field.lstrip('-')

    @property
    def asc(self):
        """ Boolean of ascending sort preference """

        return not self.raw_field.startswith('-')

    @property
    def desc(self):
        """ Boolean of descending sort preference """

        return self.raw_field.startswith('-')

    @property
    def raw_field(self):
        """ Return the original field """

        return self._field

    def __eq__(self, other):
        """ Compare other Sortable objects or strings """

        if isinstance(other, Sortable):
            return self.field == other.field

        try:
            return self.raw_field == other.lower()
        except AttributeError:
            return False

    def __repr__(self):
        """ Display the original sort with descending character """

        name = self.__class__.__name__

        return '{}(\'{}\')'.format(name, self.raw_field)

    def __str__(self):
        """ Display the original sort with descending character """

        return self.raw_field


def _validate_field(param, fields):
    """ Ensure the sortable field exists on the model """

    if param.field not in fields:
        abort(exceptions.InvalidQueryParams(**{
            'detail': 'Invalid sort query, {} field '
                      'not found'.format(param.raw_field),
            'parameter': 'sort',
        }))


def _validate_no_rels(param, rels):
    """ Ensure the sortable field is not on a relationship """

    if param.field in rels:
        abort(exceptions.InvalidQueryParams(**{
            'detail': '{} is not a supported sortable value. '
                      'Sorting on relationships is not currently '
                      'supported'.format(param.raw_field),
            'parameter': 'sort',
        }))


def init(req, model):
    """ Determine the sorting preference by query parameter

    Return an array of Sortable objects.
    """

    rels = model.relationships
    fields = model.all_fields

    params = req.get_param_as_list('sort') or [goldman.config.SORT]
    params = [Sortable(param) for param in params]

    for param in params:
        _validate_no_rels(param, rels)
        _validate_field(param, fields)

    return params
