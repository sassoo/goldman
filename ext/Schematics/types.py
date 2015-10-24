"""
    Schematics.types
    ~~~~~~~~~~~~~~~~

    All of our custom schematics model types.
"""

import phonenumbers as pn
import re
import us

from datetime import datetime as dt
from goldman.utils.str_helpers import str_to_uuid
from schematics.exceptions import (
    ConversionError,
    StopValidation,
    ValidationError
)
from schematics.types import (
    BaseType,
    DateTimeType as SchematicsDateTimeType,
    StringType
)


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


class PhoneNumberType(StringType):
    """ U.S. phone number validation """

    MESSAGES = {
        'convert': 'invalid U.S. phone number'
    }

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        We return a phoenumbers.PhoneNumber object so any kind
        of formatting can be trivially performed. Additionally,
        some convenient properties have been added:

            e164: string formatted '+11234567890'
            pretty: string formatted '(123) 456-7890'

        :return: phonenumbers.PhoneNumber
        """

        if isinstance(value, pn.phonenumber.PhoneNumber):
            return value

        try:
            phone = pn.parse(value, 'US')

            if not pn.is_valid_number(phone):
                raise
        except:
            raise ConversionError(self.messages['convert'])

        phone.e164 = pn.format_number(phone, pn.PhoneNumberFormat.E164)
        phone.pretty = pn.format_number(phone, pn.PhoneNumberFormat.NATIONAL)

        return phone

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        By default we convert to a str & pretty print the phone
        number.

        :return: str
        """

        if hasattr(value, 'pretty'):
            value = value.pretty

        return value


class ResourceType(BaseType):
    """ Resource type of the underlying model """

    MESSAGES = {
        'rtype': 'value must be {0}, not {1}'
    }

    def __init__(self, rtype, **kwargs):
        self.rtype = rtype

        super(ResourceType, self).__init__(**kwargs)

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


class StateType(BaseType):
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


class ZipCodeType(StringType):
    """ U.S. zip code field with validation """

    MESSAGES = {
        'zip_code': 'Invalid zip code format'
    }

    ZIPCODE_REGEX = re.compile('^[0-9]{5}(?:-[0-9]{4})?$')

    def validate_zip_code(self, value):
        """ Schematics validator """

        if not ZipCodeType.ZIPCODE_REGEX.match(value):
            raise StopValidation(self.messages['zip_code'])

        return value
