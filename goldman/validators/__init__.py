"""
    validators
    ~~~~~~~~~~

    Adhoc custom schematics type validators to be shared
    across any models or types.
"""

from schematics.exceptions import ValidationError
from uuid import UUID


def validate_int(value):
    """ Integer validator """

    if value and not isinstance(value, int):
        try:
            int(str(value))
        except (TypeError, ValueError):
            raise ValidationError('not a valid number')
    return value


def validate_uuid(value):
    """ UUID 128-bit validator """

    if value and not isinstance(value, UUID):
        try:
            return UUID(str(value), version=4)
        except (AttributeError, ValueError):
            raise ValidationError('not a valid UUID')
    return value
