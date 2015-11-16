"""
    stores.base
    ~~~~~~~~~~~

    Base store object.

    This should be sub-classed by other backend specific
    stores. The base store is used as an identity map & caching
    interface.
"""


class Cache(object):
    """ A very simple dictionary cache

    This can be used to store any arbitrary data within the
    context of a single request.
    """

    def __init__(self):

        self._cache = {}

    def get(self, key, bucket):
        """ Get a cached item by key

        If the cached item isn't found the return None.
        """

        try:
            return self._cache[bucket][key]
        except (KeyError, TypeError):
            return None

    def set(self, key, val, bucket):
        """ Set a cached item by key

        WARN: Regardless if the item is already in the cache,
              it will be udpated with the new value.
        """

        if bucket not in self._cache:
            self._cache[bucket] = {}

        self._cache[bucket][key] = val


class Store(object):
    """ Base resource class """

    def __init__(self):

        self.cache = Cache()

    def create(self, model):
        """ Create a new model """

        raise NotImplementedError

    def delete(self, model):
        """ Create an existing model """

        raise NotImplementedError

    def find(self, model, key, val):
        """ Find an existing model """

        raise NotImplementedError

    def query(self, query, param=None):
        """ Perform a store based query """

        raise NotImplementedError

    def search(self, model, **kwargs):
        """ Search for specific kinds of models """

        raise NotImplementedError

    def update(self, model):
        """ Modify an existing model """

        raise NotImplementedError
