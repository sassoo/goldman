"""
    goldman
    ~~~~~~~

    This is where we initialize the goldman God object.
"""

import threading

sess = threading.local()  # pylint: disable=invalid-name


from goldman.mimetypes import *
from goldman.models import *
from goldman.middleware import *
from goldman.deserializers import *
from goldman.serializers import *
from goldman.resources import *
from goldman.responders import *


from goldman.config import Config

config = Config()  # pylint: disable=invalid-name


from goldman.api import *
