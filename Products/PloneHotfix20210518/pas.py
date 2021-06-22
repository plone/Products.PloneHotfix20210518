from .utils import _getSecurity
from .utils import delete_method_docstring
from .utils import InitializeClass
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.plugins.ZODBRoleManager import ZODBRoleManager


pas_methods = (
    "applyTransform",
    "lower",
    "upper",
)
# Removing docstrings is not effective in this case,
# likely caused by the security.public setting on these methods.
# Replace them by security.private, as PluggableAuthService 2.6.2 already does.
security = _getSecurity(PluggableAuthService)
security.declarePrivate(*pas_methods)
InitializeClass(PluggableAuthService)
security = _getSecurity(BasePlugin)
security.declarePrivate("applyTransform")
InitializeClass(BasePlugin)

security = _getSecurity(ZODBRoleManager)
security.declarePrivate("enumerateRoles")
InitializeClass(ZODBRoleManager)
# At first it looked like removing the docstring was needed on top of the
# private declaration.  This is no longer true, but we keep it to be sure.
delete_method_docstring(ZODBRoleManager, "enumerateRoles")
