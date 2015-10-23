"""
    serializers.csv
    ~~~~~~~~~~~~~~~

    Serializer that is compliant with the RFC 4180 CSV format
"""

import goldman

from ..serializers.base import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    """ CSV serializer """

    MIMETYPE = goldman.config.CSV_MIMETYPE

    def serialize(self, resp, data):
        """ Determine & invoke the proper serializer method

        If data is a list then the serialize_datas method will
        be run otherwise serialize_data.

        :param data: list or single object to be serialized
        :param resp: response object
        """

        pass
