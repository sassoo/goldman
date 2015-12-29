"""
    utils.decorators
    ~~~~~~~~~~~~~~~~

    Our custom python decorators.
"""


# pylint: disable=invalid-name
class classproperty(object):  # NOQA
    """ @classmethod meets @property

    TIP: This is only a getter! Not a setter!

    Inspired by stackoverflow:
        /questions/5189699/how-can-i-make-a-class-property-in-python
    """
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)
