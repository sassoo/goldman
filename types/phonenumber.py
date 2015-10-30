"""
    types.phonenumber
    ~~~~~~~~~~~~~~~~~

    schematics united states phone number type
"""

import phonenumbers as pn

from schematics.exceptions import ConversionError
from schematics.types import BaseType


class PhoneNumberType(BaseType):
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
