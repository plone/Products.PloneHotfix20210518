# -*- coding: utf-8 -*-
from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import applyTheme
from plone.app.theming.utils import getTheme
from plone.registry.interfaces import IRegistry
from Products.PloneHotfix20210518.tests import AcceptanceTest
from zope.component import getUtility

import os
import pkg_resources
import tempfile
import transaction


THEMING_VERSION = pkg_resources.get_distribution("plone.app.theming").version

# We will try to let the rules file point to a theme on the file system.
# For security reasons, this should not work.
RULES = """<?xml version="1.0" encoding="UTF-8"?>
<rules
    xmlns="http://namespaces.plone.org/diazo"
    xmlns:css="http://namespaces.plone.org/diazo/css"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <theme href="{0}" />
</rules>
"""
# The theme will contain a message:
MESSAGE = u"Hello from a temporary directory."
# We have a sample theme file here:
HERE = os.path.dirname(__file__)
PACKAGE_THEME_FILENAME = "package_theme.txt"
PACKAGE_THEME = os.path.join(HERE, PACKAGE_THEME_FILENAME)


class TestAttackVector(AcceptanceTest):
    def setUp(self):
        self.portal = self.layer["portal"]
        rules_fd, self.rules_file = tempfile.mkstemp(
            suffix=".xml", prefix="rules", text=True
        )
        with open(self.rules_file, "w") as myfile:
            myfile.write(MESSAGE)
        # On Plone 4.3 we need to enable theming itself.
        settings = getUtility(IRegistry).forInterface(IThemeSettings, False)
        settings.enabled = True

    def tearDown(self):
        os.remove(self.rules_file)

    def test_failing_file_protocol_resolver(self):
        from plone.app.theming.utils import FailingFileProtocolResolver

        resolver = FailingFileProtocolResolver()
        with self.assertRaises(ValueError):
            resolver.resolve("file:///etc/passwd", "public_id", "context")
        with self.assertRaises(ValueError):
            resolver.resolve(
                "file:" + os.path.relpath("/etc/passwd"), "public_id", "context"
            )
        with self.assertRaises(ValueError):
            resolver.resolve("file://" + self.rules_file, "public_id", "context")
        with self.assertRaises(ValueError):
            resolver.resolve(
                "file:" + os.path.relpath(self.rules_file), "public_id", "context"
            )

    def test_failing_file_system_resolver(self):
        from plone.app.theming.utils import FailingFileSystemResolver

        resolver = FailingFileSystemResolver()
        with self.assertRaises(ValueError):
            resolver.resolve("/etc/passwd", "public_id", "context")
        with self.assertRaises(ValueError):
            resolver.resolve(os.path.relpath("/etc/passwd"), "public_id", "context")
        with self.assertRaises(ValueError):
            resolver.resolve(self.rules_file, "public_id", "context")
        with self.assertRaises(ValueError):
            resolver.resolve(os.path.relpath(self.rules_file), "public_id", "context")

    def new_theme(self, theme_path):
        from plone.app.theming.utils import createThemeFromTemplate
        from plone.resource.directory import PersistentResourceDirectory

        # Start with an empty theme.
        # Pass title and description
        theme_name = createThemeFromTemplate("Security", "")
        theme = getTheme(theme_name)
        directory = PersistentResourceDirectory()
        directory.writeFile(
            "/".join(["theme", theme_name, "rules.xml"]), RULES.format(theme_path)
        )
        applyTheme(theme)
        transaction.commit()

    def test_theme_file_system_absolute(self):
        self.new_theme(self.rules_file)
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url())
        self.assertNotIn(MESSAGE, browser.contents)

    def test_theme_file_system_relative(self):
        self.new_theme(os.path.relpath(self.rules_file))
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url())
        self.assertNotIn(MESSAGE, browser.contents)

    def test_theme_file_protocol_absolute(self):
        self.new_theme("file://" + self.rules_file)
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url())
        self.assertNotIn(MESSAGE, browser.contents)

    def test_theme_file_protocol_relative(self):
        # This is actually handled by the InternalResolver.
        # Well, in fact it gives an error because it cannot resolve it in the Plone Site:
        # AttributeError: 'PersistentResourceDirectory' object has no attribute 'getPhysicalPath'
        # This can be seen when previewing the theme in the theme editor.
        self.new_theme("file:" + os.path.relpath(self.rules_file))
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url())
        self.assertNotIn(MESSAGE, browser.contents)

    def test_theme_python_protocol(self):
        # Since our example rules file is in a Python package,
        # we can use the python resolver to access it.
        # I don't think we can avoid this.
        self.new_theme(
            "python://Products.PloneHotfix20210518/tests/" + PACKAGE_THEME_FILENAME
        )
        with open(PACKAGE_THEME) as myfile:
            contents = myfile.read()
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url())
        self.assertIn(contents, browser.contents)

    def test_available_themes(self):
        """Test that all available themes render properly.

        Our security fixes should not break them.

        But preview was broken in plone.app.theming 4.0.4,
        Plone 5.2.1.
        See https://github.com/plone/plone.app.theming/issues/173
        """
        from plone.app.theming.utils import getAvailableThemes

        for theme in getAvailableThemes():
            applyTheme(theme)
            transaction.commit()
            # Can you view the portal anonymously?
            browser = self.get_anon_browser()
            browser.open(self.portal.absolute_url())
            # Can you see the preview as admin?
            # This can give errors that are otherwise swallowed by the
            # diazo/theming transform, effectively disabling the theme.
            if THEMING_VERSION == "4.0.4":
                continue
            browser = self.get_admin_browser()
            browser.open(
                self.portal.absolute_url()
                + theme.absolutePrefix
                + "/@@theming-controlpanel-mapper-getframe?path=/&theme=apply"
                + "&forms=disable&links=replace&title=Preview"
            )
