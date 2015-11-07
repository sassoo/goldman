"""
    types.rid
    ~~~~~~~~~

    schematics resource id type

    This is short hand for declaring which field is the resource id
    or `rid` which commonly is the primary key of the model.

    It will show up in the API url's as the unique key representing
    a single unique resource in the store. It's typeness wil be
    validated against incoming requests.
"""

from schematics.types import StringType


class Type(StringType):
    """ Resource type of the underlying model """

    def __init__(self, typeness=int, **kwargs):

        super(Type, self).__init__(**kwargs)

        self.typeness = typeness
