"""
    utils.s3_helpers
    ~~~~~~~~~~~~~~~~

    Common helpers for interacting with AWS S3

    These interfaces are mostly used by our S3 resource &
    responders but any app could use these as well.
"""

from boto.s3.connection import S3Connection
from boto.s3.key import Key


def gen_url(bucket, path):
    """ Given a path generate the S3 url

    We do this to avoid a round-trip to the S3 API. This
    function may not scale well for the complexities of
    future S3 interactions so be mindful.

    :param key:
        S3 key as generated in our upload() function

    :return:
        A string URL to the object
    """

    return 'https://s3.amazonaws.com/%s/%s' % (bucket, path)


def s3_connect(key, secret):
    """ Create an S3 connection object using boto """

    return S3Connection(key, secret)


# pylint: disable=too-many-arguments
def s3_upload(acl, bucket, conn, content, content_type, path):
    """ Store an object in our an S3 bucket.

    :param acl:
        S3 ACL for the object
    :param bucket:
        S3 bucket to upload to
    :param content:
        a string representation of the object to upload
    :param content_type:
        a string MIMETYPE of the object that S3 should
        be informed of
    :param path:
        an object specific portion of the S3 key name
        to be passed to gen_url to generate the the location
        in S3 of the new object

    :raise:
        IOError on any failure
    :return:
        S3 generated URL of the uploaded object
    """

    # obj is the object that will be uploaded
    obj = Key(conn.get_bucket(bucket))
    obj.content_type = content_type
    obj.key = path

    obj.set_contents_from_string(content)
    obj.set_acl(acl)

    return gen_url(bucket, path)
