"""
    queryparams.filter
    ~~~~~~~~~~~~~~~~~~

    Filter resources according to one or more criteria.

    Requested filters follow the django convention of using
    double underscores '__' to apply operators. The query
    parameter itself follows the JSON API convention for
    filtering:

        jsonapi.org/format/#fetching-filtering
        jsonapi.org/recommendations/#filtering
"""

import goldman
import goldman.exceptions as exceptions
import re

from goldman.utils.error_handlers import abort
from goldman.utils.str_helpers import str_to_bool, str_to_dt


class Filter(object):
    """ Filter parameter object

    An instance of this object can be used to express a
    filter critera for later use by the store or whatever.

    :param field:
        String field name to filter on. Required.
    :param neg:
        Boolean negation flag. Default: False.
    :param oper: str operator expression
        String operator expression. Required.
    :param val:
        Value for expression evaluation & can be any data
        type that is expected by the store. It should already
        have been cast into whatever data type is expected.
    """

    def __init__(self, field, oper, val, neg=False):

        self.field = field
        self.oper = oper
        self.neg = neg
        self.val = val

    def __eq__(self, other):
        """ Compare other Sortable objects or strings """

        try:
            return self.field == other.field and \
                self.oper == other.oper and \
                self.neg == other.neg and \
                self.val == other.val
        except AttributeError:
            return False

    def __repr__(self):

        name = self.__class__.__name__

        return '{}(\'{}\', \'{}\', \'{}\', neg={})'.format(
            name,
            self.field,
            self.oper,
            self.val,
            self.neg,
        )

    def __str__(self):

        return '({}, {}, {}, neg={})'.format(
            self.field,
            self.oper,
            self.val,
            self.neg,
        )


class FilterOr(object):
    """ OR'd filter expression

    The filter expressions will be immediately cast into
    Filter objects if not one already.

    This object will represent the collection of Filter
    objects that should be evaluated as a collection using
    the logical `OR` operator.
    """

    def __init__(self, exprs):

        self.exprs = []

        for expr in exprs:
            if not isinstance(expr, Filter):
                expr = Filter(*expr)

            self.exprs.append(expr)

    def __contains__(self, item):
        """ Leverage the single Filter for comparison logic """

        return item in self.exprs

    def __getitem__(self, index):

        return self.exprs[index]

    def __len__(self):

        return len(self.exprs)

    def __repr__(self):
        """ Display the original sort with descending character """

        name = self.__class__.__name__

        return '{}({})'.format(name, self.exprs)

    def __str__(self):
        """ Display the original sort with descending character """

        return str(self.exprs)


def _parse_param(key):
    """ Parse the query param looking for filters

    Determine the field to filter on & the operator to
    be used when filtering.

    :param key:
        The query parameter to the left of the equal sign
    :return:
        tuple of string field name & string operator
    """

    regex = re.compile(r'filter\[([A-Za-z0-9_.]+)\]')
    match = regex.match(key)

    if match:
        field_and_opers = match.groups()[0].split('__')

        if len(field_and_opers) == 1:
            field, oper = field_and_opers[0], 'eq'

        elif len(field_and_opers) == 2:
            field, oper = field_and_opers

        else:
            abort(exceptions.InvalidQueryParams(**{
                'detail': 'Multiple filter operators are not allowed '
                          'in a single filter expression. Please '
                          'modify {} & retry'.format(key),
                'parameter': 'filter',
            }))

        return field, oper


def from_req(req, fields):  # pylint: disable=too-many-branches
    """ Determine the filters to apply by query parameter

    Return an array of Filter objects.

    Like django & other frameworks the key & the operator are
    separated by a double underscore. Example filters:

        filter[name]=John
        filter[price__gt]=199
        filter[boss__exists]=true
        filter[loc__geo_near]=40,90,1

    :param req:
        Falcon request object
    :param fields:
        Array of string model object field names
    :return:
        Array of Filter objects
    """

    vals = []

    for key, val in req.params.items():
        detail = None

        try:
            field, oper = _parse_param(key)
        except (TypeError, ValueError):
            continue

        if field.count('.') > 1:
            detail = 'Filtering on nested relationships is not ' \
                     'currently supported. Please remove {} from ' \
                     'your request & retry'.format(key)

        elif field not in fields:
            detail = 'Invalid filter query of {}, {} field not ' \
                     'found'.format(key, val)

        elif oper not in goldman.config.QUERY_FILTERS:
            detail = 'The query filter {} is not a supported ' \
                     'operator. Please change {} & retry your ' \
                     'request'.format(oper, key)

        elif oper in goldman.config.BOOL_FILTERS:
            try:
                val = str_to_bool(val)
            except ValueError:
                detail = 'The query filter {} requires a boolean ' \
                         'for evaluation. Please modify your ' \
                         'request & retry'.format(key)

        elif oper in goldman.config.DATE_FILTERS:
            try:
                val = str_to_dt(val)
            except ValueError:
                detail = 'The query filter {} supports only an ' \
                         'epoch or ISO 8601 timestamp. Please ' \
                         'modify your request & retry'.format(key)

        elif oper in goldman.config.GEO_FILTERS:
            try:
                if not isinstance(val, list) or len(val) <= 2:
                    raise ValueError
                else:
                    val = [float(i) for i in val]
            except ValueError:
                detail = 'The query filter {} requires a list ' \
                         'of floats for geo evaluation. Please ' \
                         'modify your request & retry'.format(key)

        elif oper in goldman.config.NUM_FILTERS:
            try:
                val = int(val)
            except TypeError:
                detail = 'Multiple query filters for {} is ' \
                         'unsupported. Please modify your ' \
                         'request & retry'.format(key)
            except ValueError:
                detail = 'The query filter {} requires a number ' \
                         'for evaluation. Please modify your ' \
                         'request & retry'.format(key)

        if detail:
            abort(exceptions.InvalidQueryParams(**{
                'detail': detail,
                'parameter': 'filter',
            }))

        vals.append(Filter(field, oper, val))

    return vals
