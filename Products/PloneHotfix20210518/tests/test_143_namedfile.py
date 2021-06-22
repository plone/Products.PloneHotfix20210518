# -*- coding: utf-8 -*-
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from Products.CMFPlone.utils import safe_unicode
from Products.PloneHotfix20210518.tests import BaseTest

import os
import transaction
import unittest


try:
    from plone import dexterity
except ImportError:
    dexterity = None


def get_disposition_header(browser):
    # Could be CamelCase or all lowercase.
    name = "Content-Disposition"
    if name in browser.headers.keys():
        return browser.headers.get(name)
    name = name.lower()
    return browser.headers.get(name, None)


# Note: Archetypes does not have the problem that we fix here.
@unittest.skipIf(dexterity is None, "namedfile tests skipped without dexterity (4.3)")
class TestAttackVectorNamedImage(BaseTest):
    field_class = NamedImage
    portal_type = "Image"
    field_name = "image"

    def _named_file(self, name):
        with open(os.path.join(os.path.dirname(__file__), name), "rb") as myfile:
            data = myfile.read()
        return self.field_class(data, filename=safe_unicode(name))

    def assert_download_works(self, base_url):
        browser = self.get_anon_browser()
        browser.open(base_url + "/@@download")
        header = get_disposition_header(browser)
        self.assertIsNotNone(header)
        self.assertIn("attachment", header)
        self.assertIn("filename", header)

    def assert_display_inline_works(self, base_url):
        # Test that displaying this file inline works.
        browser = self.get_anon_browser()
        browser.open(base_url)
        self.assertIsNone(get_disposition_header(browser))
        # Explicitly try the display-file view.
        browser.open(base_url + "/@@display-file")
        self.assertIsNone(get_disposition_header(browser))

    def assert_display_inline_is_download(self, base_url):
        # Test that displaying this file inline turns into a download.
        browser = self.get_anon_browser()
        browser.open(base_url)
        header = get_disposition_header(browser)
        self.assertIsNotNone(header)
        self.assertIn("attachment", header)
        self.assertIn("filename", header)
        # Explicitly try the display-file view.
        browser.open(base_url + "/@@display-file")
        header = get_disposition_header(browser)
        self.assertIsNotNone(header)
        self.assertIn("attachment", header)
        self.assertIn("filename", header)

    def test_png_image(self):
        obj_id = self.portal.invokeFactory(
            self.portal_type,
            "image-png",
            **{self.field_name: self._named_file("image.png")}
        )
        transaction.commit()
        base_url = "/".join([self.portal.absolute_url(), obj_id])
        self.assert_download_works(base_url)
        self.assert_display_inline_works(base_url)

    def test_svg_image(self):
        obj_id = self.portal.invokeFactory(
            self.portal_type,
            "image-svg",
            **{self.field_name: self._named_file("image.svg")}
        )
        transaction.commit()
        base_url = "/".join([self.portal.absolute_url(), obj_id])
        self.assert_download_works(base_url)
        self.assert_display_inline_is_download(base_url)

    def test_filename_none(self):
        # A 'None' filename None probably does not happen during normal upload,
        # but if an attacker manages this, even @@download will show inline.
        data = self._named_file("image.svg")
        data.filename = None
        obj_id = self.portal.invokeFactory(
            self.portal_type, "image-svg", **{self.field_name: data}
        )
        transaction.commit()
        base_url = "/".join([self.portal.absolute_url(), obj_id])
        self.assert_download_works(base_url)
        self.assert_display_inline_is_download(base_url)

    def test_filename_empty(self):
        # An empty filename is probably no problem, but let's check.
        data = self._named_file("image.svg")
        data.filename = u""
        obj_id = self.portal.invokeFactory(
            self.portal_type, "image-svg", **{self.field_name: data}
        )
        transaction.commit()
        base_url = "/".join([self.portal.absolute_url(), obj_id])
        self.assert_download_works(base_url)
        self.assert_display_inline_is_download(base_url)


class TestAttackVectorNamedBlobImage(TestAttackVectorNamedImage):
    field_class = NamedBlobImage


class TestAttackVectorNamedFile(TestAttackVectorNamedImage):
    field_class = NamedFile
    portal_type = "File"
    field_name = "file"

    def test_html_file(self):
        obj_id = self.portal.invokeFactory(
            self.portal_type,
            "html-file",
            file=self.field_class(
                "<h1>Attacker</h1>", filename=safe_unicode("attacker.html")
            ),
        )
        transaction.commit()
        base_url = "/".join([self.portal.absolute_url(), obj_id])
        self.assert_download_works(base_url)
        self.assert_display_inline_is_download(base_url)

    def test_pdf(self):
        # By popular request we allow PDF.
        obj_id = self.portal.invokeFactory(
            self.portal_type,
            "pdf-file",
            **{self.field_name: self._named_file("file.pdf")}
        )
        transaction.commit()
        base_url = "/".join([self.portal.absolute_url(), obj_id])
        self.assert_download_works(base_url)
        self.assert_display_inline_works(base_url)


class TestAttackVectorNamedBlobFile(TestAttackVectorNamedFile):
    field_class = NamedBlobFile
