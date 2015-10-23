"""
    app
    ~~~

    This is where we initialize the falcon application.

    We also need to register our own serializer for native
    falcon HTTPError exceptions.
"""

from goldman.config import Config

config = Config()


from goldman.deserializers import *
from goldman.serializers import *

from goldman.ext.Falcon import *
from goldman.models import *
from goldman.middleware import *
from goldman.resources import *
from goldman.responders import *

from goldman.api import API
