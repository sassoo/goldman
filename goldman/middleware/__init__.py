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
from ..middleware.http_specs import Middleware as HttpSpecsMiddleware
from ..middleware.model_qps import Middleware as ModelQpsMiddleware
from ..middleware.rate_limit import Middleware as RateLimitMiddleware
from ..middleware.security import Middleware as SecurityMiddleware
from ..middleware.serializer import Middleware as SerializerMiddleware
from ..middleware.threadlocal import Middleware as ThreadLocalMiddleware


MIDDLEWARES = [
    BasicAuthMiddleware,
    BearerTokenMiddleware,
    DeserializerMiddleware,
    HttpSpecsMiddleware,
    ModelQpsMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    SerializerMiddleware,
    ThreadLocalMiddleware,
]
