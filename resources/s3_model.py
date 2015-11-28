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
import time

from ..resources.base import Resource as BaseResource
from goldman.utils.error_helpers import abort
from goldman.utils.responder_helpers import find
from goldman.utils.s3_helpers import s3_upload


class Resource(BaseResource):
    """ S3 resource & responders """

    MIMETYPES = []

    DESERIALIZERS = [
        goldman.FormDataDeserializer,
    ]

    SERIALIZERS = [
        goldman.JSONSerializer,
    ]

    def __init__(self, model, **kwargs):

        self.model = model
        self.mimetypes = kwargs.get('mimetypes', self.MIMETYPES)

        # s3 properties
        self.bucket = kwargs.get('bucket', goldman.config.S3_BUCKET)
        self.key = kwargs.get('key', goldman.config.S3_KEY)
        self.secret = kwargs.get('secret', goldman.config.S3_SECRET)

        if not self.bucket:
            raise NotImplementedError('an S3 bucket is required')

        super(Resource, self).__init__()

    @property
    def s3_rtype(self):
        """ Return the chunk after the last / in the URL

        This will be used to generate the path in S3 & should be
        something stable to group the related objects.
        """

        return goldman.sess.req.path.split('/')[-1]

    def _gen_s3_path(self, model):

        high_time = '%.5f' % time.time()

        return '%s/%s/%s/%s.%s' % (model.rtype, model.rid_value, self.s3_rtype,
                                   high_time, extension)

    def on_post(self, req, resp, rid):
        """ Deserialize the file upload & save it to S3

        File uploads are associated with a model of some
        kind. Ensure the associating model exists first &
        foremost.
        """

        s3_rtype = req.path.split('/')[-1]

        signals.responder_pre_any.send(self.model)
        signals.responder_pre_upload.send(self.model, s3_rtype=s3_rtype)

        props = req.deserialize(self.mimetypes)
        model = find(self.model, rid)

        print props
        try:
            s3_url = s3_upload(self.bucket, self.key, self.secret, **props)
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
