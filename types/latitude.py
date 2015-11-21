"""
    types.latitude
    ~~~~~~~~~~~~~~

    schematics latitude type
"""

from schematics.types import DecimalType


class Type(DecimalType):
    """ Latitude field with validation """

    def __init__(self, **kwargs):

        kwargs.update({
            'min_value': -90,
            'max_value': 90,
        })

        super(Type, self).__init__(**kwargs)
