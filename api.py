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


class API(falcon.API):
    """ Subclass the falcon.API object with our own

    Goldman uses custom request, response, & route loading
    techniques when compared to the falcon.API object.
    """

    MIDDLEWARE = []
    ROUTES = []

    def __init__(self, *args, **kwargs):

        super(API, self).__init__(
            middleware=self.MIDDLEWARE,
            request_type=goldman.Request,
            response_type=goldman.Response,
            *args, **kwargs
        )

        self._load_routes()
        self.set_error_serializer(self._serialize_error)

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
                ('/logins/{uuid}', goldman.ModelResource(LoginModel)),
            ]
        """

        for route in self.ROUTES:
            self.add_route(*route)

    @staticmethod
    def _serialize_error(*args):
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

        error = args[1].to_dict()

        if 'description' in error:
            error['detail'] = error.pop('description')

        if 'link' in error:
            error['link'] = {'about': error['link']['href']}

        error = json.dumps({'errors': [error]})

        return (goldman.config.JSONAPI_MIMETYPE, error)
