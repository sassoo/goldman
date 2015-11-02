"""
    types.rid
    ~~~~~~~~~

    schematics resource id type

    This is short hand of declaring which field is the resource id
    or `rid` which commonly is the primary key of the model.

    It will show up in the API url's.
"""

from schematics.types import BaseType


class RidType(BaseType):
    """ Resource type of the underlying model """

    pass
