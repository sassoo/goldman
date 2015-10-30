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
pre_create = blinker.signal('pre_create')
post_create = blinker.signal('post_create')

pre_delete = blinker.signal('pre_delete')
post_delete = blinker.signal('post_delete')

pre_find = blinker.signal('pre_find')
post_find = blinker.signal('post_find')

pre_save = blinker.signal('pre_save')
post_save = blinker.signal('post_save')

pre_update = blinker.signal('pre_update')
post_update = blinker.signal('post_update')
