"""
    utils.url_helpers
    ~~~~~~~~~~~~~~~~~

    Interfaces that make constructing URL's a bit more easy.
    It's best not to scatter URL construction around in the code
    so it's hopefully easier to adjust if the API's routes are
    updated.

    If you are familiar with the Flask micro-web framework these
    interfaces will give you a url_for() type equivalent.
"""

import goldman


__all__ = ['rid_url', 'rtype_url']


def rtype_url(rtype):
    """ Return a string relative URL for a resource endpoint

    This represents the API endpoint for performing any
    supported interactions of a given model.

    :param rtype:
        string resource type name of the model
    :return:
        relative string URL
    """

    return '%s/%s' % (goldman.config.BASE_URL, rtype)


def rid_url(rtype, rid):
    """ Return a string relative URL for a unique resource id

    :param rtype:
        string resource type name of the model
    :param rid:
        string rid of the single model
    :return:
        relative string URL
    """

    return '%s/%s' % (rtype_url(rtype), rid)
