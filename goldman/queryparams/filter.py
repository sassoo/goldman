"""
    queryparams.filter
    ~~~~~~~~~~~~~~~~~~

    Filter resources according to one or more criteria.

    Like django & other frameworks the key & the operator are
    separated by a double underscore. Example filters:

        filter[name]=John
        filter[price__gt]=199
        filter[boss__exists]=true
        filter[loc__geo_near]=40,90,1


    The query parameter itself follows the JSON API convention
    for filtering:

        jsonapi.org/format/#fetching-filtering
        jsonapi.org/recommendations/#filtering
"""

import goldman
import re

from goldman.exceptions import InvalidQueryParams
from goldman.utils.str_helpers import str_to_bool, str_to_dt


LINK = 'jsonapi.org/format/#fetching-filtering'
PARAM = 'filter'


class Filter(object):
    """ Filter parameter object

    An instance of this object can be used to express a
    filter critera for later use by the store or whatever.

    :param field:
        string field name to filter on
    :param oper:
        string operator expression
    :param val:
        Value for expression evaluation & can be any data
        type that is expected by the store. It should already
        have been cast into whatever data type is expected.
    """

    def __init__(self, field, oper, val):

        self.field = field
        self.oper = oper
        self.val = val

    def __eq__(self, other):
        """ Compare other Filter objects """

        try:
            return self.field == other.field and \
                self.oper == other.oper and \
                self.val == other.val
        except AttributeError:
            return False

    def __repr__(self):

        name = self.__class__.__name__
        return '%s(\'%s\', \'%s\', \'%s\')' % (name, self.field, self.oper,
                                               self.val)

    def __str__(self):

        return 'filter[%s__%s]=%s' % (self.field, self.oper, self.val)


class FilterOr(object):
    """ OR'd filter expression

    This object will represent the collection of Filter
    objects that should be evaluated as a collection using
    the logical `OR` operator.
    """

    def __init__(self, filters):

        self.filters = filters

    def __contains__(self, item):
        """ Leverage the Filter __eq__ for comparison logic """

        return item in self.filters

    def __getitem__(self, index):

        return self.filters[index]

    def __len__(self):

        return len(self.filters)

    def __repr__(self):

        name = self.__class__.__name__
        return '%s(%s)' % (name, self.filters)


class FilterRel(Filter):
    """ Relationship filter expression

    This simply sub-classes the Filter object & adds some
    additional helper attributes which can later be used to
    generate queries.

    An example filter query of:
        filter[creator.username]=john

    would have the following `FilterRel` attribute values:

        local_field = creator
        foreign_filter = username
        foreign_field = rid
        foreign_rtype = logins

    foreign_field & foreign_rtype typically represent the
    same named properties on our goldman relationship types.
    """

    def __init__(self, foreign_field, foreign_filter, foreign_rtype,
                 local_field, *args, **kwargs):

        super(FilterRel, self).__init__(*args, **kwargs)

        self.foreign_filter = foreign_filter
        self.foreign_field = foreign_field
        self.foreign_rtype = foreign_rtype
        self.local_field = local_field


def _parse_param(key):
    """ Parse the query param looking for filters

    Determine the field to filter on & the operator to
    be used when filtering.

    :param key:
        The query parameter to the left of the equal sign
    :return:
        tuple of string field name & string operator
    """

    regex = re.compile(r'filter\[([A-Za-z0-9_./]+)\]')
    match = regex.match(key)

    if match:
        field_and_oper = match.groups()[0].split('__')

        if len(field_and_oper) == 1:
            return field_and_oper[0], 'eq'
        elif len(field_and_oper) == 2:
            return tuple(field_and_oper)
        else:
            raise InvalidQueryParams(**{
                'detail': 'The filter query param of "%s" is not '
                          'supported. Multiple filter operators are '
                          'not allowed in a single expression.' % key,
                'links': LINK,
                'parameter': PARAM,
            })


def _validate_field(param, fields):
    """ Ensure the field exists on the model """

    if '/' not in param.field and param.field not in fields:
        raise InvalidQueryParams(**{
            'detail': 'The filter query param of "%s" is not possible. The '
                      'resource requested does not have a "%s" field. Please '
                      'modify your request & retry.' % (param, param.field),
            'links': LINK,
            'parameter': PARAM,
        })


