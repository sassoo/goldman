"""
    types.rid
    ~~~~~~~~~

    schematics resource id type

    This is short hand of declaring which field is the resource id
    or `rid` which commonly is the primary key of the model.

    It will show up in the API url's as the unique key representing
    a single unique resource in the store.
"""

from schematics.types import BaseType


class Type(BaseType):
    """ Resource type of the underlying model """

    pass
