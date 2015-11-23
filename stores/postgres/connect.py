"""
    postgres.connect
    ~~~~~~~~~~~~~~~~

    A convenience class to assist in creation of the
    psycopg2 database object.
"""

import goldman
import psycopg2
import psycopg2.extras


class Connect(object):
    """ Custom psycopg2 connection object by the start """

    def __init__(self):

        self._conn = None

    @property
    def config(self):
        """ Return the configuration as needed """

        return goldman.config.PG_URL

    def connect(self):
        """ Construct the psycopg2 connection instance

        :return: psycopg2.connect instance
        """

        if self._conn:
            return self._conn

        self._conn = psycopg2.connect(
            self.config,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

        self._conn.set_session(autocommit=True)
        psycopg2.extras.register_hstore(self._conn)

        return self._conn
