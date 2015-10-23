"""
    Psycopg2.connect
    ~~~~~~~~~~~~~~~~

    A convenience class to assist in creation of the
    psycopg2 database object.
"""

import goldman
import psycopg2
import psycopg2.extras


__all__ = ['pg']


class Connect(object):
    """ Custom database object to be initialized on falcon start """

    def __init__(self):

        self.conn = self.connect()

    @property
    def config(self):
        """ Return the configuration as needed by neo.Graph() """

        return goldman.config.PG_URL

    def connect(self):
        """ Construct the py2neo Graph instance

        This will associate the graph instance with a specific URL
        & thusly a database.

        :return: py2neo.Graph instance
        """

        conn = psycopg2.connect(
            self.config,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

        conn.set_session(autocommit=True)

        return conn


# pylint: disable=invalid-name
pg = Connect().conn
