"""
    types.to_one
    ~~~~~~~~~~~~

    schematics datetime type

    This should be used instead of the native schematics datetime
    type. It supports epoch serialization/deserialization in addition
    to the default behavior.
"""

from goldman.utils.str_helpers import str_to_uuid
from schematics.exceptions import (
    ConversionError,
    ValidationError
)
from schematics.types import BaseType


class ToOneType(BaseType):
    """ Custom field for our ToOne relationships """

    MESSAGES = {
        'rtype': 'resource type must be {0} not {1}',
        'uuid': 'id is not a valid UUID string'
    }

    def __init__(self, rtype, **kwargs):
        self.rtype = rtype
        # self.uuid = uuid

        super(ToOneType, self).__init__(**kwargs)

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        :return: model object
        """

        # must be a model object already
        if value and not isinstance(value, dict):
            return value

        try:
            if value and value['rtype'] != self.rtype:
                raise ValueError

            elif value:
                # value = get_model_by_rtype(value['rtype'])

                if not value:
                    raise ValueError
        except ValueError:
            raise ConversionError(self.messages['rtype']).format(
                self.rtype,
                value['rtype'],
            )

        value.uuid = value['uuid']

        return value

    def validate_uuid(self, value):
        """ Schematics validator """

        if value:
            try:
                str_to_uuid(value)
            except ValueError:
                raise ValidationError(self.messages['uuid'])

        return value
