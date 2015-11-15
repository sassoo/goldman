"""
    postgres.store
    ~~~~~~~~~~~~~~

    Interface with helper routines for persisting, finding,
    etc from a postgresql database.
"""

import goldman
import goldman.exceptions as exceptions
import goldman.signals as signals

from ..base import Store as BaseStore
from ..postgres.connect import Connect
from goldman.queryparams.filter import FilterOr, FilterRel
from goldman.queryparams.sort import Sortable
from goldman.utils.error_handlers import abort
from goldman.utils.model_helpers import rtype_to_model


CONNECT = Connect()


ERRORS_TABLE = {
    '42883': 'One or more of the query filters had an unexpected value '
             'that could not be processed. This is a rare scenario & '
             'it is unclear which field has the issue. Please review '
             'your filters for any irregularities.',
}


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


def handle_exc(exc):
    """ Given a database exception determine how to fail

    Attempt to lookup a known error & abort on a meaningful
    error. Otherwise issue a generic DatabaseUnavailable exception.

    :param exc: psycopg2 exception
    """

    err = ERRORS_TABLE.get(exc.pgcode)

    if err:
        abort(exceptions.InvalidQueryParams(**{
            'detail': err,
            'parameter': 'filter',
        }))

    abort(exceptions.DatabaseUnavailable)


