"""
    models.default_schema
    ~~~~~~~~~~~~~~~~~~~~~

    Using the default_schema assumes a few things:

        * the API uses authentication
        * each model has a creator field defaulting to the
          logged in user that created the model
        * each model has timestamp fields for create / update

    It will also use the goldman BaseModel as is required on
    all models if using a goldman store.
"""

import goldman
import goldman.signals as signals

from ..models.base import Model as BaseModel
from datetime import datetime as dt
from goldman.types import DateTimeType, ToOneType
from schematics.types import IntType


class Model(BaseModel):
    """ Model with some common schematics types """

    creator = ToOneType(
        from_rest=False,
        rtype='logins',
        skip_exists=True,
    )

    created = DateTimeType(from_rest=False)
    updated = DateTimeType(from_rest=False)

    rid = IntType(
        from_rest=False,
        rid=True,
    )


# pylint: disable=unused-argument
def pre_create(sender, model):
    """ Callback before creating any new model

    Identify the creator of the new model & set the
    created timestamp to now.
    """

    model.created = dt.utcnow()
    model.creator = goldman.sess.login


def pre_save(sender, model):
    """ Callback before saving any model

    Update the updated timestamp to now.
    """

    model.updated = dt.utcnow()


signals.pre_create.connect(pre_create)
signals.pre_save.connect(pre_save)
