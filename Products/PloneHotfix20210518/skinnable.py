from Products.CMFCore.Skinnable import SkinnableObjectManager
from Products.CMFCore.utils import getToolByName


SkinnableObjectManager._orig_getSkinNameFromRequest = (
    SkinnableObjectManager.getSkinNameFromRequest
)


def getSkinNameFromRequest(self, REQUEST):
    name = self._orig_getSkinNameFromRequest(REQUEST)
    if not name:
        return
    # CMFCore 2.3+ uses queryUtility(ISkinsTool)
    # CMFCore 2.2 uses self.getSkinsFolderName()
    # getToolByName seems a fair compromise in Plone.
    skins_tool = getToolByName(self, "portal_skins", None)
    if skins_tool is None:
        return
    if name not in skins_tool.getSkinSelections():
        return
    return name


SkinnableObjectManager.getSkinNameFromRequest = getSkinNameFromRequest
