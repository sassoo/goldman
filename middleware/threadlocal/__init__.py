"""
    middleware.threadlocal
    ~~~~~~~~~~~~~~~~~~~~~~

    This middleware will initialize the native python thread.local
    capability common in other python web frameworks. Any attributes
    anchored on the goldman.sess attribute is unique & isolated
    to the thread handling the request.
"""

import goldman


class Middleware(object):
    """ Thread local storage middleware. """

    # pylint: disable=unused-argument
    def process_request(self, req, resp):
        """ Process the request before routing it. """

        # goldman.sess.cache = redis, memcached, whatever
        goldman.sess.req = req

        if goldman.config.STORE:
            goldman.sess.store = goldman.config.STORE()

    def process_resource(self, req, resp, resource):
        """ Process the request after routing.

        The logged in identity should be known by the time
        the resource is found.
        """

        goldman.sess.login = req.login
