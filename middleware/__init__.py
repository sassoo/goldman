"""
    middleware
    ~~~~~~~~~~

    Our custom middlewares as documented here:

        http://falcon.readthedocs.org/en/stable/api/middleware.html

    Things like auth, logging, analytics, etc can go here.
"""

# from app.middleware.basicauth import BasicAuth
from ..middleware.deserializer import Middleware as DeserializerMiddleware
from ..middleware.falcon_catcher import Middleware as FalconCatcherMiddleware
from ..middleware.security import Middleware as SecurityMiddleware
from ..middleware.serializer import Middleware as SerializerMiddleware


MIDDLEWARES = [
    DeserializerMiddleware,
    FalconCatcherMiddleware,
    SecurityMiddleware,
    SerializerMiddleware,
]
