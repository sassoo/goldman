"""
    types.datetime
    ~~~~~~~~~~~~~~

    schematics datetime type

    This should be used instead of the native schematics datetime
    type. It supports epoch serialization/deserialization in addition
    to the default behavior.
"""

from __future__ import absolute_import
from datetime import datetime as dt

from schematics.types import DateTimeType as SchematicsDateTimeType


class Type(SchematicsDateTimeType):
    """ Extended DateTimeType to support epoch timestamps """

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        If epoch_date is true then convert the `datetime.datetime`
        object into an epoch `int`.
        """

        if context and context.get('epoch_date'):
            epoch = dt(1970, 1, 1)
            value = (value - epoch).total_seconds()
            return int(value)
        elif context and context.get('datetime_date'):
            return value
        else:
            return super(Type, self).to_primitive(value, context)
