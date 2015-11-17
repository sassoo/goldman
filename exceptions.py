"""
    exceptions
    ~~~~~~~~~~

    Custom error classes to be raised throughout the app to
    abort requests with JSON API compliant errors
"""

import goldman
import falcon


class APIException(Exception):
    """ Exception class for error handling in JSON API format.

    :spec: http://jsonapi.org/format/#errors
    """

    def __init__(self, **kwargs):

        super(APIException, self).__init__()

        kwargs['links'] = {'about': kwargs.get('links', '')}
        kwargs['detail'] = kwargs.get('detail', '')

        self.data = kwargs

    def __call__(self):

        return self

    def __getattr__(self, key):

        if key == "data":
            return self.data
        else:
            return self.data[key]

    def to_dict(self):
        """ Convenience function to get the exception as a dict """

        return self.data


"""
    400 Bad Request
    ~~~~~~~~~~~~~~~
"""


class EmptyRequestBody(APIException):
    """ The request body must not be empty """

    DETAIL = 'The operation you attempted requires a request body ' \
             'yet none was found. Please generate a valid request body ' \
             '& retry your request.'

    def __init__(self, **kwargs):
        super(EmptyRequestBody, self).__init__(**{
            'code': 'empty_request_body',
            'detail': self.DETAIL,
            'status': falcon.HTTP_400,
            'title': 'Empty request body',
        })


class InvalidQueryParams(APIException):
    """ The query parameter is invalid

    This exception supports detail & links overrides, however
    the source object containing a parameter to the attribute
    that caused the failure is required.
    """

    DETAIL = 'One or more query parameters are invalid or corrupt. ' \
             'Please modify your request & retry.'

    def __init__(self, **kwargs):
        super(InvalidQueryParams, self).__init__(**{
            'code': 'invalid_query_param',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'source': {'parameter': kwargs['parameter']},
            'status': falcon.HTTP_400,
            'title': 'Invalid or corrupt query parameter',
        })


class InvalidRequestBody(APIException):
    """ The request body is invalid

    This exception supports detail & links overrides.
    """

    DETAIL = 'The body of your request is fundamentally invalid or ' \
             'corrupt. We weren\'t able to even begin processing it ' \
             'because of the issue. Please modify your request body ' \
             '& retry.'

    def __init__(self, **kwargs):
        super(InvalidRequestBody, self).__init__(**{
            'code': 'invalid_request_body',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'status': falcon.HTTP_400,
            'title': 'Invalid or corrupt request body',
        })


class InvalidRequestHeader(APIException):
    """ One or more request headers are invalid

    This exception supports detail & links overrides.
    """

    DETAIL = 'One or more of your request headers and/or there ' \
             'parameters are invalid or corrupt. Please modify ' \
             'your request headers & retry.'

    def __init__(self, **kwargs):
        super(InvalidRequestHeader, self).__init__(**{
            'code': 'invalid_request_header',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'status': falcon.HTTP_400,
            'title': 'Invalid or corrupt request header',
        })


class InvalidURL(APIException):
    """ The URL is invalid

    This exception supports detail & links overrides.
    """

    DETAIL = 'The URL provided is invalid. Please modify your ' \
             'request URL & retry.'

    def __init__(self, **kwargs):
        super(InvalidURL, self).__init__(**{
            'code': 'invalid_url',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'status': falcon.HTTP_400,
            'title': 'Invalid or corrupt URL',
        })


"""
    401 Unauthorized
    ~~~~~~~~~~~~~~~~
"""


class BasicAuthRequired(APIException):
    """ The API requires Basic Authentication """

    DETAIL = 'The URL requested (route) requires authentication. ' \
             'We couldn\'t find an Authorization header as documented ' \
             'in the Basic Authentication section of RFC 7235. Please ' \
             'retry your request with authentication.'

    def __init__(self, **kwargs):
        realm = 'Basic realm="{}"'.format(goldman.config.AUTH_REALM)

        super(BasicAuthRequired, self).__init__(**{
            'code': 'basic_auth_required',
            'detail': self.DETAIL,
            'headers': {
                'WWW-Authenticate': realm,
            },
            'links': 'tools.ietf.org/html/rfc7235',
            'status': falcon.HTTP_401,
            'title': 'Basic Authentication is required',
        })


class InvalidAuthSyntax(APIException):
    """ The Authorization header provided is invalid. """

    DETAIL = 'The Authorization header you provided could not be properly ' \
             'interpreted. It appears to be malformed & does not follow ' \
             'the guidelines of RFC 7235. Please check your syntax.'

    def __init__(self, **kwargs):
        realm = 'Basic realm="{}"'.format(goldman.config.AUTH_REALM)

        super(InvalidAuthSyntax, self).__init__(**{
            'code': 'invalid_auth_syntax',
            'detail': self.DETAIL,
            'headers': {
                'WWW-Authenticate': realm,
            },
            'links': 'tools.ietf.org/html/rfc7235',
            'status': falcon.HTTP_401,
            'title': 'Invalid Authorization header',
        })


