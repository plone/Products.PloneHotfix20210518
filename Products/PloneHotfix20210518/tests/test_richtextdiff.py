# -*- coding: utf-8 -*-
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.textfield.value import RichTextValue
from Products.CMFDiffTool.CMFDTHtmlDiff import CMFDTHtmlDiff
from Products.CMFDiffTool.interfaces import IDifference

import unittest


class DummyType(object):
    def __init__(self, body):
        self.body = body


class RichTextDiffTestCase(unittest.TestCase):
    """Test RichTextDiff"""
    layer = PLONE_INTEGRATION_TESTING

    def test_parseField_value_is_none(self):
        value = None
        diff = CMFDTHtmlDiff(DummyType(value), DummyType(value), 'body')
        self.assertEqual(diff._parseField(value), [])

    def test_parseField_value_is_not_none(self):
        value = RichTextValue(u'foo')
        diff = CMFDTHtmlDiff(DummyType(value), DummyType(value), 'body')
        self.assertEqual(diff._parseField(value), [u'foo'])

    def test_inline_diff_same(self):
        value = RichTextValue(u'foo')
        diff = CMFDTHtmlDiff(DummyType(value), DummyType(value), 'body')
        inline_diff = diff.inline_diff()

        self.assertTrue(IDifference.providedBy(diff))
        self.assertEqual(diff.same, True)
        self.assertEqual(inline_diff, u'foo ')

    def test_inline_diff_same_hacker(self):
        value = RichTextValue(u'<script>alert("Hacker value")</script>')
        diff = CMFDTHtmlDiff(DummyType(value), DummyType(value), 'body')
        inline_diff = diff.inline_diff()
        # The script tag should not be escaped, but totally not shown.
        self.assertNotIn("<script", inline_diff)
        self.assertNotIn("&gt;", inline_diff)

    def test_inline_diff_different(self):
        old_value = RichTextValue(u'foo')
        new_value = RichTextValue(u'foo bar')
        diff = CMFDTHtmlDiff(
            DummyType(old_value), DummyType(new_value), 'body')

        inline_diff = diff.inline_diff()

        self.assertTrue(IDifference.providedBy(diff))
        self.assertEqual(diff.same, False)
        self.assertEqual(inline_diff, u'foo <span class="insert">bar </span> ')

    def test_inline_diff_different_hacker(self):
        old_value = RichTextValue(u'clean')
        new_value = RichTextValue(u'<script>alert("Hacker value")</script>')
        diff = CMFDTHtmlDiff(DummyType(old_value), DummyType(new_value), 'body')
        inline_diff = diff.inline_diff()
        # The script tag should not be escaped, but totally not shown.
        self.assertNotIn("<script", inline_diff)
        self.assertNotIn("&gt;", inline_diff)

        old_value = RichTextValue(u'<script>alert("Hacker value")</script>')
        new_value = RichTextValue(u'clean')
        diff = CMFDTHtmlDiff(DummyType(old_value), DummyType(new_value), 'body')
        inline_diff = diff.inline_diff()
        # The script tag should not be escaped, but totally not shown.
        self.assertNotIn("<script", inline_diff)
        self.assertNotIn("&gt;", inline_diff)
