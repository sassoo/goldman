"""
    utils.model_helpers
    ~~~~~~~~~~~~~~~~~~~

    Convient model helpers. That's it.
"""

import goldman


def rtype_to_model(rtype):
    """ Return a boolean if the string value represents one

    :param val: str
    :return: bool
    :raise: ValueError
    """

    models = goldman.config.MODELS

    for model in models:
        if rtype.lower() == model.RTYPE.lower():
            return model

    raise ValueError
