"""
    deserializers.csv
    ~~~~~~~~~~~~~~~~~

    Deserializer that is compliant with the RFC 4180 CSV format

    XXX FIX: handle relationships
"""

import goldman
import goldman.exceptions as exceptions
import csv

from goldman.utils.error_helpers import abort
from ..deserializers.base import Deserializer as BaseDeserializer, fail


class Normalizer(object):
    """ The JSON API payload normalizer """

    @classmethod
    def run(cls, row, reader):
        """ Invoke the CSV normalizer

        We don't need to vet the inputs much because the
        Parser has already done all the work.

        :return: dict
        """

        pass


class Parser(object):
    """ The CSV payload parser """

    @classmethod
    def run(cls, row, reader):
        """ Invoke the CSV parser on an individual row

        The row should already be a dict from the CSV reader.
        The reader is passed in so we can easily reference the
        CSV document headers & line number when generating
        errors.
        """

        cls._parse_keys(row, reader.line_num)
        cls._parse_relationships(row, reader.line_num)

    @staticmethod
    def _parse_keys(row, line_num):
        """ Perform some sanity checks on they keys

        Each key in the row should not be named None cause
        (that's an overrun). A key named `type` MUST be
        present on the row & have a string value.

        :param row: dict
        :param line_num: int
        """

        link = 'tools.ietf.org/html/rfc4180#section-2'

        none_keys = [key for key in row.keys() if key is None]

        if none_keys:
            fail('You have more fields defined on row number {} '
                 'than field headers in your CSV data. Please fix '
                 'your request body.'.format(line_num), link)

        elif not row.get('type'):
            fail('Row number {} does not have a type value defined. '
                 'Please fix your request body.'.format(line_num), link)

    @staticmethod
    def _parse_relationships(row, line_num):
        """ Perform some sanity checks on the relationships

        Relationships should have a single '.' in them & `id`
        & `type` keys. A string type value is required while id
        is not since it could be severing the relationship.

        :param row: dict
        :param line_num: int
        """

        pass


class Deserializer(BaseDeserializer):
    """ CSV deserializer """

    MIMETYPE = goldman.CSV_MIMETYPE

    def deserialize(self, data=None):
        """ Invoke the deserializer

        If the payload is a collection (more than 1 records)
        then a list will be returned of normalized dict's.

        If the payload is a single item then the normalized
        dict will be returned (not a list)

        :return: list or dict
        """

        data = []

        if self.req.content_type_params.get('header') != 'present':
            abort(exceptions.InvalidRequestHeader(**{
                'detail': 'When using text/csv your Content-Type '
                          'header MUST have a header=present parameter '
                          '& the payload MUST include a header of fields',
                'links': 'tools.ietf.org/html/rfc4180#section-3'
            }))

        try:
            reader = csv.DictReader(self.req.stream)

            self._validate_field_headers(reader)

            for row in reader:
                Parser.run(row, reader)

                row = Normalizer.run(row, reader)
                row = super(Deserializer, self).deserialize(data)

                data.append(row)
        except csv.Error:
            abort(exceptions.InvalidRequestBody)

        return data

    @staticmethod
    def _validate_field_headers(reader):
        """ Perform some validations on the CSV headers

        A `type` field header must be present & all field
        headers must be strings.

        :param reader: csv reader object
        """

        link = 'tools.ietf.org/html/rfc4180#section-2'

        for field in reader.fieldnames:
            if not isinstance(field, str):
                fail('All headers in your CSV payload must be '
                     'strings.', link)

        if 'type' not in reader.fieldnames:
            fail('A type header must be present in your CSV '
                 'payload.', link)
