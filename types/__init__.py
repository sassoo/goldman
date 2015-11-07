"""
    types
    ~~~~~

    All of our custom schematics model types.
"""

from ..types.datetime import Type as DateTimeType
from ..types.phonenumber import Type as PhoneNumberType
from ..types.resource import Type as ResourceType
from ..types.state import Type as StateType
from ..types.to_many import Type as ToManyType
from ..types.to_one import Type as ToOneType
from ..types.zipcode import Type as ZipCodeType


TYPES = [
    DateTimeType,
    PhoneNumberType,
    ResourceType,
    StateType,
    ToManyType,
    ToOneType,
    ZipCodeType,
]
