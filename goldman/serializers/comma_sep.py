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

        super(Serializer, self).serialize(data)

        self.resp.content_type += '; header=present'
        import pprint
        pprint.PrettyPrinter().pprint(data)

        # X-Total-Count header
        # Link header for pagination
        #   tools.ietf.org/html/rfc5988#section-5
        #   canvas.instructure.com/doc/api/file.pagination.html
        #   github.com/falconry/falcon/blob/master/falcon/response.py#L379

    def _serialize_datas(self, datas):
        """ Turn the list into individual CSV records (rows)

        :spec: jsonapi.org/format/#document-top-level
        :param datas: list of dicts
        :return: list
        """

        return [self._serialize_data(d) for d in datas]

    def _serialize_data(self, data):
        """ Turn the data into a single CSV record (row)

        :spec: jsonapi.org/format/#document-resource-objects
        :param data: dict
        :return: dict
        """

        data.update(data['include'])
        data.update(data['to_many'])
        data.update(data['to_one'])

        for key, val in data.items():
            if isinstance(val, dict):
                pass
            elif isinstance(val, list):
                pass
            else:
                str(val)
