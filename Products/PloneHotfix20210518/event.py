from plone.app.event.ical import importer
from zope.i18nmessageid import MessageFactory
from zope.interface import Invalid


_ = MessageFactory('plone')


def no_file_protocol_url(value):
    """Validator for ical_url: we do not want file: urls.

    This opens up security issues.

    Originally we only checked file://, but that still allows relative urls
    like file:../
    """
    if value and value.startswith("file:"):
        raise Invalid(_(u"URLs with file: are not allowed."))
    return True


importer.IIcalendarImportSettings["ical_url"].constraint = no_file_protocol_url
# plone.app.event 3.2.10+ already has this constraint, but a less strict one.
# Override it for good measure.
importer.no_file_protocol_url = no_file_protocol_url
