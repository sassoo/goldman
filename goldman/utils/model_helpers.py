"""
    utils.model_helpers
    ~~~~~~~~~~~~~~~~~~~

    Convient model helpers. That's it.
"""

import goldman


__all__ = ['rtype_to_model']


def rtype_to_model(rtype):
    """ Return a model class object given a string resource type

    :param rtype:
        string resource type
    :return:
        model class object
    :raise:
        ValueError
    """

    models = goldman.config.MODELS
    for model in models:
        if rtype.lower() == model.RTYPE.lower():
            return model
    raise ValueError('%s resource type not registered' % rtype)
