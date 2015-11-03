"""
    queryparams.page
    ~~~~~~~~~~~~~~~~

    Paginate resources according to limit offset criteria.

    Only two queryparams are supported for pagination:

        page[limit]: number of resources to return
        page[offset]: number of resources to skip
"""

import goldman
import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort


class Paginator(object):
    """ Pagination object

    An instance of this object can be used to express a
    pagination strategy.

    :param limit:
        Integer value of resources to a result set to
    :param offet:
        Integer value of resources to skip
    """

    def __init__(self, limit, offset):

        try:
            self.limit = self._cast_page(limit)
            self.offset = self._cast_page(offset)
        except ValueError:
            self.error = True

        self.total = 0

    def __eq__(self, other):

        try:
            return self.limit == other.limit and \
                self.offset == other.offset
        except AttributeError:
            return False

    def __repr__(self):

        name = self.__class__.__name__

        return '{}({}, {})'.format(name, self.limit, self.offset)

    def __str__(self):

        return '{}, {}'.format(self.limit, self.offset)

    @staticmethod
    def _cast_page(val):
        """ Convert the page limit & offset into int's & type check """

        if len(val) > 1 or int(val[0]) < 0:
            raise ValueError

        return int(val[0])


def init(req, model):  # pylint: disable=unused-argument
    """ Determine the pagination preference by query parameter

    Numbers only, >=0, & each query param may only be
    specified once.

    :return: Paginator object
    """

    limit = req.get_param_as_list('page[limit]') or [goldman.config.PAGE_LIMIT]
    offset = req.get_param_as_list('page[offset]') or [0]

    try:
        return Paginator(limit, offset)
    except ValueError:
        abort(exceptions.InvalidQueryParams(**{
            'detail': 'The page[\'limit\'] & page[\'offset\'] query '
                      'params may only be specified once each & must '
                      'both be an integer >= 0.',
            'link': 'jsonapi.org/format/#fetching-pagination',
            'parameter': 'page',
        }))
