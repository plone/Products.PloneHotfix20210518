try:
    # Plone 5
    from plone.app.users.schema import IUserDataSchema
except ImportError:
    # Plone 4
    IUserDataSchema = None
from Products.CMFPlone import PloneMessageFactory as _
from zope import schema


class FullnameInvalid(schema.ValidationError):
    __doc__ = _(u"Invalid fullname.")


def checkFullname(value):
    # We override the original constraint of TextLine,
    # so we must do our own checks.
    if "\n" in value or "\r" in value:
        raise FullnameInvalid
    if value and "<" in value:
        # Trying to insert code, you nasty hacker?
        # Most spots where we show a fullname will not be vulnerable,
        # but some might, for example when loaded via JavaScript.
        raise FullnameInvalid

    return True


if IUserDataSchema is not None:
    IUserDataSchema["fullname"].constraint = checkFullname
