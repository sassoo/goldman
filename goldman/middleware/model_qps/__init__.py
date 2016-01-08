"""
    middleware.model_qps
    ~~~~~~~~~~~~~~~~~~~~

    This middleware will initialize the query parameters supported
    by our model based resources. The supported query params are
    those directly called out by the JSON API specification but
    do not require the JSON API (de)serializer.


    NOTE: Query param processing will NOT occur on resources
          without a model property containing a goldman model
          class object. The model is needed so proper vetting
          of the query params can occur against the models
          attributes.


    The request object will have it's attributes updated with
    the coerced query parameter values. The attribute names are
    the pluralized version of the query params themselves.

    Currently supported query params are:

        fields, filter, include, page, & sort
"""

import goldman.queryparams.fields as fields
import goldman.queryparams.filter as filters
import goldman.queryparams.include as includes
import goldman.queryparams.page as pages
import goldman.queryparams.sort as sorts


class Middleware(object):
    """ Model query parameter middleware. """

    # pylint: disable=unused-argument
    def process_resource(self, req, resp, resource):
        """ Process the request after routing.

        The resource is required to determine if a model based
        resource is being used for validations.
        """

        if hasattr(resource, 'model'):
            model = resource.model

            req.fields = fields.init(req, model)
            req.filters = filters.init(req, model)
            req.includes = includes.init(req, model)
            req.pages = pages.init(req, model)
            req.sorts = sorts.init(req, model)
