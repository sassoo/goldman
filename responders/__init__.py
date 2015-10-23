"""
    resources.responders
    ~~~~~~~~~~~~~~~~~~~~

    An assortment of interfaces for composition or common
    methods across our responders by a logical grouping.
"""

from ..responders.rest import Responder as RestResponder


RESPONDERS = [
    RestResponder,
]
