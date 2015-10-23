"""
    queryparams.sort
    ~~~~~~~~~~~~~~~~

    Sort resources according to one or more criteria.
"""

import goldman
import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort


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

        _field = field.lower()
        field = _field.lstrip('-')

        self._field = _field
        self.field = field

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

        return 'Sortable(\'{}\')'.format(self.raw_field)

    def __str__(self):
        """ Display the original sort with descending character """

        return self.raw_field


def _validate_field(param, field, fields):
    """ Ensure the sortable field exists on the model """

    if field not in fields:
        abort(exceptions.InvalidQueryParams(**{
            'detail': 'Invalid sort query, {} field '
                      'not found'.format(param),
            'parameter': 'sort',
        }))


def _validate_no_rels(param, field, rels):
    """ Ensure the sortable field is not on a relationship """

    if field in rels:
        abort(exceptions.InvalidQueryParams(**{
            'detail': '{} is not a supported sortable value. '
                      'Sorting on relationships is not currently '
                      'supported'.format(param),
            'parameter': 'sort',
        }))


def from_req(req, fields, rels):
    """ Determine the sorting preference by query parameter

    Return an array of Sortable objects.

    If the sortables don't comply with our basic rules then
    abort immediately on an InvalidQueryParam exception.

    RULES
    ~~~~~

    Currently our API framework does not support sorting
    on relationships fields.

    :param req:
        Falcon request object
    :param fields:
        Array of string model object field names
    :param rels:
        Array of string model object relationship field names
    :return:
        Array of Sortable objects
    """

    vals = req.get_param_as_list('sort') or [goldman.config.SORT]

    for val in vals:
        field = val.lower().lstrip('-')

        _validate_no_rels(val, field, rels)
        _validate_field(val, field, fields)

    return [Sortable(val) for val in vals]
