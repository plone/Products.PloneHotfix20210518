# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.PloneHotfix20210518.tests import BaseTest

import unittest


try:
    from plone.app.users.schema import IUserDataSchema
except ImportError:
    IUserDataSchema = None


@unittest.skipIf(IUserDataSchema is None, "p.a.user fullname tests skipped on 4.3")
class TestAttackVector(BaseTest):
    def test_registering_user(self):
        # Test that registering a user works.
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url() + "/@@register")
        browser.getControl(name="form.widgets.fullname").value = "Joe"
        browser.getControl(name="form.widgets.email").value = "joe@example.org"
        browser.getControl(name="form.widgets.username").value = "joe"
        browser.getControl(name="form.buttons.register").click()
        portal_membership = getToolByName(self.portal, "portal_membership")
        self.assertTrue(portal_membership.getMemberById("joe"))

    def test_original_constraint(self):
        # Check that our new constraint leaves the original constraint intact.
        # A newline in the fullname should not be accepted.
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url() + "/@@register")
        browser.getControl(name="form.widgets.fullname").value = "Joe\nCarioca"
        browser.getControl(name="form.widgets.email").value = "joe@example.org"
        browser.getControl(name="form.widgets.username").value = "joe"
        browser.getControl(name="form.buttons.register").click()
        self.assertIn("Invalid fullname.", browser.contents)
        portal_membership = getToolByName(self.portal, "portal_membership")
        self.assertIsNone(portal_membership.getMemberById("joe"))

    def test_xss_from_fullname(self):
        # We disallow any '<', because that might mean <script> gets accepted.
        # This is handled fine in most cases, but not everywhere,
        # leading to possible cross site scripting.
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url() + "/@@register")
        browser.getControl(name="form.widgets.fullname").value = "Joe <3 Plone"
        browser.getControl(name="form.widgets.email").value = "joe@example.org"
        browser.getControl(name="form.widgets.username").value = "joe"
        browser.getControl(name="form.buttons.register").click()
        self.assertIn("Invalid fullname.", browser.contents)
        portal_membership = getToolByName(self.portal, "portal_membership")
        self.assertIsNone(portal_membership.getMemberById("joe"))

    def test_xss_from_personal_information(self):
        # The above tests are for the registration form.
        # Try editing.  Easiest is to let the admin try this.
        browser = self.get_admin_browser()
        browser.open(self.portal.absolute_url() + "/@@personal-information")
        browser.getControl(
            name="form.widgets.fullname"
        ).value = "Admin >The Boss< Plone"
        browser.getControl(name="form.buttons.save").click()
        self.assertIn("Invalid fullname.", browser.contents)
        portal_membership = getToolByName(self.portal, "portal_membership")
        admin = portal_membership.getMemberById("admin")
        self.assertFalse(admin.getProperty("fullname"))
