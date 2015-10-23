"""
    resources.related
    ~~~~~~~~~~~~~~~~~

    Related resource object(s) with responders.

    Get the to-one or to-many relationship by name (related)
    of the model.
"""

from app.resources.base import Resource as BaseResource


class Resource(BaseResource):
    """ Related item(s) resource & responders """

    def __init__(self, model):

        super(Resource, self).__init__()

        self.model = model

    def on_get(self, req, resp, uuid, related):
        """ Find the model by id & serialize it back

        We return a 404 if the model can't be found.
        """

        related = self.model.find_related(uuid, related)

        related.acl_get(req.login)
        resp.serialize(related)
