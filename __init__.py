"""
    app
    ~~~

    This is where we initialize the falcon application.
"""

import threading

sess = threading.local()  # pylint: disable=invalid-name


from goldman.config import Config

config = Config()  # pylint: disable=invalid-name


from goldman.deserializers import *
from goldman.serializers import *

from goldman.models import *
from goldman.resources import *
from goldman.responders import *

from goldman.api import *
