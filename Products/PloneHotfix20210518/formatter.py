from AccessControl import ModuleSecurityInfo
from AccessControl import secureModule


string_modsec = ModuleSecurityInfo("string")
for name in ("Formatter", "Template"):
    string_modsec.declarePrivate(name)  # NOQA: D001
secureModule("string")
