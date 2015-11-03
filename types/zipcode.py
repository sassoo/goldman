"""
    types.zipcode
    ~~~~~~~~~~~~~

    schematics zip code type
"""

import re

from schematics.exceptions import StopValidation
from schematics.types import StringType


class Type(StringType):
    """ U.S. zip code field with validation """

    MESSAGES = {
        'zip_code': 'Invalid zip code format'
    }

    ZIPCODE_REGEX = re.compile('^[0-9]{5}(?:-[0-9]{4})?$')

    def validate_zip_code(self, value):
        """ Schematics validator """

        if not Type.ZIPCODE_REGEX.match(value):
            raise StopValidation(self.messages['zip_code'])

        return value