class InvalidPassword(APIException):
    """ The password provided is invalid. """

    DETAIL = 'The password provided could not be validated. Confirm ' \
             'you spelled it correctly & retry.'

    def __init__(self, **kwargs):
        realm = 'Basic realm="{}"'.format(goldman.config.AUTH_REALM)

        super(InvalidPassword, self).__init__(**{
            'code': 'invalid_password',
            'detail': self.DETAIL,
            'headers': {
                'WWW-Authenticate': realm,
            },
            'status': falcon.HTTP_401,
            'title': 'Invalid password',
        })


class InvalidUsername(APIException):
    """ The username provided is invalid. """

    DETAIL = 'The username provided could not be found. Confirm ' \
             'you spelled it correctly & retry.'

    def __init__(self, **kwargs):
        realm = 'Basic realm="{}"'.format(goldman.config.AUTH_REALM)

        super(InvalidUsername, self).__init__(**{
            'code': 'invalid_username',
            'detail': self.DETAIL,
            'headers': {
                'WWW-Authenticate': realm,
            },
            'status': falcon.HTTP_401,
            'title': 'Invalid username',
        })


"""
    403 Forbidden
    ~~~~~~~~~~~~~
"""


class AccessDenied(APIException):
    """ The logged in user lacks privileges to get the resource. """

    DETAIL = 'The access attempt on the requested resource ' \
             'was denied.'

    def __init__(self, **kwargs):
        super(AccessDenied, self).__init__(**{
            'code': 'access_denied',
            'detail': kwargs.get('detail', self.DETAIL),
            'status': falcon.HTTP_403,
            'title': 'Access denied accessing resource',
        })


class ModificationDenied(APIException):
    """ The logged in user lacks privileges for attempted modification. """

    DETAIL = 'The modification attempt on the requested resource ' \
             'was denied.'

    def __init__(self, **kwargs):
        super(ModificationDenied, self).__init__(**{
            'code': 'modification_denied',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'status': falcon.HTTP_403,
            'title': 'Access denied in modification attempt',
        })


class TLSRequired(APIException):
    """ The API requires TLS (SSL) security """

    DETAIL = 'The URL requested (route) requires https (TLS). ' \
             'Any other protocols are not allowed. Please retry ' \
             'your request using https.'

    def __init__(self, **kwargs):
        super(TLSRequired, self).__init__(**{
            'code': 'ssl_required',
            'detail': self.DETAIL,
            'links': 'en.wikipedia.org/wiki/HTTPS',
            'status': falcon.HTTP_403,
            'title': 'TLS is required',
        })


"""
    404 Not Found
    ~~~~~~~~~~~~~
"""


class DocumentNotFound(APIException):
    """ The document queried for could not be found """

    DETAIL = 'We processed your request just fine but could not ' \
             'find the document you requested. Did it get deleted?'

    def __init__(self, **kwargs):

        super(DocumentNotFound, self).__init__(**{
            'code': 'document_not_found',
            'detail': self.DETAIL,
            'status': falcon.HTTP_404,
            'title': 'Queried document not found',
        })


class RouteNotFound(APIException):
    """ The API URL (route) requested does not exist """

    DETAIL = 'The URL requested (route) could not be found. ' \
             'We were unable to even query for any documents you may ' \
             'have been looking for because we have no routes registered ' \
             'by that URL. This is commonly a spelling error.'

    def __init__(self, **kwargs):

        super(RouteNotFound, self).__init__(**{
            'code': 'route_not_found',
            'detail': self.DETAIL,
            'status': falcon.HTTP_404,
            'title': 'API endpoint not found',
        })


"""
    405 Method Not Allowed
    ~~~~~~~~~~~~~~~~~~~~~~
"""


class MethodNotAllowed(APIException):
    """ The HTTP Method isn't allowed on the given endpoint (route) """

    DETAIL = 'The URL requested (route) does not support that method. ' \
             'We support a wide array of HTTP Methods but they are ' \
             'limited across endpoints. Please review our docs.'

    def __init__(self, **kwargs):

        super(MethodNotAllowed, self).__init__(**{
            'code': 'method_not_allowed',
            'detail': self.DETAIL,
            'status': falcon.HTTP_405,
            'title': 'HTTP Method not allowed',
        })


"""
    406 Not Acceptable
    ~~~~~~~~~~~~~~~~~~
"""


class RequestNotAcceptable(APIException):
    """ No acceptable serializers found in the request """

    DETAIL = 'Your request did not contain an Accept header with any ' \
             'MIMETYPE\'s that we support. Please modify your ' \
             'response preference & retry.'

    def __init__(self, **kwargs):

        super(RequestNotAcceptable, self).__init__(**{
            'code': 'request_not_acceptable',
            'detail': self.DETAIL,
            'links': 'tools.ietf.org/html/rfc7231#section-5.3.2',
            'status': falcon.HTTP_406,
            'title': 'Unacceptable response preference',
        })