class Store(BaseStore):
    """ PostgreSQL database store """

    def __init__(self):

        self.conn = CONNECT.connect()

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

        TIP: to_manys are not located on the table in Postgres
             & are instead application references, so any reference
             to there column names should be pruned!

        :return: str
        """

        to_many = model.to_many
        cols = [f for f in model.all_fields if f not in to_many]
        cols = ', '.join(cols)

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

        Ultimately the WHERE statement will look something like:

            age >= {age_gte}

        where age_gte is the key name in the param dict with a
        value of the evil user input. In the end, a string
        statement & dict param are returned as a tuple if any
        filters were provided otherwise None.

        :return: tuple (string, dict)
        """

        def _filter(filtr):
            """ Process each individual Filter object """

            oper = FILTER_TABLE[filtr.oper]
            prop = '{field}_{oper}'.format(
                field=filtr.field.replace('.', '_'),
                oper=filtr.oper,
            )

            if isinstance(filtr, FilterRel):
                stmt = _filter_rel(filtr, oper, prop)
            else:
                stmt = '{field} {oper} %({prop})s'.format(
                    field=filtr.field,
                    oper=oper,
                    prop=prop,
                )

            return stmt, {prop: filtr.val}

        def _filter_or(filters):
            """ Given a FilterOr object return a SQL query """

            param = {}
            stmts = []

            for filtr in filters:
                vals = _filter(filtr)

                param.update(vals[1])
                stmts.append(vals[0])

            stmt = ' OR '.join(stmts)
            stmt = '({})'.format(stmt)

            return stmt, param

        def _filter_rel(rel, oper, prop):
            """ Given a FilterRel object return a SQL sub query """

            stmt = """
                   {local_field} = (SELECT {foreign_field} FROM {foreign_rtype}
                                    WHERE {foreign_filter} {oper} %({prop})s)
                   """

            return stmt.format(
                foreign_field=rel.foreign_field,
                foreign_filter=rel.foreign_filter,
                foreign_rtype=rel.foreign_rtype,
                local_field=rel.local_field,
                oper=oper,
                prop=prop,
            )

        param = {}
        stmts = []

        for filtr in filters:
            if isinstance(filtr, FilterOr):
                vals = _filter_or(filtr)
            else:
                vals = _filter(filtr)

            param.update(vals[1])
            stmts.append(vals[0])

        if stmts:
            stmt = ' AND '.join(stmts)
            stmt = ' WHERE ' + stmt

        return stmt, param

    @staticmethod
    def pages_query(pages):
        """ Turn the tuple of pages into a SQL LIMIT/OFFSET query """

        try:
            return ' OFFSET {0} LIMIT {1}'.format(pages.offset, pages.limit)
        except AttributeError:
            return ''

    @staticmethod
    def sorts_query(sortables):
        """ Turn the Sortables into a SQL ORDER BY query """

        stmts = []

        for sortable in sortables:
            if sortable.desc:
                stmts.append('{} DESC'.format(sortable.field))
            else:
                stmts.append('{} ASC'.format(sortable.field))

        return ' ORDER BY {}'.format(', '.join(stmts))

    @staticmethod
    def to_pg(model):
        """ Invoke the models to_primitive properly for pg """

        return model.to_primitive(context={
            'datetime_date': True,
            'rel_ids': True,
        })

    def create(self, model):
        """ Given a model object instance create it """

        signals.pre_create.send(model.__class__, model=model)
        signals.pre_save.send(model.__class__, model=model)

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

        result = self.query(query, param=param)

        signals.post_create.send(model.__class__, model=model)
        signals.post_save.send(model.__class__, model=model)

        return model.merge(result[0], clean=True)

    def delete(self, model):
        """ Given a model object instance delete it """

        signals.pre_delete.send(model.__class__, model=model)

        param = {'rid_value': self.to_pg(model)[model.rid_field]}
        query = """
                DELETE FROM {table}
                WHERE {rid_field} = %(rid_value)s
                RETURNING {cols};
                """

        query = query.format(
            cols=self.field_cols(model),
            rid_field=model.rid_field,
            table=model.rtype,
        )

        result = self.query(query, param=param)

        signals.post_delete.send(model.__class__, model=model)

        return result

    def find(self, rtype, key, val):
        """ Given a resource type & a single key/val find the model

        A single instantiated model object found by the key/val
        will be returned if a match is found in the database.
        If no record can be found then return None.

        WARN: This isn't for complex queries! Use search() instead.

        :return: model or None
        """

        model = rtype_to_model(rtype)
        param = {'key': key, 'val': val}
        query = """
                SELECT {cols} FROM {table}
                WHERE {key} = %(val)s;
                """

        query = query.format(
            cols=self.field_cols(model),
            key=key,
            table=rtype,
        )

        signals.pre_find.send(model.__class__, model=model)

        result = self.query(query, param=param)
        if result:
            result = model(result[0])
            signals.post_find.send(model.__class__, model=result)

        return result

    def query(self, query, param=None):
        """ Perform a SQL based query

        This will abort on a failure to communicate with
        the database.

        :query: string query
        :params: parameters for the query
        :return: RecordList from psycopg2
        """

        with self.conn.cursor() as curs:
            print 'XXX QUERY', query
            try:
                curs.execute(query, param)
            except BaseException as exc:
                msg = 'query: {}, param: {}, exc: {}'.format(query, param, exc)

                if hasattr(exc, 'pgcode'):
                    msg = '{}, exc code: {}'.format(msg, exc.pgcode)

                print msg
                handle_exc(exc)

            results = curs.fetchall()

        return results

    def search(self, rtype, **kwargs):
        """ Search for the model by assorted criteria """

        model = rtype_to_model(rtype)
        param = {}
        pages = self.pages_query(kwargs.get('pages'))
        sorts = self.sorts_query(kwargs.get(
            'sorts', [Sortable(goldman.config.SORT)]
        ))

        query = """
                SELECT {cols}, count(*) OVER() as _count
                FROM {table}
                """
        query = query.format(
            cols=self.field_cols(model),
            table=rtype,
        )

        filters = kwargs.get('filters')
        filters += getattr(model, 'default_filters', [])

        if filters:
            where, param = self.filters_query(filters)
            query += where

        query += sorts
        query += pages

        signals.pre_search.send(model.__class__, model=model)

        results = self.query(query, param=param)
        models = [model(result) for result in results]

        if models:
            signals.post_search.send(model.__class__, models=results)

        pages = kwargs.get('pages')
        if pages and results:
            pages.total = results[0]['_count']

        return models

    def update(self, model):
        """ Given a model object instance update it """

        signals.pre_update.send(model.__class__, model=model)
        signals.pre_save.send(model.__class__, model=model)

        param = self.to_pg(model)
        param['rid_value'] = param[model.rid_field]

        query = """
                UPDATE {table}
                SET ({dirty_cols}) = ({dirty_vals})
                WHERE {rid_field} = %(rid_value)s
                RETURNING {cols};
                """

        query = query.format(
            cols=self.field_cols(model),
            dirty_cols=self.dirty_cols(model),
            dirty_vals=self.dirty_vals(model),
            rid_field=model.rid_field,
            table=model.rtype,
        )

        result = self.query(query, param=param)

        signals.post_update.send(model.__class__, model=model)
        signals.post_save.send(model.__class__, model=model)

        return model.merge(result[0], clean=True)
