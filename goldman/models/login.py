"""
    models.logins
    ~~~~~~~~~~~~~

    The Login model & schema
"""

import goldman
import goldman.signals as signals

from ..models.default_schema import Model as DefaultSchemaModel
from datetime import datetime as dt
from goldman.exceptions import AuthRejected
from goldman.utils.str_helpers import (
    cmp_val_salt_hash,
    gen_salt_and_hash,
    random_str,
)
from goldman.types import DateTimeType, ResourceType
from schematics.exceptions import ValidationError
from schematics.types import BooleanType, StringType


class Model(DefaultSchemaModel):
    """ Login model """

    RTYPE = 'logins'

    """
    The attrs below are the models fields
    """

    rtype = ResourceType(RTYPE)

    # identity fields
    username = StringType(
        admin_restrict=True,
        lower=True,
        max_length=25,
        required=True,
    )

    # security fields
    locked = BooleanType(
        admin_restrict=True,
        required=True,
    )
    login_date = DateTimeType(from_rest=False)
    password = StringType(
        max_length=100,
        min_length=6,
        serialize_when_none=False,
        to_rest=False,
    )
    salt = StringType(
        from_rest=False,
        to_rest=False,
    )
    token = StringType(
        from_rest=False,
        to_rest=False,
    )

    @classmethod
    def auth_creds(cls, username, password):
        """ Callback method for Basic Authentication """

        store = goldman.sess.store
        login = store.find(cls.RTYPE, 'username', username)

        if not login:
            msg = 'No login found by that username. Spelling error?'
            raise AuthRejected(**{'detail': msg})
        elif login.locked:
            msg = 'The login account is currently locked out.'
            raise AuthRejected(**{'detail': msg})
        elif not cmp_val_salt_hash(password, login.salt, login.password):
            msg = 'The password provided is incorrect. Spelling error?'
            raise AuthRejected(**{'detail': msg})
        else:
            return login

    @classmethod
    def auth_creds_token(cls, username, password):
        """ Callback method for OAuth 2.0 ROPC resource """

        login = cls.auth_creds(username, password)

        if not login.token:
            login.token = random_str()
        return login, login.token

    @classmethod
    def auth_token(cls, token):
        """ Callback method for OAuth 2.0 bearer token middleware """

        store = goldman.sess.store
        login = store.find(cls.RTYPE, 'token', token)

        if not login:
            msg = 'No login found with that token. It may have been revoked.'
            raise AuthRejected(**{'detail': msg})
        elif login.locked:
            msg = 'The login account is currently locked out.'
            raise AuthRejected(**{'detail': msg})
        else:
            return login

    def validate_username(self, data, value):
        """ Ensure the username is unique

        If the login is being created then simply check if
        the username is in the store & fail.

        Otherwise if the login is being updated check if the
        existing rid on a username match is the same as the
        login being updated otherwise fail.
        """

        store = goldman.sess.store
        existing = store.find(data['rtype'], 'username', value)

        if existing:
            if not data['rid'] or data['rid'] != existing.rid:
                raise ValidationError('username is already taken')


# pylint: disable=unused-argument
def pre_create(sender, model):
    """ Callback before creating a new login

    Without a password during create we are forced to
    lock the account & set the password to something
    random.
    """

    if not model.password:
        model.locked, model.password = True, random_str()


def pre_save(sender, model):
    """ Hash the password if being changed """

    if 'password' in model.dirty_fields:
        model.salt, model.password = gen_salt_and_hash(model.password)


def post_authenticate(sender):
    """ Update the login_date timestamp

    The login_date update will be debounced so writes don't
    occur on every hit of the the API. If the login_date
    was modified within 15 minutes then don't update it.
    """

    login = goldman.sess.login
    now = dt.now()

    if not login.login_date:
        login.login_date = now
    else:
        sec_since_updated = (now - login.login_date).seconds
        min_since_updated = sec_since_updated / 60

        if min_since_updated > 15:
            login.login_date = now

    if login.dirty:
        store = goldman.sess.store
        store.update(login)


signals.pre_create.connect(pre_create, sender=Model)
signals.pre_save.connect(pre_save, sender=Model)

signals.post_authenticate.connect(post_authenticate)
