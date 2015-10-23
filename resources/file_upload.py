"""
    resources.file_upload
    ~~~~~~~~~~~~~~~~~~~~~

"""

from app.resources.base import Resource as BaseResource


class Resource(BaseResource):
    """ File upload resource & responders """

    def __init__(self, model, **kwargs):
        self.callback = kwargs.get('callback', None)
        self.key = kwargs.get('key', None)
        self.model = model
