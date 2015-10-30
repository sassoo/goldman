"""
    resources.base
    ~~~~~~~~~~~~~~

    Base resource object.

    This should be sub-classed by other more mature resource
    handlers. It's utility is providing common tasks & error handling
    for all resources.
"""


class Resource(object):
    """ Base resource class """

    DESERIALIZERS = []
    SERIALIZERS = []

    def __init__(self):

        if not self.DESERIALIZERS:
            raise NotImplementedError('resource DESERIALIZERS required')

        elif not self.SERIALIZERS:
            raise NotImplementedError('resource SERIALIZERS required')
