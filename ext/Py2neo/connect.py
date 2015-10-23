"""
    Py2neo.connect
    ~~~~~~~~~~~~~~

    A convenience class to assist in creation of the py2neo
    graph object. The graph object is assigned to the neo
    variable & can be used throughout the application.
"""

import app.config
import py2neo


__all__ = ['cypher', 'graph']


class Connect(object):
    """ Custom database object to be initialized on falcon start """

    def __init__(self):

        self.graph = self.connect()

    @property
    def config(self):
        """ Return the configuration as needed by neo.Graph() """

        return app.config.NEO_URL

    def connect(self):
        """ Construct the py2neo Graph instance

        This will associate the graph instance with a specific URL
        & thusly a database.

        :return: py2neo.Graph instance
        """

        return py2neo.Graph(self.config)


# pylint: disable=invalid-name
neo = Connect()
graph = neo.graph
cypher = graph.cypher
