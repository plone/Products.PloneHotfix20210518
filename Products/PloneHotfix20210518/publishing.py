# -*- coding: utf-8 -*-
from .utils import delete_method_docstring


try:
    from Products.CMFPlone.PloneTool import PloneTool
except ImportError:
    PloneTool = None


content_classes = []

try:
    from Products.CMFPlone.Portal import PloneSite

    content_classes.append(PloneSite)
except ImportError:
    pass
try:
    from plone.dexterity.content import Container
    from plone.dexterity.content import Item

    content_classes.append(Container)
    content_classes.append(Item)
except ImportError:
    pass
try:
    from Products.ATContentTypes.content.base import ATCTBTreeFolder
    from Products.ATContentTypes.content.base import ATCTContent

    content_classes.append(ATCTBTreeFolder)
    content_classes.append(ATCTContent)
except ImportError:
    pass


if PloneTool is not None:
    # Some of these methods must be publicly available,
    # for use in a script or template.  But none need to be available as url.
    # Some could be abused in that case, for example for reflected XSS.
    method_names = (
        "addPortalMessage",
        "browserDefault",
        "getReviewStateTitleFor",
        "portal_utf8",
        "urlparse",
        "urlunparse",
        "utf8_portal",
        "getOwnerName",
        "normalizeString",
        "getEmptyTitle",
    )
    for method_name in method_names:
        delete_method_docstring(PloneTool, method_name)


# Products.CMFPlone has patches/publishing.py, containing
# the publishing patch from Products.PloneHotfix20160419,
# but this does not work on Python 3.  So we do it better here.
method_names = (
    "EffectiveDate",
    "ExpirationDate",
    "getAttributes",
    "getChildNodes",
    "getFirstChild",
    "getLastChild",
    "getLayout",
    "getNextSibling",
    "getNodeName",
    "getNodeType",
    "getNodeValue",
    "getOwnerDocument",
    "getParentNode",
    "getPhysicalPath",
    "getPreviousSibling",
    "getTagName",
    "hasChildNodes",
    "Type",
)
for klass in content_classes:
    for method_name in method_names:
        delete_method_docstring(klass, method_name)