class SerializerNotAllowed(APIException):
    """ The serializer chosen is not allowed for the URL requested """

    DETAIL = 'Your response preference (Accept header) is supported by ' \
             'our API but not for that route. Please review our docs ' \
             '& retry your request with a different response preference.'

    def __init__(self, **kwargs):

        super(SerializerNotAllowed, self).__init__(**{
            'code': 'serializer_not_allowed',
            'detail': self.DETAIL,
            'status': falcon.HTTP_406,
            'title': 'Serializer is unacceptable for this route',
        })


"""
    409 Conflict
    ~~~~~~~~~~~~
"""


class ResourceConflict(APIException):
    """ Generic resource conflict """

    DETAIL = 'Your request had a generic resource conflict.'

    def __init__(self, **kwargs):

        super(ResourceConflict, self).__init__(**{
            'code': 'resource_conflict',
            'detail': kwargs.get('detail', self.DETAIL),
            'status': falcon.HTTP_409,
            'title': 'Generic resource conflict',
        })


class ResourceTypeNotAllowed(APIException):
    """ The resource type is not allowed for the URL requested """

    DETAIL = 'You tried saving a resource to a route that doesn\'t ' \
             'match the type in your request payload. Please alter ' \
             'the route or the type in your payload & retry your request.'

    def __init__(self, **kwargs):

        super(ResourceTypeNotAllowed, self).__init__(**{
            'code': 'resource_type_not_allowed',
            'detail': self.DETAIL,
            'status': falcon.HTTP_409,
            'title': 'Resource type not allowed for this route',
        })


"""
    415 Unsupported Media Type
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class ContentTypeRequired(APIException):
    """ The request requires a Content-Type header """

    DETAIL = 'The URL requested (route) & the HTTP method used ' \
             'require a Content-Type header. Unfortunately we ' \
             'couldn\'t find the header in your request. Please ' \
             'retry your request with all required headers.'

    def __init__(self, **kwargs):

        super(ContentTypeRequired, self).__init__(**{
            'code': 'content_type_required',
            'detail': self.DETAIL,
            'links': 'tools.ietf.org/html/rfc7231#section-3.1.1.5',
            'status': falcon.HTTP_415,
            'title': 'Content-type header required',
        })


class DeserializerNotAllowed(APIException):
    """ The deserializer chosen is not allowed for the URL requested """

    DETAIL = 'Your requested Media Type (Content-Type header) is ' \
             'supported by our API but not for that route. Please ' \
             'review our docs & retry your request with a different ' \
             'media type.'

    def __init__(self, **kwargs):

        super(DeserializerNotAllowed, self).__init__(**{
            'code': 'deserializer_not_allowed',
            'detail': self.DETAIL,
            'links': 'tools.ietf.org/html/rfc7231#section-6.5.13',
            'status': falcon.HTTP_415,
            'title': 'Deserializer is unsupported for this route',
        })


class RequestUnsupported(APIException):
    """ No requested deserializer could be found """

    DETAIL = 'Your requested Media Type (Content-Type header) is ' \
             'unsupported by our API. Please review our docs & ' \
             'retry your request with a different media type.'

    def __init__(self, **kwargs):

        super(RequestUnsupported, self).__init__(**{
            'code': 'content_type_unsupported',
            'detail': self.DETAIL,
            'links': 'tools.ietf.org/html/rfc7231#section-6.5.13',
            'status': falcon.HTTP_415,
            'title': 'The Content-Type provided is unsupported',
        })


"""
    422 Unprocessable Entity
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class ValidationFailure(APIException):
    """ The models validation routines failed when saving

    This exception supports detail & links overrides, however
    the source object containing a pointer to the attribute
    that caused the failure is required.
    """

    DETAIL = 'Generic validation error message'

    def __init__(self, pointer, **kwargs):
        super(ValidationFailure, self).__init__(**{
            'code': 'validation_failure',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'source': {'pointer': pointer},
            'status': '422 Unprocessable Entity',
            'title': 'Your attribute modification failed validations',
        })


"""
    500 Internal Server Error
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class GenericError(APIException):
    """ Something puked within our API & is probably 3rd party

    This exception supports detail & links overrides.
    """

    DETAIL = 'Generic internal server error'

    def __init__(self, **kwargs):
        super(GenericError, self).__init__(**{
            'code': 'generic_error',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'status': '500 Internal Server Error',
            'title': 'The request had an unexpected error',
        })


"""
    503 Service Unavailable
    ~~~~~~~~~~~~~~~~~~~~~~~
"""


class ServiceUnavailable(APIException):
    """ Something puked within our API, probably the database

    This exception supports detail & links overrides.
    """

    DETAIL = 'Generic service unavailable error'

    def __init__(self, **kwargs):
        super(ServiceUnavailable, self).__init__(**{
            'code': 'service_unavailable',
            'detail': kwargs.get('detail', self.DETAIL),
            'links': kwargs.get('links'),
            'status': '503 Service Unavailable',
            'title': 'Our server is currently unavailable',
        })


class DatabaseUnavailable(ServiceUnavailable):
    """ Something puked when accessing the database

    This is simply a convenience class
    """

    DETAIL = 'When handling your request we experienced an unexpected ' \
             'error when communicating with the database. This is likely ' \
             'transitory so please retry your request.'
