"""
    utils.error_helpers
    ~~~~~~~~~~~~~~~~~~~

    Convenient interfaces for aborting on error similar
    to abort() in the Flask micro-web framework.
"""

from goldman.exceptions import AccessDenied, ModificationDenied
from goldman.serializers.jsonapi_error import Serializer as \
    JsonApiErrorSerializer


__all__ = ['abort', 'access_fail', 'mod_fail']


def abort(error):
    """ Immediately raise our serializer with error(s)

    See jsonapi_error.Serializer docs on the usage of error
    """

    raise JsonApiErrorSerializer(error)


def access_fail(msg=None):
    """ Simple wrapper around aborting with AccessDenied """

    if msg:
        abort(AccessDenied(**{
            'detail': msg,
        }))
    else:
        abort(AccessDenied)


def mod_fail(msg=None):
    """ Simple wrapper around aborting with ModificationDenied """

    if msg:
        abort(ModificationDenied(**{
            'detail': msg,
        }))
    else:
        abort(ModificationDenied)