def _validate_rel(param, rels):
    """ Validate relationship based filters

    We don't support nested filters currently.

    FIX: Ensure the relationship filter field exists on the
         relationships model!
    """

    if param.field.count('/') > 1:
        raise InvalidQueryParams(**{
            'detail': 'The filter query param of "%s" is attempting to '
                      'filter on a nested relationship which is not '
                      'currently supported.' % param,
            'links': LINK,
            'parameter': PARAM,
        })
    elif '/' in param.field:
        model_field = param.field.split('/')[0]

        if model_field not in rels:
            raise InvalidQueryParams(**{
                'detail': 'The filter query param of "%s" is attempting to '
                          'filter on a relationship but the "%s" field is '
                          'NOT a relationship field.' % (param, model_field),
                'links': LINK,
                'parameter': PARAM,
            })


def _validate_param(param):  # pylint: disable=too-many-branches
    """ Ensure the filter cast properly according to the operator """

    detail = None

    if param.oper not in goldman.config.QUERY_FILTERS:
        detail = 'The query filter {} is not a supported ' \
                 'operator. Please change {} & retry your ' \
                 'request'.format(param.oper, param)

    elif param.oper in goldman.config.GEO_FILTERS:
        try:
            if not isinstance(param.val, list) or len(param.val) <= 2:
                raise ValueError
            else:
                param.val = [float(i) for i in param.val]
        except ValueError:
            detail = 'The query filter {} requires a list ' \
                     'of floats for geo evaluation. Please ' \
                     'modify your request & retry'.format(param)

    elif param.oper in goldman.config.ENUM_FILTERS:
        if not isinstance(param.val, list):
            param.val = [param.val]

        param.val = tuple(param.val)

    elif isinstance(param.val, list):
        detail = 'The query filter {} should not be specified more ' \
                 'than once or have multiple values. Please modify ' \
                 'your request & retry'.format(param)

    elif param.oper in goldman.config.BOOL_FILTERS:
        try:
            param.val = str_to_bool(param.val)
        except ValueError:
            detail = 'The query filter {} requires a boolean ' \
                     'for evaluation. Please modify your ' \
                     'request & retry'.format(param)

    elif param.oper in goldman.config.DATE_FILTERS:
        try:
            param.val = str_to_dt(param.val)
        except ValueError:
            detail = 'The query filter {} supports only an ' \
                     'epoch or ISO 8601 timestamp. Please ' \
                     'modify your request & retry'.format(param)

    elif param.oper in goldman.config.NUM_FILTERS:
        try:
            param.val = int(param.val)
        except ValueError:
            detail = 'The query filter {} requires a number ' \
                     'for evaluation. Please modify your ' \
                     'request & retry'.format(param)

    if detail:
        raise InvalidQueryParams(**{
            'detail': detail,
            'links': LINK,
            'parameter': PARAM,
        })


def init(req, model):
    """ Return an array of Filter objects. """

    fields = model.all_fields
    rels = model.relationships
    params = []

    for key, val in req.params.items():
        try:
            field, oper = _parse_param(key)
        except (TypeError, ValueError):
            continue

        try:
            local_field, foreign_filter = field.split('/')
            field_type = getattr(model, local_field)

            foreign_field = field_type.field
            foreign_rtype = field_type.rtype

            if hasattr(field_type, 'local_field'):
                local_field = field_type.local_field

            param = FilterRel(foreign_field, foreign_filter, foreign_rtype,
                              local_field, field, oper, val)
        except AttributeError:
            raise InvalidQueryParams(**{
                'detail': 'The filter query param "%s" specified a filter '
                          'containing a "." indicating a relationship filter '
                          'but a relationship by that name does not exist '
                          'on the requested resource.' % key,
                'links': LINK,
                'parameter': PARAM,
            })
        except ValueError:
            param = Filter(field, oper, val)

        _validate_param(param)
        _validate_rel(param, rels)
        _validate_field(param, fields)
        params.append(param)

    return params
