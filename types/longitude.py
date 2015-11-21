"""
    types.longitude
    ~~~~~~~~~~~~~~~

    schematics longitude type
"""

from schematics.types import DecimalType


class Type(DecimalType):
    """ Longitude field with validation """

    def __init__(self, **kwargs):

        kwargs.update({
            'min_value': -180,
            'max_value': 180,
        })

        super(Type, self).__init__(**kwargs)
