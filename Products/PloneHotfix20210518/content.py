# -*- coding: utf-8 -*-
from ._compat import char_types
from .htmltools import html_escape
from .htmltools import html_safe

import json

try:
    # plone.app.content 3
    from plone.app.content.browser import contents as fc
except ImportError:
    try:
        # 2.2.x
        from plone.app.content.browser import folder as fc
    except ImportError:
        # 2.1.x and lower do not need this patch
        fc = None


if fc is not None:
    # Patch ContextInfo
    # If PloneHotfix20200121 is loaded, then the original call will already
    # have been saved under a different name.
    # We patch that one, instead of letting our patch call a patch which calls the original.
    orig_name = "_orig___call__"
    if not hasattr(fc.ContextInfo, orig_name):
        setattr(fc.ContextInfo, orig_name, fc.ContextInfo.__call__)

    def context_info_call(self):
        result = self._orig___call__()
        data = json.loads(result)
        obj = data.get("object", None)
        if obj is None:
            return result
        changed = False
        for key, value in obj.items():
            if not isinstance(value, char_types):
                continue
            safe_value = html_safe(value)
            if safe_value == value:
                continue
            obj[key] = safe_value
            changed = True
        if not changed:
            return result
        result = json.dumps(data)
        return result


    fc.ContextInfo.__call__ = context_info_call
