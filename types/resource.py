"""
    types.resource
    ~~~~~~~~~~~~~~

    schematics resource type, type

    This is like a contant type except it does allow being
    written to. Validation then confirms the written value
    is the constant value.
"""

from schematics.exceptions import ValidationError
from schematics.types import StringType


class Type(StringType):
    """ Resource type of the underlying model """

    MESSAGES = {
        'rtype': 'value must be {0}, not {1}'
    }

    def __init__(self, rtype, **kwargs):

        self.rtype = rtype

        super(Type, self).__init__(**kwargs)

    def to_native(self, value, context=None):
        """ Schematics deserializer override """

        if not value:
            value = self.rtype

        return value

    def validate_rtype(self, value):
        """ Schematics validator

        The provided rtype must match that of the
        underlying model.

        :return: str
        """

        if not value or value != self.rtype:
            msg = self.messages['rtype'].format(self.rtype, value)

            raise ValidationError(msg)

        return value
