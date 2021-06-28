from .htmltools import html_escape
from .htmltools import html_safe
from os import linesep
from Products.CMFDiffTool.libs import htmldiff

import Products.CMFDiffTool


try:
    from Products.CMFDiffTool.namedfile import is_same
    from Products.CMFDiffTool.namedfile import make_lists_same_length
    has_namedfile = True
except ImportError:
    # Very old versions did not have this support.
    has_namedfile = False
    is_same = None
    make_lists_same_length = None


try:
    # If this import works, this is already a fixed version.
    from Products.CMFDiffTool.utils import html_escape as already_patched
except ImportError:
    already_patched = False

if not already_patched:

    def binary_inline_diff(self):
        """Simple inline diff that just checks that the filename
        has changed."""
        css_class = 'FilenameDiff'
        html = []
        if self.oldFilename != self.newFilename:
            html.append(
                self.inlinediff_fmt % (css_class,
                                        self.filenameTitle(html_escape(self.oldFilename)),
                                        self.filenameTitle(html_escape(self.newFilename))),
            )

        if html:
            return linesep.join(html)


    Products.CMFDiffTool.BinaryDiff.BinaryDiff.inline_diff = binary_inline_diff


    def cmfdhtml_inline_diff(self):
        """Return a specialized diff for HTML"""
        a = '\n'.join(self._parseField(self.oldValue,
                                        filename=self.oldFilename))
        b = '\n'.join(self._parseField(self.newValue,
                                        filename=self.newFilename))
        return htmldiff.htmldiff(html_safe(a), html_safe(b))


    Products.CMFDiffTool.CMFDTHtmlDiff.CMFDTHtmlDiff.inline_diff = cmfdhtml_inline_diff


    def field_inline_diff(self):
        css_class = 'InlineDiff'
        inlinediff_fmt = self.inlinediff_fmt
        same_fmt = self.same_fmt
        r = []
        a = self._parseField(self.oldValue, filename=self.oldFilename)
        b = self._parseField(self.newValue, filename=self.newFilename)
        for tag, alo, ahi, blo, bhi in self.getLineDiffs():
            if tag == 'replace':
                for i in range(alo, ahi):
                    r.append(inlinediff_fmt % (css_class, html_escape(a[i]), ''))
                for i in range(blo, bhi):
                    r.append(inlinediff_fmt % (css_class, '', html_escape(b[i])))
            elif tag == 'delete':
                for i in range(alo, ahi):
                    r.append(inlinediff_fmt % (css_class, html_escape(a[i]), ''))
            elif tag == 'insert':
                for i in range(blo, bhi):
                    r.append(inlinediff_fmt % (css_class, '', html_escape(b[i])))
            elif tag == 'equal':
                for i in range(alo, ahi):
                    r.append(same_fmt % (css_class, html_escape(a[i])))
            else:
                raise ValueError('unknown tag "%s"' % tag)
        return '\n'.join(r)


    Products.CMFDiffTool.FieldDiff.FieldDiff.inline_diff = field_inline_diff


    def relationlist_inline_diff(self):
        css_class = 'InlineDiff'
        inlinediff_fmt = self.inlinediff_fmt
        same_fmt = self.same_fmt
        r = []
        for tag, alo, ahi, blo, bhi in self.getLineDiffs():
            if tag == 'replace':
                for i in range(alo, ahi):
                    obj = self.oldValue[i]
                    obj_title = html_escape(obj.Title())
                    obj_url = obj.absolute_url()
                    r.append(inlinediff_fmt %
                                (css_class, 'diff_sub', obj_url, obj_title))
                for i in range(blo, bhi):
                    obj = self.newValue[i]
                    obj_title = html_escape(obj.Title())
                    obj_url = obj.absolute_url()
                    r.append(inlinediff_fmt %
                                (css_class, 'diff_add', obj_url, obj_title))
            elif tag == 'delete':
                for i in range(alo, ahi):
                    obj = self.oldValue[i]
                    obj_title = html_escape(obj.Title())
                    obj_url = obj.absolute_url()
                    r.append(inlinediff_fmt %
                                (css_class, 'diff_sub', obj_url, obj_title))
            elif tag == 'insert':
                for i in range(blo, bhi):
                    obj = self.newValue[i]
                    obj_title = html_escape(obj.Title())
                    obj_url = obj.absolute_url()
                    r.append(inlinediff_fmt %
                                (css_class, 'diff_add', obj_url, obj_title))
            elif tag == 'equal':
                for i in range(alo, ahi):
                    obj = self.oldValue[i]
                    obj_title = html_escape(obj.Title())
                    obj_url = obj.absolute_url()
                    r.append(same_fmt % (css_class, obj_url, obj_title))
            else:
                raise ValueError('unknown tag %s' % tag)
        return '\n'.join(r)


    try:
        Products.CMFDiffTool.ListDiff.RelationListDiff.inline_diff = relationlist_inline_diff
    except AttributeError:
        # RelationListDiff does not exist in Plone 4.3.
        pass


    def text_inline_diff(self):
        """Simple inline diff that just assumes that either the filename
        has changed, or the text has been completely replaced."""
        css_class = 'InlineDiff'
        old_attr = self._parseField(self.oldValue,
                                    filename=self.oldFilename)
        new_attr = self._parseField(self.newValue,
                                    filename=self.newFilename)
        if old_attr:
            old_fname = old_attr.pop(0)
        else:
            old_fname = None
        if new_attr:
            new_fname = new_attr.pop(0)
        else:
            new_fname = None
        a = linesep.join(old_attr or [])
        b = linesep.join(new_attr or [])
        html = []
        if old_fname != new_fname:
            html.append(
                self.inlinediff_fmt % ('%s FilenameDiff' % css_class,
                                        html_escape(old_fname), html_escape(new_fname)),
            )
        if a != b:
            html.append(
                self.inlinediff_fmt % (css_class, html_escape(a), html_escape(b)),
            )
        if html:
            return linesep.join(html)


    Products.CMFDiffTool.TextDiff.TextDiff.inline_diff = text_inline_diff


    if has_namedfile:

        def namedfile_inline_diff(self):
            css_class = 'InlineDiff'
            old = self._parseField(self.oldValue, self.oldFilename)[0]
            new = self._parseField(self.newValue, self.newFilename)[0]

            return '' if self.same else self.inlinediff_fmt % (css_class, html_escape(old), html_escape(new))


        Products.CMFDiffTool.namedfile.NamedFileBinaryDiff.inline_diff = namedfile_inline_diff


        def namedfilelist_inline_diff(self):
            if self.same:
                return None

            css_class = 'InlineDiff'

            old_reprs = self._parseField(self.oldValue, None)
            new_reprs = self._parseField(self.newValue, None)

            old_data = [
                {'repr': repr, 'data': value.data, 'filename': value.filename}
                for (repr, value) in zip(old_reprs, self.oldValue or [])
            ]
            new_data = [
                {'repr': repr, 'data': value.data, 'filename': value.filename}
                for (repr, value) in zip(new_reprs, self.newValue or [])
            ]

            dummy_dict = {'repr': '', 'data': None, 'filename': None}
            make_lists_same_length(old_data, new_data, dummy_dict)

            def is_same_dict(d1, d2):
                return is_same(
                    d1['data'], d1['filename'], d2['data'], d2['filename'],
                )

            return '\n'.join([
                ((self.same_fmt % (css_class, html_escape(d_old['repr'])))
                    if is_same_dict(d_old, d_new) else self.inlinediff_fmt
                    % (css_class, html_escape(d_old['repr']), html_escape(d_new['repr']))
                    ) for (d_old, d_new) in zip(old_data, new_data)])


        Products.CMFDiffTool.namedfile.NamedFileListDiff.inline_diff = namedfilelist_inline_diff
