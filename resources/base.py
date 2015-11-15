"""
    resources.base
    ~~~~~~~~~~~~~~

    Base resource object.

    This should be sub-classed by other more mature resource
    handlers. It's utility is providing common tasks & error handling
    for all resources.
"""

import types


class Resource(object):
    """ Base resource class """

    DESERIALIZERS = []
    SERIALIZERS = []

    def __init__(self, disable=None):

        disable = disable or []
        rondrs = getattr(self, 'rondrs', [])

        if not self.DESERIALIZERS:
            raise NotImplementedError('resource DESERIALIZERS required')

        elif not self.SERIALIZERS:
            raise NotImplementedError('resource SERIALIZERS required')

        for rondr in rondrs:
            func = types.MethodType(rondr, self)
            name = rondr.func_name

            if name not in disable:
                setattr(self, name, func)
