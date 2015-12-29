"""
    extensions
    ~~~~~~~~~~

    Define asome constants for different mimetypes
"""


EXTENSION_TABLE = {
    'image/gif': 'gif',
    'image/jpeg': 'jpeg',
    'image/jpg': 'jpg',
    'image/png': 'png',
}


def get(content_type):
    """ Return the string extension from content-type """

    return EXTENSION_TABLE.get(content_type)
