"""
    resources.s3
    ~~~~~~~~~~~~

    AWS S3 object wrangling resource

    Currently, a multipart/form-data file upload is expected
    on POST.
"""

import falcon
import goldman
import goldman.exceptions as exceptions
import goldman.signals as signals

from ..resources.base import Resource as BaseResource
from goldman.utils.error_helpers import abort
from goldman.utils.responder_helpers import find
from goldman.utils.s3_helpers import s3_upload


class Resource(BaseResource):
    """ S3 resource & responders """

    DESERIALIZERS = [
        goldman.FormDataDeserializer,
    ]

    SERIALIZERS = [
        goldman.JSONSerializer,
    ]

    def __init__(self, model, bucket=None, mimetypes=None):

        self.model = model
        self.bucket = bucket or goldman.config.get('S3_BUCKET')
        self.mimetypes = mimetypes or getattr(self, 'MIMETYPES', ())

        if not bucket:
            raise NotImplementedError('an S3 bucket is required')

        super(Resource, self).__init__()

    def on_post(self, req, resp, rid):
        """ Deserialize the file upload & save it to S3

        File uploads are associated with a model of some
        kind. Ensure the associating model exists first &
        foremost.
        """

        s3_rtype = req.path.split('/')[-1]

        signals.responder_pre_any.send(self.model)
        signals.responder_pre_upload.send(self.model, s3_rtype=s3_rtype)

        props = req.deserialize(self.mimetypes)  # return content(-type)
        model = find(self.model, rid)

        try:
            s3_url = s3_upload(self.bucket, **props)
        except IOError:
            abort(exceptions.ServiceUnavailable(**{
                'detail': 'The upload attempt failed unexpectedly',
            }))

        resp.location = s3_url
        resp.status = falcon.HTTP_201

        resp.serialize({'data': {'url': s3_url}})

        signals.responder_post_any.send(self.model)
        signals.responder_post_upload.send(self.model, model=model,
                                           s3_rtype=s3_rtype, s3_url=s3_url)
