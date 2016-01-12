"""
    resources.s3
    ~~~~~~~~~~~~

    AWS S3 object wrangling resource

    Currently, a multipart/form-data file upload is expected
    on POST.
"""

import falcon
import goldman
import goldman.signals as signals
import time

from ..resources.base import Resource as BaseResource
from goldman.exceptions import ServiceUnavailable
from goldman.utils.error_helpers import abort
from goldman.utils.responder_helpers import find
from goldman.utils.s3_helpers import s3_connect, s3_upload


class Resource(BaseResource):
    """ S3 resource & responders """

    MIMETYPES = []

    DESERIALIZERS = [
        goldman.FormDataDeserializer,
    ]

    SERIALIZERS = [
        goldman.JsonSerializer,
    ]

    def __init__(self, model, **kwargs):

        self.model = model
        self.mimetypes = kwargs.get('mimetypes', self.MIMETYPES)

        # s3 properties
        self.acl = kwargs.get('acl', 'public-read')
        self.bucket = kwargs.get('bucket', goldman.config.S3_BUCKET)
        self.key = kwargs.get('key', goldman.config.S3_KEY)
        self.secret = kwargs.get('secret', goldman.config.S3_SECRET)

        if not self.bucket:
            raise NotImplementedError('an S3 bucket is required')
        super(Resource, self).__init__()

    @property
    def _s3_rtype(self):
        """ Return the chunk after the last / in the URL

        This will be used to generate the path in S3 & should be
        something stable to group the related objects.
        """

        return goldman.sess.req.path.split('/')[-1]

    def _gen_s3_path(self, model, props):
        """ Return the part of the S3 path based on inputs

        The path will be passed to the s3_upload method &
        will ultimately be merged with the standard AWS S3
        URL.

        An example model type of 'users' with a resource ID
        of 99 & an API endpoint ending with 'photos' will have
        a path generated in the following way:

            users/99/photos/<timestamp>.<extension>

        The timestamp is a high precision timestamp & the
        extension is typically 3 characters & derived in
        the form-data deserializer.
        """

        now = '%.5f' % time.time()

        return '%s/%s/%s/%s.%s' % (model.rtype, model.rid_value,
                                   self._s3_rtype, now, props['file-ext'])

    def on_post(self, req, resp, rid):
        """ Deserialize the file upload & save it to S3

        File uploads are associated with a model of some
        kind. Ensure the associating model exists first &
        foremost.
        """

        signals.responder_pre_any.send(self.model)
        signals.responder_pre_upload.send(self.model)

        props = req.deserialize(self.mimetypes)
        model = find(self.model, rid)

        signals.pre_upload.send(self.model, model=model)

        try:
            conn = s3_connect(self.key, self.secret)
            path = self._gen_s3_path(model, props)
            s3_url = s3_upload(self.acl, self.bucket, conn, props['content'],
                               props['content-type'], path)
        except IOError:
            abort(ServiceUnavailable(**{
                'detail': 'The upload attempt failed unexpectedly',
            }))

        signals.post_upload.send(self.model, model=model, url=s3_url)

        resp.location = s3_url
        resp.status = falcon.HTTP_201

        resp.serialize({'data': {'url': s3_url}})

        signals.responder_post_any.send(self.model)
        signals.responder_post_upload.send(self.model)
