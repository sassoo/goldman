"""
    signals
    ~~~~~~~

    All of our blinker signals.
"""

import blinker


"""
Signals for our goldman model based resource responders.
These should be called first thing by the responders.
"""

# pylint: disable=invalid-name
on_any = blinker.signal('on_any')
on_delete = blinker.signal('on_delete')
on_get = blinker.signal('on_get')
on_patch = blinker.signal('on_patch')
on_post = blinker.signal('on_post')


"""
Signals for our base goldman models invoked by the store
during there requisite operations
"""

pre_create = blinker.signal('pre_create')
post_create = blinker.signal('post_create')

pre_delete = blinker.signal('pre_delete')
post_delete = blinker.signal('post_delete')

pre_find = blinker.signal('pre_find')
post_find = blinker.signal('post_find')

pre_save = blinker.signal('pre_save')
post_save = blinker.signal('post_save')

pre_search = blinker.signal('pre_search')
post_search = blinker.signal('post_search')

pre_update = blinker.signal('pre_update')
post_update = blinker.signal('post_update')
