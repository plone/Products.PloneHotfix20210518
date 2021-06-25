# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from Products.PloneHotfix20210518.tests import BaseTest
from plone.testing.z2 import Browser
from zExceptions import NotFound

import transaction


# We want to avoid hackers getting script tags inserted.
# But for example an ampersand is okay as long as it is escaped,
# although it should not be doubly escaped, because that looks wrong.
NORMAL_TEXT = "Smith & Jones"
ESCAPED_TEXT = "Smith &amp; Jones"
DOUBLY_ESCAPED_TEXT = "Smith &amp;amp; Jones"
# For script tags, we could either escape them or filter them
# using the safe html filter.
HACKED = 'The <script>alert("hacker")</script> was here.'


class TestAttackVector(BaseTest):
    def get_browser(self):
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        return browser

    def test_ampersand(self):
        self.portal.invokeFactory(
            "Folder",
            id="folder1",
            title=NORMAL_TEXT,
            description=NORMAL_TEXT,
            creators=(NORMAL_TEXT,),
            contributors=(NORMAL_TEXT,),
        )
        folder1 = self.portal.folder1
        self.assertEqual(folder1.Title(), NORMAL_TEXT)
        self.assertEqual(folder1.Description(), NORMAL_TEXT)
        folder1.invokeFactory(
            "Document",
            id="page1",
            title=NORMAL_TEXT,
            description=NORMAL_TEXT,
            creators=(NORMAL_TEXT,),
            contributors=(NORMAL_TEXT,),
        )
        page1 = folder1.page1
        self.assertEqual(page1.Title(), NORMAL_TEXT)
        self.assertEqual(page1.Description(), NORMAL_TEXT)
        transaction.commit()

        # Check the output.
        browser = self.get_browser()
        browser.open(folder1.absolute_url())
        self.assert_only_escaped_text(browser)
        browser.open(page1.absolute_url())
        self.assert_only_escaped_text(browser)
        browser.open(folder1.absolute_url() + "/folder_contents")
        self.assert_only_escaped_text(browser)

        # The next exists only on Plone 5.0+.
        try:
            browser.open(folder1.absolute_url() + "/@@fc-contextInfo")
        except NotFound:
            pass
        else:
            self.assert_only_escaped_text(browser)

    def test_xss(self):
        self.portal.invokeFactory(
            "Folder",
            id="folder1",
            title=HACKED,
            description=HACKED,
            creators=(HACKED,),
            contributors=(HACKED,),
        )
        folder1 = self.portal.folder1
        self.assertEqual(folder1.Title(), HACKED)
        # With good old Archetypes the description gets cleaned up to
        # 'The  alert("hacker")  was here.'
        # self.assertEqual(folder1.Description(), HACKED)
        folder1.invokeFactory(
            "Document",
            id="page1",
            title=HACKED,
            description=HACKED,
            creators=(HACKED,),
            contributors=(HACKED,),
        )
        page1 = folder1.page1
        self.assertEqual(page1.Title(), HACKED)
        # self.assertEqual(page1.Description(), HACKED)
        transaction.commit()

        # Check the output.
        browser = self.get_browser()
        browser.open(folder1.absolute_url())
        self.assert_not_in(HACKED, browser.contents)
        browser.open(page1.absolute_url())
        self.assert_not_in(HACKED, browser.contents)
        browser.open(folder1.absolute_url() + "/folder_contents")
        self.assert_not_in(HACKED, browser.contents)

        # The next exists only on Plone 5.0+.
        try:
            browser.open(folder1.absolute_url() + "/@@fc-contextInfo")
        except NotFound:
            pass
        else:
            self.assert_not_in(HACKED, browser.contents)

    def assert_only_escaped_text(self, browser):
        body = browser.contents
        # The escaped version of the text text should be in the response text.
        self.assertIn(ESCAPED_TEXT, body)
        # The normal version should not.
        self.assert_not_in(NORMAL_TEXT, body)
        # We should avoid escaping twice.
        # But on Plone 5.0 and 5.1 I get this in the html head and body:
        # "http://nohost/plone/author/Smith &amp;amp; Jones"
        # That has got nothing to do with what we are fixing here.
        # So only test this for the folder contents json url that we care about.
        if browser.url.endswith("/@@fc-contextInfo"):
            self.assert_not_in(DOUBLY_ESCAPED_TEXT, body)

    def assert_not_in(self, target, body):
        # This gives a too verbose error message, showing the entire body:
        # self.assertNotIn("x", body)
        # So we roll our own less verbose version.
        if target not in body:
            return
        index = body.index(target)
        start = max(0, index - 50)
        end = min(index + len(target) + 50, len(body))
        assert False, "Text '{0}' unexpectedly found in body: ... {1} ...".format(
            target, body[start:end]
        )
