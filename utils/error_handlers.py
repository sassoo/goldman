"""
    utils.error_handlers
    ~~~~~~~~~~~~~~~~~~~~

    Convenient interfaces for aborting on error similar
    to abort() in the Flask micro-web framework.
"""

import goldman.exceptions as exceptions

from goldman.serializers.jsonapi_error import Serializer as \
    JSONAPIErrorSerializer


__all__ = ['abort', 'mod_fail']


def abort(error):
    """ Immediately raise our serializer with error(s)

    See jsonapi_error.Serializer docs on the usage of error
    """

    raise JSONAPIErrorSerializer(error)


def mod_fail(msg):
    """ Simple wrapper around aborting with ModificationDenied """

    abort(exceptions.ModificationDenied(**{
        'detail': msg
    }))
