"""
    models.common
    ~~~~~~~~~~~~~

    Many applications that use our model based resources &
    stores have a few common types across all there models.

    This model can be sub-classed to include those common
    types.
"""

from goldman.types import DateTimeType, ToOneType
from goldman.utils.url_helpers import url_for_model
from schematics.types import StringType


__all__ = ['Model']


class Model(object):
    """ Model with some common schematics types """

    creator = ToOneType(
        from_rest=False,
        rtype='logins',
    )

    created = DateTimeType(from_rest=False)
    updated = DateTimeType(from_rest=False)

    uuid = StringType(
        from_rest=False,
        unique=True
    )

    @property
    def location(self):
        """ Return a string relative URL of the model """

        rtype = getattr(self, 'rtype')

        return url_for_model(rtype, self.uuid)
