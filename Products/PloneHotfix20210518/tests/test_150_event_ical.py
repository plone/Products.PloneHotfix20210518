# -*- coding: utf-8 -*-
from Products.PloneHotfix20210518.tests import BaseTest

import transaction


try:
    # Available since at least plone.app.event 1.0rc1
    from plone.app.event.ical.importer import IIcalendarImportSettings
except ImportError:
    IIcalendarImportSettings = None

import unittest


@unittest.skipIf(IIcalendarImportSettings is None, "p.a.event ical tests skipped")
class TestAttackVector(BaseTest):
    def test_constraint(self):
        self.portal.invokeFactory("Folder", "f1")
        f1 = self.portal["f1"]
        f1_url = f1.absolute_url()
        transaction.commit()

        # Enable ical import.
        browser = self.get_admin_browser()
        browser.open(f1_url + "/ical_import_settings/enable")
        try:
            browser.getControl("Confirm action").click()
        except LookupError:
            # On 4.3 with plone.app.contenttypes, the action already happens on GET,
            # without needing to click Confirm action.
            pass

        # Set it to a file url.
        browser.open(f1_url + "/ical_import_settings")
        self.assertIn("URL to an external icalendar resource file", browser.contents)
        browser.getControl(name="form.widgets.ical_url").value = "file:///tmp/test.ical"
        browser.getControl(name="form.buttons.save").click()
        self.assertIn("URLs with file: are not allowed.", browser.contents)
