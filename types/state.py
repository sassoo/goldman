"""
    types.state
    ~~~~~~~~~~~

    schematics united states, state type
"""

import us

from schematics.exceptions import ConversionError
from schematics.types import BaseType


class Type(BaseType):
    """ U.S. state field with validation """

    MESSAGES = {
        'convert': 'invalid U.S. state'
    }

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        We return a us.states.State object so the abbreviation
        or long name can be trivially accessed. Additionally,
        some geo type ops are available.

        :return: us.states.State
        """

        if isinstance(value, us.states.State):
            return value

        try:
            state = us.states.lookup(value)

            if not state:
                raise TypeError
        except TypeError:
            raise ConversionError(self.messages['convert'])

        return state

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        By default we convert to a str & use the states long name.

        :return: str
        """

        if value:
            value = str(value)

        return value
