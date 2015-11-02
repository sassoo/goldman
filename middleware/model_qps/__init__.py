"""
    middleware.model_qps
    ~~~~~~~~~~~~~~~~~~~~

    This middleware will initialize the query parameters supported
    by our model based resources. The supported query params are
    those directly called out by the JSON API specification but
    do not require the JSON API (de)serializer.

    The request object will have it's attributes updated with
    the coerced query parameter values. The attribute names are
    the pluralized version of the query params themselves.

    Currently supported query params are:

        fields, filter, include, page, & sort

    Any supported (de)serializer of our models MUST honor these
    query parameters!


    Processing & coercsion will take place for each query parameter
    regardless if the resource is backed by a model. However, if
    the resource is backed by a model then additional model based
    validations will be run to enforce certain rules.

    It's also nice of an API to notify the user when they've done
    something wrong rather than silently ignore it resulting in
    unexpected output!
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

        req.fields = fields.from_req(req)
        req.filters = filters.from_req(req)
        req.includes = includes.from_req(req)
        req.pages = pages.from_req(req)
        req.sorts = sorts.from_req(req)

        if hasattr(resource, 'model'):
            model = resource.model

            fields.validate(req, model)
            filters.validate(req, model)
            includes.validate(req, model)
            pages.validate(req, model)
            sorts.validate(req, model)
