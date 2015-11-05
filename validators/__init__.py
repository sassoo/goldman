"""
    validators
    ~~~~~~~~~~

    All of our custom schematics type validators.
"""

from goldman.utils.str_helpers import str_to_uuid
from schematics.exceptions import ValidationError


def validate_int(value):
    """ Integer validator """

    if value:
        try:
            int(value)
        except (TypeError, ValueError):
            raise ValidationError('not a valid number')

    return value


def validate_uuid(value):
    """ UUID 128-bit validator """

    if value:
        try:
            str_to_uuid(value)
        except ValueError:
            raise ValidationError('not a valid UUID')

    return value
