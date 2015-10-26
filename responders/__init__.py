"""
    responders
    ~~~~~~~~~~

    An assortment of interfaces for composition or common
    methods across our responders by a logical grouping.
"""

from ..responders.model import Responder as ModelResponder


RESPONDERS = [
    ModelResponder,
]
