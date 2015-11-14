"""
    signals
    ~~~~~~~

    All of our blinker signals.
"""

import blinker


"""
Signals for our base goldman model
"""

# pylint: disable=invalid-name
acl_create = blinker.signal('acl_create')
pre_create = blinker.signal('pre_create')
post_create = blinker.signal('post_create')

acl_delete = blinker.signal('acl_delete')
pre_delete = blinker.signal('pre_delete')
post_delete = blinker.signal('post_delete')

acl_find = blinker.signal('acl_find')
pre_find = blinker.signal('pre_find')
post_find = blinker.signal('post_find')

acl_save = blinker.signal('acl_save')
pre_save = blinker.signal('pre_save')
post_save = blinker.signal('post_save')

acl_search = blinker.signal('acl_search')
pre_search = blinker.signal('pre_search')
post_search = blinker.signal('post_search')

acl_update = blinker.signal('acl_update')
pre_update = blinker.signal('pre_update')
post_update = blinker.signal('post_update')
