"""
    request
    ~~~~~~~

    Define our sub-classed Request object to be used instead of the
    native falcon Request object.
"""

from falcon.request import Request as FalconRequest


class Request(FalconRequest):
    """ Subclass the default falcon request object """

    def __init__(self, *args, **kwargs):

        super(Request, self).__init__(*args, **kwargs)

        self.deserializer = None
        self.login = None

    @property
    def content_type_params(self):
        """ Return the Content-Type request header parameters

        Convert all of the colon separated parameters into
        a dict of key/vals. If some stupid reason duplicate
        & conflicting params are present then the last one
        wins.

        If a particular content-type param is non-compliant
        by not being a simple key=val pair then it is skipped.

        If no content-type header or params are present then
        return None.

        :return: dict or None
        """

        ret = {}

        if self.content_type:
            # pylint: disable=no-member
            params = self.content_type.split(';')[1:]

            for param in params:
                try:
                    key, val = param.split('=')
                except (AttributeError, ValueError):
                    continue

                ret[key] = val.strip('"')

        return ret or None

    @property
    def content_type_required(self):
        """ Check if a Content-Type request header is needed

        True if the HTTP Method requires a Content-Type
        otherwise False.
        """

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

        :return: request payload as is
        """

        if self.content_length in (None, 0):
            return None

        # pylint: disable=no-member
        return self.stream.read()
