"""
    Py2neo.store
    ~~~~~~~~~~~~

    Interface with helper routines for persisting, finding,
    etc from a neo4j database.
"""

import app.exceptions as exceptions
import app.ext.Py2neo as neo
import app.params as params

from app.utils.error_helpers import abort


FILTER_TABLE = {
    'eq': '=',
    'gt': '>',
    'lt': '<',
    'ne': '<>',
    'gte': '>=',
    'lte': '<=',

    'after': '>',
    'before': '<',
}


def filters_query(filters):
    """ Turn the tuple of filters into neo4j WHERE statements

    The key (column name) & operator have already been vetted
    so they can be trusted but the value could still be evil
    so it MUST be a parameterized input!

    That is done by creating a param dict where they key name
    & val look like:

        '{}_{}'.format(key, oper): val

    The key is constructed the way it is to ensure uniqueness,
    if we just used the key name then it could be clobbered.

    Ultimately the WHERE statement will look something lik:

        age >= {age_gte}

    where age_gte is the key name in the param dict with a
    value of the evil user input. In the end, a string
    statement & dict param are returned as a tuple if any
    filters were provided otherwise None.

    :return: tuple (string, dict)
    """

    param = {}
    stmts = []

    for filtr in filters:
        key, oper, val = filtr

        prop = '{}_{}'.format(key, oper)
        oper = FILTER_TABLE[oper]

        predicate = '{0} {1} {{{2}}}'.format(key, oper, prop)
        statement = 'WHERE n.' + predicate

        param.update({prop: val})
        stmts.append(statement)

    stmt = ' AND '.join(stmts)

    return stmt, param


def pages_query(pages):
    """ Turn the tuple of pages into a neo4j SKIP/LIMIT query """

    if not pages:
        pages = (0, params.PAGE_LIMIT)

    return 'SKIP {0} LIMIT {1}'.format(pages[0], pages[1])


def sorts_query(sorts):
    """ Turn the tuple of sorts into a neo4j ORDER BY query """

    stmts = []

    if not sorts:
        sorts = (params.SORT,)

    for sort in sorts:
        if sort.startswith('-'):
            stmts.append('n.{} DESC'.format(sort))
        else:
            stmts.append('n.{}'.format(sort))

    return ' ORDER BY {}'.format(', '.join(stmts))


class Store(object):
    """ neo4j graph database store """

    @staticmethod
    def query(query, one=False, param=None):
        """ Perform a cypher based query

        This will abort on a failure to communicate with
        the database.

        :query: string query
        :params: parameters for the query
        :return: Record or RecordList from py2neo
        """

        if one:
            exe = neo.cypher.execute_one
        else:
            exe = neo.cypher.execute

        try:
            value = exe(query, parameters=param)
        except BaseException as exc:
            msg = 'Error executing {0} query with params {1} ' \
                  ': {2}'.format(query, param, exc)

            print msg
            abort(exceptions.DatabaseUnavailable)

        return value

    def create(self, model):
        """ Given a model object instance create it """

        param = {'param': self.to_neo(model)}
        query = """
                CREATE (n:{table})
                SET n = {param}
                RETURN n
                """

        query = query.format(
            table=model.rtype,
        )

        return self.query(query, one=True, param=param)

    def find(self, model, uuid):
        """ Given a model object & uuid find the node

        An instantiated model object found by rtype value
        will be returned if a match is found in the database.
        If no record can be found the return None.

        :return: model or None
        """

        param = {'uuid': uuid}
        query = """
                MATCH (n:%s {uuid: {uuid}})
                RETURN n
                """ % model.rtype

        value = self.query(query, one=True, param=param)

        if value:
            value = model(value.properties)

        return value

    def search(self, model, **kwargs):
        """ Search for the model by assorted criteria """

        param = {}
        pages = pages_query(kwargs.get('pages'))
        sorts = sorts_query(kwargs.get('sorts'))

        query = 'MATCH (n:{})'.format(model.rtype)

        filters = kwargs.get('filters')
        if filters:
            where, param = filters_query(filters)
            query += ' {}'.format(where)

        query += sorts
        query += ' WITH n {}'.format(pages)
        query += ' RETURN n'

        values = self.query(query, param=param)
        values = [model(value.n.properties) for value in values]

        return values

    @staticmethod
    def to_neo(model):
        """ Invoke the models to_primitive properly for neo4j """

        return model.to_primitive(context={'epoch_date': True})
