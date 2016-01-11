"""
    queryparams.page
    ~~~~~~~~~~~~~~~~

    Paginate resources according to limit offset criteria
    according to.

        jsonapi.org/format/#fetching-pagination

    Only two query params are supported for pagination:

        page[limit]: number of resources to return
        page[offset]: number of resources to skip
"""

import goldman

from goldman.exceptions import InvalidQueryParams


LINK = 'jsonapi.org/format/#fetching-pagination'
PARAM = 'page'


class Paginator(object):
    """ Pagination object

    An instance of this object can be used to express a
    pagination strategy.

    :param limit:
        Integer value of resources to limit a result
        set to
    :param offet:
        Integer value of resources to skip
    """

    def __init__(self, limit, offset):

        self.limit = self._cast_page(limit)
        self.offset = self._cast_page(offset)
        self.total = 0

    def __eq__(self, other):

        try:
            return self.limit == other.limit and \
                self.offset == other.offset
        except AttributeError:
            return False

    def __repr__(self):

        name = self.__class__.__name__

        return '%s(%s, %s)' % (name, self.limit, self.offset)

    def __str__(self):

        return '%s, %s' % (self.limit, self.offset)

    @property
    def current(self):
        """ Generate query parameters for the current page """

        return 'page[offset]=%s&page[limit]=%s' % (self.offset, self.limit)

    @property
    def first(self):
        """ Generate query parameters for the first page """

        if self.total and self.limit < self.total:
            return 'page[offset]=0&page[limit]=%s' % self.limit
        else:
            return None

    @property
    def last(self):
        """ Generate query parameters for the last page """

        if self.limit > self.total:
            return None
        elif self.offset >= self.total:
            return None
        else:
            offset = (self.total / self.limit) * self.limit
            limit = self.total - offset
            return 'page[offset]=%s&page[limit]=%s' % (offset, limit)

    @property
    def more(self):
        """ Generate query parameters for the next page """

        if self.offset + self.limit + self.limit >= self.total:
            return self.last
        else:
            offset = self.offset + self.limit
            return 'page[offset]=%s&page[limit]=%s' % (offset, self.limit)

    @property
    def prev(self):
        """ Generate query parameters for the prev page """

        if self.total:
            if self.offset - self.limit - self.limit < 0:
                return self.first
            else:
                offset = self.offset - self.limit
                return 'page[offset]=%s&page[limit]=%s' % (offset, self.limit)
        else:
            return None

    @staticmethod
    def _cast_page(val):
        """ Convert the page limit & offset into int's & type check """

        try:
            val = int(val)
            if val < 0:
                raise ValueError
            return val
        except (TypeError, ValueError):
            raise ValueError

    def to_dict(self):
        """ Convert the Paginator into a dict """

        return {
            'current': self.current,
            'first': self.first,
            'last': self.last,
            'next': self.more,
            'prev': self.prev,
        }


def init(req, model):  # pylint: disable=unused-argument
    """ Determine the pagination preference by query parameter

    Numbers only, >=0, & each query param may only be
    specified once.

    :return: Paginator object
    """

    limit = req.get_param('page[limit]') or goldman.config.PAGE_LIMIT
    offset = req.get_param('page[offset]') or 0

    try:
        return Paginator(limit, offset)
    except ValueError:
        raise InvalidQueryParams(**{
            'detail': 'The page[\'limit\'] & page[\'offset\'] query '
                      'params may only be specified once each & must '
                      'both be an integer >= 0.',
            'links': 'jsonapi.org/format/#fetching-pagination',
            'parameter': 'page',
        })
