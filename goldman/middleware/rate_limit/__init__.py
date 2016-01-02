"""
    middleware.rate_limit
    ~~~~~~~~~~~~~~~~~~~~~

    Basic rate limiter for the API to avoid overloading the
    API by friend or asshole. It follows the guidance of
    RFC 6585 section 4 by leveraging HTTP 429 status codes &
    RFC 7231 section 7.1.3 Retry-After headers.

    The middleware looks for goldman.config constants by
    the name of:

        RATE_LIMIT_COUNT - the number of requests allowed
                           within a given RATE_LIMIT_DURATION

        RATE_LIMIT_DURATION - number of seconds long the window
                              of RATE_LIMIT_COUNT applies

    This middleware should probably be the very first
    middleware hit to avoid as much processing as possible.
"""

import goldman
import goldman.exceptions as exceptions

from cachetools import TTLCache
from goldman.utils.error_helpers import abort


class Middleware(object):
    """ Falcon rate limiting middleware """

    def __init__(self):

        self.count = goldman.config.RATE_LIMIT_COUNT
        self.duration = goldman.config.RATE_LIMIT_DURATION

        self.cache = TTLCache(maxsize=self.count, ttl=self.duration)

    @property
    def _error_headers(self):
        """ Return a dict of headers in every auth failure """

        return {
            'Retry-After': self.duration,
            'X-RateLimit-Limit': self.count,
            'X-RateLimit-Remaining': 0,
        }

    # pylint: disable=unused-argument
    def process_request(self, req, resp):
        """ Process the request before routing it. """

        key = req.env['REMOTE_PORT'] + req.env['REMOTE_ADDR']
        val = self.cache.get(key, 0)

        if val == self.count:
            abort(exceptions.TooManyRequests(headers=self._error_headers))
        else:
            self.cache[key] = val + 1
