"""
    utils.str_helpers
    ~~~~~~~~~~~~~~~~~

    Convient string helpers. That's it.
"""

import uuid

from datetime import datetime as dt


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
