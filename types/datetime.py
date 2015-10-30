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


class DateTimeType(SchematicsDateTimeType):
    """ Extended DateTimeType to support epoch timestamps """

    def to_native(self, value, context=None):
        """ Schematics deserializer override """

        if isinstance(value, dt):
            return value

        try:
            value = dt.utcfromtimestamp(value)
        except TypeError:
            value = super(DateTimeType, self).to_native(value, context)

        return value

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        If epoch_date is true then convert the `datetime.datetime`
        object into an epoch `int`.
        """

        if context and context.get('epoch_date'):
            epoch = dt(1970, 1, 1)
            value = (value - epoch).total_seconds()
            value = int(value)
        elif context and context.get('datetime_date'):
            pass
        else:
            value = super(DateTimeType, self).to_primitive(value, context)

        return value
