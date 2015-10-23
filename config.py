"""
    config
    ~~~~~~

    Initialize some of our helpful constants used throughout
    the api & merge them with an app specific overrides.
"""

import importlib
import os


class Config(object):
    """ Default configuration settings.

    To override any these configurations define the env
    variable 'GOLDMAN_CONFIG_MODULE' & ensure the module
    is in the python path.

    Any directives beginning with '_' will be considered
    private & not attached to the Config object.
    """

    # Content-Types
    CSV_MIMETYPE = 'text/csv'
    FILEUPLOAD_MIMETYPE = 'multipart/form-data'
    JSON_MIMETYPE = 'application/json'
    JSONAPI_MIMETYPE = 'application/vnd.api+json'

    # JSON API
    JSONAPI_VERSION = '1.0'

    # Query filter operators
    BOOL_FILTERS = ('exists',)
    DATE_FILTERS = ('after', 'before')
    GEO_FILTERS = ('geo_near', 'geo_within')
    LIST_FILTERS = ('in', 'nin')
    NUM_FILTERS = ('gt', 'gte', 'len', 'lt', 'lte')
    STR_FILTERS = ('contains',)

    QUERY_FILTERS = BOOL_FILTERS + DATE_FILTERS + GEO_FILTERS + \
        LIST_FILTERS + NUM_FILTERS + STR_FILTERS

    # Query pagination
    PAGE_LIMIT = 10

    # Query sort preference
    SORT = 'created'

    # URL prefix for the API
    BASE_URL = '/api'

    # WWW-Authenticate
    AUTH_REALM = 'JSON API'

    def __init__(self):

        try:
            module = os.environ.get('GOLDMAN_CONFIG_MODULE', '')
            module = importlib.import_module(module)
        except (ImportError, ValueError):
            module = None

        if module:
            for attr in dir(module):
                if not attr.startswith('_'):
                    val = getattr(module, attr)

                    setattr(self, attr, val)

    def __getattr__(self, name):
        """ Return None if the attr isn't found

        Instead of throwing an exception if the attribute isn't
        found like python would ordinarily do & forcing each access
        to guard against... we conveniently return None.
        """

        try:
            return getattr(self, name)
        except AttributeError:
            return None
