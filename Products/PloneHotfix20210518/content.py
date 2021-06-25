# -*- coding: utf-8 -*-
from ._compat import char_types

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

    # Also, if 'escape' is defined, then either the 2020 hotfix is there,
    # or we have an already fixed version.
    # This means the title is already escaped.
    # We need to know this, to avoid getting a doubly_escaped title.
    escape = getattr(fc, "escape", None)
    if escape is not None:
        title_already_escaped = True
    else:
        title_already_escaped = False
        try:
            # py3
            from html import escape
        except ImportError:
            # py2
            from cgi import escape


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
            # Watch out for doubly escaped Title.
            # In Python 2, the keys are unicode.
            # We could use simplejson.loads, which always gives string.
            # But the use of simplejson was only introduced in
            # plone.app.content 3.4.2.  Let's check bytes and unicode.
            # if title_already_escaped and key in (b"Title", u"Title"):
            if title_already_escaped and key == "Title":
                continue
            escaped_value = escape(value)
            if escaped_value == value:
                continue
            obj[key] = escaped_value
            changed = True
        if not changed:
            return result
        result = json.dumps(data)
        return result


    fc.ContextInfo.__call__ = context_info_call
