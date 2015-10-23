"""
    models.base
    ~~~~~~~~~~~

    Our base model for sub-classing.
"""

from goldman.ext.Schematics.model import Model as BaseSchematicsModel
from goldman.ext.Schematics.types import DateTimeType, ToOneType
from goldman.utils.url_helpers import url_for_model
from schematics.types import StringType


class Model(BaseSchematicsModel):
    """ Base model to be extended by the database mixins """

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

    """
    Model creation methods
    """

    # pylint: disable=unused-argument
    def acl_create(self, login):
        """ ACL callback check during model creation """

        return True

    def pre_create(self):
        """ Callback before creating a new model """

        pass

    def post_create(self):
        """ Callback after creating a new model """

        pass

    """
    Model deletion methods
    """

    # pylint: disable=unused-argument
    def acl_delete(self, login):
        """ ACL callback check during model creation """

        return True

    def pre_delete(self):
        """ Callback before deleting an existing model """

        pass

    def post_delete(self):
        """ Callback after deleting an existing model """

        pass

    """
    Model finding methods
    """

    def acl_find(self, login):
        """ ACL callback check during model finding """

        return True

    """
    Model save methods
    """

    def acl_save(self, login):
        """ ACL callback check during any model save """

        return True

    def pre_save(self):
        """ Callback before saving any model """

        pass

    def post_save(self):
        """ Callback after saving any model """

        pass

    """
    Model update methods
    """

    def acl_update(self, login):
        """ ACL callback check during model modification """

        return True

    def pre_update(self):
        """ Callback before updating an existing model """

        pass

    def post_update(self):
        """ Callback after updating an existing model """

        pass
