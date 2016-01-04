"""
    request
    ~~~~~~~

    Define our sub-classed Request object to be used instead of the
    native falcon Request object.

    We extend the native Falcon request object in the following
    notable ways:

      * break up the Content-Type itself & its params into
        separate properties. We override the native content_type
        property to NOT include the params.

      * proxy the deserialize method to the selected
        deserializer

      * proxy the deserialize method to the selected
        deserializer

      * is_<method> helpers to evaluate the type of method
        being used as a truthy property
"""

from falcon.request import Request as FalconRequest
from goldman.utils.str_helpers import naked


class Request(FalconRequest):
    """ Subclass the default falcon request object

    First set content_type_params before reassigning content_type
    sans params.
    """

    def __init__(self, *args, **kwargs):

        super(Request, self).__init__(*args, **kwargs)

        self.content_type_params = self._init_content_type_params()
        self.content_type = self._init_content_type()
        self.deserializer = None

    @property
    def auth_scheme(self):
        """ If an Authorization header is present get the scheme

        It is expected to be the first string in a space separated
        list & will always be returned lowercase.
        """

        try:
            auth = getattr(self, 'auth')
            return naked(auth.split(' ')[0]).lower()
        except (AttributeError, IndexError):
            return None

    @property
    def content_required(self):
        """ Check if a Content-* request headers are needed """

        return self.method in ('PATCH', 'POST', 'PUT')

    @property
    def is_deleting(self):
        """ Return True if the request method is DELETE """

        return self.method == 'DELETE'

    @property
    def is_getting(self):
        """ Return True if the request method is GET """

        return self.method == 'GET'

    @property
    def is_patching(self):
        """ Return True if the request method is PATCH """

        return self.method == 'PATCH'

    @property
    def is_posting(self):
        """ Return True if the request method is POST """

        return self.method == 'POST'

    def _init_content_type(self):
        """ Return the Content-Type request header excluding params

        Remove any excess whitespace & lower case it for more
        predictable compares.
        """

        try:
            return naked(self.content_type.split(';')[0]).lower()
        except (AttributeError, IndexError):
            return None

    def _init_content_type_params(self):
        """ Return the Content-Type request header parameters

        Convert all of the semi-colon separated parameters into
        a dict of key/vals. If for some stupid reason duplicate
        & conflicting params are present then the last one
        wins.

        If a particular content-type param is non-compliant
        by not being a simple key=val pair then it is skipped.

        If no content-type header or params are present then
        return an empty dict.

        :return: dict
        """

        ret = {}

        if self.content_type:
            params = self.content_type.split(';')[1:]
            for param in params:
                try:
                    key, val = param.split('=')
                    ret[naked(key)] = naked(val)
                except ValueError:
                    continue

        return ret

    def deserialize(self, *args, **kwargs):
        """ Simple proxy to the deserializer's deserialize function

        This allows code to later run request.deserialize() &
        have it always call the deserialize method on the proper
        deserializer.
        """

        return self.deserializer.deserialize(*args, **kwargs)

    def get_body(self):
        """ Read in the request stream & return it as is

        If the request object doesn't claim to have a request body
        eg no content_length, then return None

        WARN: This could use a ton of memory so use it wisely.
              Images or bulk payloads should be read in more
              intelligently by the deserializer.

        :return:
            request payload as is
        """

        if self.content_length in (None, 0):
            return None

        # pylint: disable=no-member
        return self.stream.read()
