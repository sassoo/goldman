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
pre_req = blinker.signal('pre_req')
post_req = blinker.signal('post_req')

pre_req_create = blinker.signal('pre_req_create')
post_req_create = blinker.signal('post_req_create')

pre_req_delete = blinker.signal('pre_req_delete')
post_req_delete = blinker.signal('post_req_delete')

pre_req_find = blinker.signal('pre_req_find')
post_req_find = blinker.signal('post_req_find')

pre_req_search = blinker.signal('pre_req_search')
post_req_search = blinker.signal('post_req_search')

pre_req_update = blinker.signal('pre_req_update')
post_req_update = blinker.signal('post_req_update')


"""
Signals for our file upload resources before & after an
upload for a given model.
"""

pre_req_upload = blinker.signal('pre_req_upload')
post_req_upload = blinker.signal('post_req_upload')

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
