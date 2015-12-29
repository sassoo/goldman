"""
    deserializers.form_urlencoded
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Deserializer that simply acknowledges the need for form
    uploads according to:

        www.w3.org/TR/1999/REC-html401-19991224/interact/forms.html#h-17.13.4

    Falcon already takes form-urlencoded params & makes them
    available via request.get_param() so there is no need to
    do anything except register the mimetype with the deserializer.
"""

import goldman

from ..deserializers.base import Deserializer as BaseDeserializer


class Deserializer(BaseDeserializer):
    """ Form URL encoded compliant deserializer """

    MIMETYPE = goldman.FORMURL_MIMETYPE
