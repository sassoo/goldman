"""
    utils.error_handlers
    ~~~~~~~~~~~~~~~~~~~~

    Convenient interfaces for aborting on error similar
    to abort() in the Flask micro-web framework.
"""

from goldman.serializers.jsonapi_error import Serializer as \
    JSONAPIErrorSerializer


__all__ = ['abort']


def abort(error):
    """ Immediately raise our serializer with error(s)

    See jsonapi_error.Serializer docs on the usage of error
    """

    raise JSONAPIErrorSerializer(error)
