"""
    utils.str_helpers
    ~~~~~~~~~~~~~~~~~

    Convient string helpers. That's it.
"""

import hashlib
import uuid

from datetime import datetime as dt


def cmp_val_salt_hash(val, salt, str_hash):
    """ Given a string, salt, & hash validate the string

    The salt & val will be concatented as in gen_salt_and hash()
    & compared to the provided hash. This will only ever work
    with hashes derived from gen_salt_and_hash()

    :param val: clear-text string
    :param salt: string salt
    :param str_hash: existing hash to compare against
    :return: boolean
    """

    computed_hash = hashlib.sha256(val + salt).hexdigest()

    return computed_hash == str_hash


def gen_salt_and_hash(val=None):
    """ Generate a salt & hash

    If no string is provided then a random string will be
    used to hash & referred to as `val`.

    The salt will always be randomly generated & the hash
    will be a sha256 hex value of the `val` & the salt as
    a concatenated string. It follows the guidance here:

        crackstation.net/hashing-security.htm#properhashing

    :param val: str
    :return: tuple of strings (salt, hash)
    """

    if not val:
        val = random_str()

    str_salt = random_str()
    str_hash = hashlib.sha256(val + str_salt).hexdigest()

    return str_salt, str_hash


def naked(val):
    """ Given a string strip off all white space & quotes """

    return val.strip(' "\'\t')


def random_str():
    """ Return a random string """

    return str(uuid.uuid4())


def str_to_bool(val):
    """ Return a boolean if the string value represents one

    :param val: str
    :return: bool
    :raise: ValueError
    """

    if isinstance(val, bool):
        return val
    elif val.lower() == 'true':
        return True
    elif val.lower() == 'false':
        return False
    else:
        raise ValueError


def str_to_dt(val):
    """ Return a datetime object if the string value represents one

    Epoch integer or an ISO 8601 compatible string is
    supported.

    :param val: str
    :return: datetime
    :raise: ValueError
    """

    if isinstance(val, dt):
        return val

    try:
        if val.isdigit():
            val = dt.utcfromtimestamp(float(val))
        else:
            val = dt.strptime(val, '%Y-%m-%dT%H:%M:%S.%f')
    except (AttributeError, TypeError):
        raise ValueError

    return val


def str_to_uuid(val):
    """ Return a UUID object if the string value represents one

    :param val: str
    :return: UUID
    :raise: ValueError
    """

    if isinstance(val, uuid.UUID):
        return val

    try:
        return uuid.UUID(str(val), version=4)
    except (AttributeError, ValueError):
        raise ValueError
