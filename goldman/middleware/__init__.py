"""
    middleware
    ~~~~~~~~~~

    Our custom middlewares as documented here:

        http://falcon.readthedocs.org/en/stable/api/middleware.html

    Things like auth, logging, analytics, etc can go here.
"""

from ..middleware.basicauth import Middleware as BasicAuthMiddleware
from ..middleware.bearer_token import Middleware as BearerTokenMiddleware
from ..middleware.deserializer import Middleware as DeserializerMiddleware
from ..middleware.falcon_catcher import Middleware as FalconCatcherMiddleware
from ..middleware.model_qps import Middleware as ModelQpsMiddleware
from ..middleware.rfc_7231 import Middleware as RFC7231Middleware
from ..middleware.security import Middleware as SecurityMiddleware
from ..middleware.serializer import Middleware as SerializerMiddleware
from ..middleware.threadlocal import Middleware as ThreadLocalMiddleware


MIDDLEWARES = [
    BasicAuthMiddleware,
    BearerTokenMiddleware,
    DeserializerMiddleware,
    FalconCatcherMiddleware,
    ModelQpsMiddleware,
    RFC7231Middleware,
    SecurityMiddleware,
    SerializerMiddleware,
    ThreadLocalMiddleware,
]
