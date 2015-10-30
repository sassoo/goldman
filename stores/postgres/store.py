"""
    postgres.store
    ~~~~~~~~~~~~~~

    Interface with helper routines for persisting, finding,
    etc from a postgresql database.
"""

import goldman.exceptions as exceptions
import goldman.signals as signals

from ..base import Store as BaseStore
from ..postgres.connect import Connect
from goldman.utils.error_handlers import abort


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


conn = Connect().conn  # pylint: disable=invalid-name


class Store(BaseStore):
    """ PostgreSQL database store """

    def __init__(self):

        super(Store, self).__init__()

    @staticmethod
    def dirty_cols(model):
        """ Get the models dirty columns in a friendly SQL format

        This will be a string of comma separated field names
        prefixed by the models resource type. If no fields are
        dirty then return None

        :return: str or None
        """

        cols = ', '.join(model.dirty_fields)

        return cols or None

    @staticmethod
    def dirty_vals(model):
        """ Get the models dirty values in a friendly SQL format

        This will be a string of comma separated field
        names in a format for psycopg to substitute with
        parameterized inputs.

        An example, if the `rid` & `created` fields are
        dirty then they'll be converted into:

            '%(rid)s, %(created)s'

        :return: str or None
        """

        vals = []

        for field in model.dirty_fields:
            vals.append('%({0})s'.format(field))

        vals = ', '.join(vals)

        return vals or None

    @staticmethod
    def field_cols(model):
        """ Get the models columns in a friendly SQL format

        This will be a string of comma separated field
        names prefixed by the models resource type.

        :return: str
        """

        cols = ', '.join(model.all_fields)

        return cols or None

    @staticmethod
    def filters_query(filters):
        """ Turn the tuple of filters into SQL WHERE statements

        The key (column name) & operator have already been vetted
        so they can be trusted but the value could still be evil
        so it MUST be a parameterized input!

        That is done by creating a param dict where they key name
        & val look like:

            '{}_{}'.format(key, oper): val

        The key is constructed the way it is to ensure uniqueness,
        if we just used the key name then it could get clobbered.

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

            prop = '{0}_{1}'.format(key, oper)
            oper = FILTER_TABLE[oper]

            stmt = '{0} {1} %({2})s'.format(key, oper, prop)

            param.update({prop: val})
            stmts.append(stmt)

        if stmts:
            stmt = ' AND '.join(stmts)
            stmt = ' WHERE {0}'.format(stmt)

            return stmt, param

    @staticmethod
    def pages_query(pages):
        """ Turn the tuple of pages into a SQL LIMIT/OFFSET query """

        try:
            return ' OFFSET {0} LIMIT {1}'.format(pages[0], pages[1])
        except (IndexError, TypeError):
            return ''

    @staticmethod
    def sorts_query(sortables):
        """ Turn the Sortables into a SQL ORDER BY query """

        stmts = []

        for sortable in sortables:
            if sortable.desc:
                stmts.append('{0} DESC'.format(sortable))
            else:
                stmts.append('{0} ASC'.format(sortable))

        if stmts:
            return ' ORDER BY {0}'.format(', '.join(stmts))
        else:
            return ''

    @staticmethod
    def to_pg(model):
        """ Invoke the models to_primitive properly for pg """

        return model.to_primitive(context={'datetime_date': True})

    def create(self, model):
        """ Given a model object instance create it """

        param = self.to_pg(model)
        query = """
                INSERT INTO {table} ({dirty_cols})
                VALUES ({dirty_vals})
                RETURNING {cols};
                """

        query = query.format(
            cols=self.field_cols(model),
            dirty_cols=self.dirty_cols(model),
            dirty_vals=self.dirty_vals(model),
            table=model.rtype,
        )

        signals.pre_create.send(model.__class__, model=model)
        signals.pre_save.send(model.__class__, model=model)
        result = self.query(query, one=True, param=param)
        signals.post_create.send(model.__class__, model=model)
        signals.post_save.send(model.__class__, model=model)

        return result

    def delete(self, model):
        """ Given a model object instance delete it """

        param = self.to_pg(model)
        query = """
                DELETE FROM {table}
                WHERE rid = %(rid)s
                RETURNING {cols};
                """

        query = query.format(
            cols=self.field_cols(model),
            table=model.rtype,
        )

        signals.pre_delete.send(model.__class__, model=model)
        result = self.query(query, one=True, param=param)
        signals.post_delete.send(model.__class__, model=model)

        return result

    def find(self, model, key, val):
        """ Given a model class & a single key/val find the model

        A single instantiated model object found by the key/val
        will be returned if a match is found in the database.
        If no record can be found then return None.

        WARN: This isn't for complex queries! Use search() instead.

        :return: model or None
        """

        param = {'key': key, 'val': val}
        query = """
                SELECT {cols} FROM {table}
                WHERE %(key)s = %(val)s;
                """

        query = query.format(
            cols=self.field_cols(model),
            table=model.RTYPE,
        )

        signals.pre_find.send(model.__class__, model=model)

        value = self.query(query, one=True, param=param)
        if value:
            value = model(value)
            signals.post_find.send(value.__class__, model=value)

        return value

    def query(self, query, one=False, param=None):
        """ Perform a SQL based query

        This will abort on a failure to communicate with
        the database.

        :query: string query
        :params: parameters for the query
        :return: Record or RecordList from psycopg2
        """

        with conn.cursor() as curs:
            try:
                curs.execute(query, param)
            except BaseException as exc:
                msg = 'Error executing {0} query with params {1} ' \
                      ': {2}'.format(query, param, exc)

                print 'XXX HERE'
                print msg
                print exc.pgcode
                print dir(exc.diag)
                print type(exc.diag)
                print exc.diag.constraint_name
                print exc.diag.table_name
                abort(exceptions.DatabaseUnavailable)

            if one:
                value = curs.fetchone()
            else:
                value = curs.fetchall()

        return value

    def search(self, model, **kwargs):
        """ Search for the model by assorted criteria """

        param = {}
        pages = self.pages_query(kwargs.get('pages'))
        sorts = self.sorts_query(kwargs.get('sorts'))

        query = 'SELECT {cols} FROM {table}'.format(
            cols=self.field_cols(model),
            table=model.rtype,
        )

        filters = kwargs.get('filters')
        if filters:
            where, param = self.filters_query(filters)
            query += where

        query += sorts
        query += pages

        values = self.query(query, param=param)
        values = [model(value) for value in values]

        return values

    def update(self, model):
        """ Given a model object instance update it """

        param = self.to_pg(model)
        query = """
                UPDATE {table}
                SET ({dirty_cols}) = ({dirty_vals})
                WHERE rid = %(rid)s
                RETURNING {cols};
                """

        query = query.format(
            cols=self.field_cols(model),
            dirty_cols=self.dirty_cols(model),
            dirty_vals=self.dirty_vals(model),
            table=model.rtype,
        )

        signals.pre_update.send(model.__class__, model=model)
        signals.pre_save.send(model.__class__, model=model)
        result = self.query(query, one=True, param=param)
        signals.post_update.send(model.__class__, model=model)
        signals.post_save.send(model.__class__, model=model)

        return result
