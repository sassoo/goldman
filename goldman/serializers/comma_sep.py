"""
    serializers.csv
    ~~~~~~~~~~~~~~~

    Serializer that is compliant with the RFC 4180 CSV format
"""

import goldman

from ..serializers.base import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    """ CSV serializer """

    MIMETYPE = goldman.CSV_MIMETYPE

    def serialize(self, data):
        """ Determine & invoke the proper serializer method

        If data is a list then the serialize_datas method will
        be run otherwise serialize_data.
        """

        pass
        # X-Total-Count header
        # Link header for pagination
        #   http://tools.ietf.org/html/rfc5988#section-5
        #   https://canvas.instructure.com/doc/api/file.pagination.html
