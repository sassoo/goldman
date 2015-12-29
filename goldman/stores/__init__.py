"""
    stores
    ~~~~~~

    All stores supported by our API

    Be mindful of how they are named to avoid conflict with any
    official 3rd party packages.

    TIP: Unlike other modules in goldman we don't import all
         of the different stores since they need 3rd party
         libs. Load only if needed.
"""

from ..stores.base import Store as BaseStore


RESOURCES = [
    BaseStore,
]
