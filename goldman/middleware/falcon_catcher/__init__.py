"""
    middleware.falcon_catcher
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Some fundamental errors can't be intercepted any other
    way in Falcon. These include 404 when the route isn't found
    & 405 when the method is bunk. Falcon will try to send its
    own errors.

    In these cases, intercept them & replace them with our
    JSON API compliant version.

    TIP: The (de)serializers should be responsible for the checks
         that are unique to them. DO NOT put those types of checks
         in this file!
"""

import goldman.exceptions as exceptions
import falcon

from goldman.utils.error_helpers import abort


class Middleware(object):
    """ Falcon error handler middleware """

    # pylint: disable=unused-argument
    def process_response(self, req, resp, resource):
        """ Post-processing of the response (after routing).

        If no route could be determined then the resource will be
        None.
        """

        if not resource and resp.status == falcon.HTTP_NOT_FOUND:
            abort(exceptions.RouteNotFound)

        elif resp.status == falcon.HTTP_METHOD_NOT_ALLOWED:
            abort(exceptions.MethodNotAllowed)
