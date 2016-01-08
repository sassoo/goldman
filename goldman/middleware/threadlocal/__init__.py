"""
    middleware.threadlocal
    ~~~~~~~~~~~~~~~~~~~~~~

    This middleware will initialize the native python thread.local
    capability common in other python web frameworks.

    Any attributes anchored on the goldman.sess attribute is
    unique & isolated to the thread handling the request.
"""

import goldman


class Middleware(object):
    """ Thread local storage middleware. """

    # pylint: disable=unused-argument
    def process_request(self, req, resp):
        """ Process the request before routing it. """

        goldman.sess.req = req

        if goldman.config.STORE:
            goldman.sess.store = goldman.config.STORE()
