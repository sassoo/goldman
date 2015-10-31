"""
    validators
    ~~~~~~~~~~

    All of our custom schematics type validators.
"""

from goldman.utils.str_helpers import str_to_uuid
from schematics.exceptions import ValidationError


def validate_uuid(value):
    """ Schematics validator """

    if value:
        try:
            str_to_uuid(value)
        except ValueError:
            raise ValidationError('invalid UUID syntax')

    return value
