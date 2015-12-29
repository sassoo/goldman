"""
    signals
    ~~~~~~~

    All of our blinker signals.
"""

import blinker


"""
Signals for our goldman authentication interfaces. See the
interfaces for additional clarity on just when they are called.
"""

# pylint: disable=invalid-name
pre_authenticate = blinker.signal('pre_authenticate')
post_authenticate = blinker.signal('post_authenticate')


"""
Signals for our goldman model based resource responders.
These should be called first thing by the responders.
"""

responder_pre_any = blinker.signal('responder_pre_any')
responder_post_any = blinker.signal('responder_post_any')

responder_pre_create = blinker.signal('responder_pre_create')
responder_post_create = blinker.signal('responder_post_create')

responder_pre_delete = blinker.signal('responder_pre_delete')
responder_post_delete = blinker.signal('responder_post_delete')

responder_pre_find = blinker.signal('responder_pre_find')
responder_post_find = blinker.signal('responder_post_find')

responder_pre_search = blinker.signal('responder_pre_search')
responder_post_search = blinker.signal('responder_post_search')

responder_pre_update = blinker.signal('responder_pre_update')
responder_post_update = blinker.signal('responder_post_update')


"""
Signals for our file upload resources before & after an
upload for a given model.
"""

responder_pre_upload = blinker.signal('responder_pre_upload')
responder_post_upload = blinker.signal('responder_post_upload')

pre_upload = blinker.signal('pre_upload')
post_upload = blinker.signal('post_upload')


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
