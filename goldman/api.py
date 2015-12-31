"""
    api
    ~~~

    Our custom sub-class of the falcon.API main object.

    API will load the routes, order the middleware's, &
    register our custom request/response objects.
"""

import falcon
import goldman
import json

from goldman.request import Request
from goldman.response import Response


__all__ = ['API']


class API(falcon.API):
    """ Subclass the falcon.API object with our own

    Goldman uses custom request, response, & route loading
    techniques when compared to the falcon.API object.
    """

    MIDDLEWARE = []
    RESOURCES = []
    ROUTES = []

    def __init__(self):

        middleware = [
            goldman.SecurityMiddleware(),
            goldman.RFC7231Middleware(),
            goldman.FalconCatcherMiddleware(),
            goldman.DeserializerMiddleware(),
            goldman.SerializerMiddleware(),
            goldman.ModelQpsMiddleware(),
            goldman.ThreadLocalMiddleware(),
        ]
        middleware += self.MIDDLEWARE

        super(API, self).__init__(
            middleware=middleware,
            request_type=Request,
            response_type=Response,
        )

        self._load_resources()
        self._load_routes()
        self.set_error_serializer(self._error_serializer)

    def _load_resources(self):
        """ Load all the native goldman resources.

        The route or API endpoint will be automatically determined
        based on the resource object instance passed in.
        """

        for resource in self.RESOURCES:
            if isinstance(resource, goldman.ModelsResource):
                route = '/%s' % resource.rtype

            elif isinstance(resource, goldman.ModelResource):
                route = '/%s/{rid}' % resource.rtype

            elif isinstance(resource, goldman.RelatedResource):
                route = '/%s/{rid}/{related}' % resource.rtype

            else:
                raise TypeError('unsupported resource type')

            self.add_route(*(route, resource))

    def _load_routes(self):
        """ Load all the routes.

        A class constant of ROUTES is expected containing
        an array of tuples in the following format:

            ROUTES = [
                ('/<endpoint>', <resource instance>)
            ]

        a real life example would look like:

            ROUTES = [
                ('/logins', goldman.ModelsResource(LoginModel)),
                ('/logins/{rid}', goldman.ModelResource(LoginModel)),
            ]

        This is the same format the native falcon `add_route`
        method wants the routes.
        """

        for route in self.ROUTES:
            self.add_route(*route)

    @staticmethod
    def _error_serializer(req, exc):  # pylint: disable=unused-argument
        """ Serializer for native falcon HTTPError exceptions.

        We override the default serializer with our own so we can
        ensure the errors are serialized in a JSON API compliant format.

        Surprisingly, most falcon error attributes map directly to
        the JSON API spec. The few that don't can be mapped accordingly:

            HTTPError                     JSON API
            ~~~~~~~~~                     ~~~~~~~~

            error['description']    ->   error['detail']
            error['link']['href']   ->   error['link']['about']

        Per the falcon docs this function should return a tuple of

            (MIMETYPE, BODY PAYLOAD)
        """

        error = exc.to_dict()

        if 'description' in error:
            error['detail'] = error.pop('description')

        if 'link' in error:
            error['link'] = {
                'about': error['link']['href']
            }

        error = json.dumps({'errors': [error]})

        return (goldman.config.JSONAPI_MIMETYPE, error)
