"""
    utils.s3_helpers
    ~~~~~~~~~~~~~~~~

    Common helpers for interacting with AWS S3

    These interfaces are mostly used by our S3 resource &
    responders but any app could use these as well.
"""

import time

from base64 import b64decode
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from flask import abort, current_app as app, g, request
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = ['gif', 'jpeg', 'jpg', 'png']


def connect():
    config = app.config['S3_SETTINGS']

    return S3Connection(config['key'], config['secret'])

def ext_to_content_type(ext):
    if ext in ['jpeg', 'jpg']:
        return 'image/jpeg'
    else:
        return 'image/%s' % ext

def gen_url(key):
    """ Given a key generate the S3 url

    We do this to avoid a round-trip to the S3 API. This function may not
    scale well for the complexities of future S3 interactions so be mindful.

    Args:
        key: S3 key as generated in our upload() function

    Returns:
        A string URL to the object
    """
    bucket = app.config['S3_SETTINGS']['bucket']

    return '//s3.amazonaws.com/%s/%s' % (bucket, key)

def s3_upload(bucket, content, content_type, acl='public-read', prefix=None):
    """ Store an object in our an S3 bucket.

    Key is only the portion of the S3 key that can't be auto
    determined. It will be concatenated with our standard S3
    key prefix/suffix which include the relative s3 URL,
    bucket name, & high precision timestamp.

    It will look like:
        //<s3 url>/<bucket>/<prefix>/<timestamp>.<extension>

    :param acl:
        S3 ACL for the object
    :param bucket:
        S3 bucket to upload to
    :param content:
        a string representation of the object to upload
    :param content_type:
        a string MIMETYPE of the object that S3 should
        be informed of
    :param prefix:
        an object specific portion of the S3 key name
        to be concatenated with the value of S3_URL

    :raise:
        IOError on any failure
    :return:
        S3 generated URL of the uploaded object
    """

    conn = connect()
    bucket = conn.get_bucket(bucket)

    # obj is the object that will be uploaded to S3
    obj = Key(bucket)
    obj.content_type = content_type

    # Create the name of the object in S3. It is prefixed with the company ID
    # followed by '/' & the key name provided to this function. Lastly, the
    # extension is appended & a high precision timestamp. We include slashes so
    # it's easier to navigate in the S3 web console
    obj.key = '%s/%s-%s.%s' % (str(g.login.company.id), key,
                               '%.5f' % time.time(), extension)

    obj.set_contents_from_string(content)
    obj.set_acl(acl)

    return gen_url(obj.key)
