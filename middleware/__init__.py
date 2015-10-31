"""
    middleware
    ~~~~~~~~~~

    Our custom middlewares as documented here:

        http://falcon.readthedocs.org/en/stable/api/middleware.html

    Things like auth, logging, analytics, etc can go here.
"""

from ..middleware.basicauth import Middleware as BasicAuthMiddleware
from ..middleware.deserializer import Middleware as DeserializerMiddleware
from ..middleware.falcon_catcher import Middleware as FalconCatcherMiddleware
from ..middleware.security import Middleware as SecurityMiddleware
from ..middleware.serializer import Middleware as SerializerMiddleware
from ..middleware.threadlocal import Middleware as ThreadLocalMiddleware


MIDDLEWARES = [
    BasicAuthMiddleware,
    DeserializerMiddleware,
    FalconCatcherMiddleware,
    SecurityMiddleware,
    SerializerMiddleware,
    ThreadLocalMiddleware,
]
