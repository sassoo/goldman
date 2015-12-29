# Goldman

Goldman is an opinionated WSGI framework built on [Falcon](https://github.com/falconry/falcon) with batteries included.

It is [JSON API 1.0](http://jsonapi.org/format/) compliant & most compliments a [CRUD+L](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) type application currently using a postgres database (referred to as a store), however additional stores are on the roadmap. The framework can be used simply by defining your models with validations & you automatically get:

 * Content negotiation
 * JSON API query parameters including pagination
 * Model based routing
 * Serialization / Deserialization to & from REST endpoints
 * Serialization / Deserialization to & from the store
 * signalling using [Blinker](https://github.com/jek/blinker)
 * much much more

### Resource Examples:

Need some examples? How about a few resources like an American & their Truck, you would define your resources like:

```python
import goldman

from app.models import American, Truck


class API(goldman.API):
    """ Subclass the goldman.API object & define resources """

    RESOURCES = [
        goldman.ModelResource(Truck),
        goldman.ModelsResource(Truck),
        goldman.RelatedResource(Truck),

        goldman.ModelResource(American),
        goldman.ModelsResource(American),
        goldman.RelatedResource(American),
    ]
```

The above creates API end points supporing all CRUD+L type operations for the American & Truck models. This includes complex query parameters as documented in the JSON API specification. Pagination as well. The `goldman.RelatedResource` is for handling a models relationships if present.

### Model Examples:

To define a model we leverage & extend the awesome [Schematics](https://github.com/schematics/schematics) framework for serialization/deserialization & validation. This is different than (de)serialization over the wire which goldman does as well. From the same examples above the models could look like:

```python

import goldman

from goldman.types import PhoneNumberType, ResourceType, ToManyType, ToOneType
from schematics.types import BooleanType, IntType, StringType


class American(goldman.BaseModel):
    """ American model """

    RTYPE = 'americans'

    """
    The attrs below are the models fields
    """
    
    rid = IntType(
        from_rest=False,
        rid=True,
    )
    rtype = ResourceType(RTYPE)

    first_name = StringType(
        max_length=150,
        required=True,
    )
    last_name = StringType(
        max_length=150,
        required=True,
    )

    balding = BooleanType(default=True)
    loves_freedom = BooleanType(default=True)
    weight = IntType(min_value=250)
    
    # relationships
    trucks = ToManyType(
        field='owner',
        rtype='trucks',
    )
    
    
class Truck(goldman.BaseModel):
    """ Truck model """

    RTYPE = 'trucks'

    """
    The attrs below are the models fields
    """
    
    rid = IntType(
        from_rest=False,
        rid=True,
    )
    rtype = ResourceType(RTYPE)
    
    color = StringType(required=True)
    mpg = IntType(max_value=10)
    
    truck_bed_for_lovin = BooleanType(default=True)
    
    # relationships
    owner = ToOneType(rtype='americans')
```


The models fields will be cast to the appropriate data types for extra business logic, storage, & transport over the wire. Additionally, validations will be run with JSON API compliant exceptions. An enormous amount of work has been done to ensure strong exception handling with meaningful errors.

### Stuff used to make this:

 * [Faclon](https://github.com/falconry/falcon) core WSGI capability
 * [Psycopg2](http://initd.org/psycopg/) for postgres integration
 * [Blinker](https://github.com/jek/blinker) for signalling events
 * [Schematics](http://codemirror.net/) for the awesome object schema layer with validations & a bunch more
 * [Python-PhoneNumbers](https://github.com/daviddrysdale/python-phonenumbers) for phone number validations
 * [Python-US](https://github.com/unitedstates/python-us) for state validations
