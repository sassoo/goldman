"""
    middleware.basicauth
    ~~~~~~~~~~~~~~~~~~~~

    Basic authentication implementation as documented in RFC-1945
    & RFC-2617 respectively.
"""

import goldman.exceptions as exceptions

from app.store import store
from goldman.utils.error_handlers import abort
from base64 import b64decode


# pylint: disable=too-few-public-methods
class Middleware(object):
    """ Ensure RFC compliance & authenticate the user. """

    # pylint: disable=unused-argument
    def process_request(self, req, resp):
        """ Process the request before routing it.

        Per RFC 2617 section 3.2.1 an invalid Authorization header
        or as the spec calls it "not Acceptable" header should
        return a 401.

        If authentication succeeds then the request object will
        have a login property updated with a value of the login
        model from the database.
        """

        if not req.auth:
            abort(exceptions.BasicAuthRequired)

        elif not self._validate_scheme(req):
            abort(exceptions.InvalidAuthSyntax)

        username, password = self._get_creds(req)

        if not username or not password:
            abort(exceptions.InvalidAuthSyntax)

        login = self._get_login(username)

        if not login:
            abort(exceptions.InvalidUsername)

        elif login.gen_hash(password) != login.password:
            abort(exceptions.InvalidPassword)

        else:
            req.login = login

    @staticmethod
    def _get_creds(req):
        """ Return a tuple of username & password from the request

        Per RFC 2617 section 2 the username & password are colon
        separated & base64 encoded. They will come after the schema
        is declared.

        :return: tuple (username, password) or None, None
        """

        try:
            creds = req.auth.split(' ')[1]
            creds = b64decode(creds)
            username, password = creds.split(':')
        except (IndexError, TypeError, ValueError):
            return None, None

        return username, password

    @staticmethod
    def _get_login(username):
        """ Return the Login model from the database by username

        :return: Login model or None
        """

        return store.search('logins', ('username', 'eq', username))

    @staticmethod
    def _validate_scheme(req):
        """ True if the authentication scheme is Basic

        Per RFC 2617 section 1.2 the string Basic is case
        insensitive & should be followed by a space & the
        encoded creds.

        :return: bool
        """

        scheme = req.auth.split(' ')[0]

        return scheme.lower() == 'basic'
