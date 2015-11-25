"""
    resources.s3_model_image
    ~~~~~~~~~~~~~~~~~~~~~~~~

    AWS S3 image upload

    Uses the base s3_model resource but defines the allowed
    mimetypes when uploading.
"""

from ..resources.s3_model import Resource as S3ModelResource


class Resource(S3ModelResource):
    """ S3 model image resource & responders """

    MIMETYPES = ('image/jpeg', 'image/png')
