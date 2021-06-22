# -*- coding: utf-8 -*-
from .utils import protect_class
from Products.CMFCore.permissions import ManagePortal


try:
    from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool
except ImportError:
    QuickInstallerTool = None
try:
    from Products.CMFQuickInstallerTool.InstalledProduct import InstalledProduct
except ImportError:
    InstalledProduct = None
try:
    # CMFPlone has a wrapper around the tool.
    from Products.CMFPlone.QuickInstallerTool import QuickInstallerTool as PloneQI
except ImportError:
    PloneQI = None


if QuickInstallerTool is not None:
    protect_class(QuickInstallerTool, ManagePortal)
if InstalledProduct is not None:
    protect_class(InstalledProduct, ManagePortal)
if PloneQI is not None:
    protect_class(PloneQI, ManagePortal)
