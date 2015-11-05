"""
    responders.model
    ~~~~~~~~~~~~~~~~

    Model responder mixin.

    This can be used on any resources that need common
    funtionality when interacting with models in a RESTFUL
    like fashion.

    Things like JSON API compatible query parameter processing
    URL validations, some store method wrapping, etc.
"""

import goldman
import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort


# pylint: disable=too-many-instance-attributes
class Responder(object):
    """ Model responder mixin """

    def __init__(self, resource, req, resp):  # pylint: disable=unused-argument
        """ Initialize all the model responder

        This responder should be passed in the same args as a
        native falcon resources responder. The responder will
        expect to find the following attributes on the resource:

        `resource.model`:
            model class (not instance)
        """

        self._model = resource.model

    def find(self, rtype, rid):
        """ Find a model from the store by resource id """

        rid_field = self._model.rid_field
        model = goldman.sess.store.find(rtype, rid_field, rid)

        if not model:
            abort(exceptions.DocumentNotFound)

        return model

    def _from_rest_hide(self, model, props):
        """ Purge fields not allowed during a REST deserialization

        This is done on fields with `from_rest=False`.
        """

        hide = model.get_fields_by_prop('from_rest', False)

        for field in hide:
            try:
                del props[field]
            except KeyError:
                continue

    def _from_rest_ignore(self, model, props):
        """ Purge fields that are completely unknown """

        model_fields = model.all_fields

        for prop in props.keys():
            if prop not in model_fields:
                del props[prop]

    def _from_rest_lower(self, model, props):
        """ Lowercase fields requesting it during a REST deserialization """

        for field in model.to_lower:
            try:
                props[field] = props[field].lower()
            except (AttributeError, KeyError):
                continue

    def from_rest(self, model, props):
        """ Map the REST data onto self

        Additionally, perform the following tasks:

            * purge all fields not allowed as incoming data
            * purge all unknown fields from the incoming data
            * lowercase certain fields that need it
            * merge new data with existing & validate
                * mutate the existing model (self)
                * abort on validation errors
                * coerce all the values
        """

        self._from_rest_hide(model, props)
        self._from_rest_ignore(model, props)
        self._from_rest_lower(model, props)

        model.merge(props, validate=True)

    def _to_rest_hide(self, model, props):
        """ Purge fields not allowed during a REST serialization

        This is done on fields with `to_rest=False`.
        """

        hide = model.get_fields_by_prop('to_rest', False)

        for field in hide:
            try:
                del props[field]
            except KeyError:
                continue

    def _to_rest_include(self, model, props, includes):
        """ Fetch the models to be included """

        props['include'] = []

        if includes:
            for include in includes:
                rel = getattr(model, include)
                model = rel.load()

                if model:
                    props['include'].append(self.to_rest(model))

    def _to_rest_rels(self, model, props):
        """ Move the relationships to appropriate location in the props

        All to_ones should be in a to_one key while all to_manys
        should be in a to_many key.
        """

        props['to_many'] = {}
        props['to_one'] = {}

        for key in model.to_one:
            try:
                props['to_one'][key] = props.pop(key)
            except KeyError:
                continue

        for key in model.to_many:
            try:
                props['to_many'][key] = props.pop(key)
            except KeyError:
                continue

    def to_rest(self, model, include=None):
        """ Convert the model into a dict for serialization """

        sparse = goldman.sess.req.fields.get(model.rtype, [])

        if sparse:
            sparse += [model.rid_field, model.rtype_field]

        props = model.to_primitive(sparse_fields=sparse)
        props['rid'] = props.pop(model.rid_field)
        props['rtype'] = props.pop(model.rtype_field)

        self._to_rest_hide(model, props)
        self._to_rest_rels(model, props)
        self._to_rest_include(model, props, include)

        return props
