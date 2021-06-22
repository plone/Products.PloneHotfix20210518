# -*- coding: utf-8 -*-
from AccessControl.Permissions import view_management_screens
from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
# Expressions.boboAwareZopeTraverse is a function
# expression(s).BoboAwareZopeTraverse is a class
# Import them with names that are easier to tell apart.
from Products.PageTemplates.Expressions import boboAwareZopeTraverse as traverse_function
from Products.PageTemplates.Expressions import trustedBoboAwareZopeTraverse as trusted_traverse_function
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PloneHotfix20210518.tests import BaseTest
from zExceptions import NotFound
from zExceptions import Unauthorized

import AccessControl
import os
import random
import re
import string
import unittest


try:
    from AccessControl.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass

try:
    # Python 3.7+
    from random import _os
except ImportError:
    # Python 3.6- is not vulnerable.
    _os = None

try:
    # Zope 4 / Plone 5.2
    from Products.PageTemplates.expression import BoboAwareZopeTraverse as TraverseClass
    from Products.PageTemplates.expression import TrustedBoboAwareZopeTraverse as TrustedTraverseClass
except ImportError:
    try:
        # Plone 5.0 and 5.1.  Additionally Plone 4.3 if you have added five.pt yourself.
        from five.pt.expressions import BoboAwareZopeTraverse as TraverseClass
        from five.pt.expressions import TrustedBoboAwareZopeTraverse as TrustedTraverseClass
    except ImportError:
        # Plone 4.3 without five.pt
        TraverseClass = None
        TrustedTraverseClass = None


# Path of this directory:
path = os.path.dirname(__file__)


class DummyView(object):

    __name__ = "dummy-view"
    _authenticator = "secret"
    _ = "translation"


class DummyContent(SimpleItem):
    """Dummy content class to show the (un)restrictedTraverse works."""
    security = ClassSecurityInfo()

    @security.public
    def public(self):
        """Public method"""
        return "I am public"

    @security.private
    def private(self):
        """Private method"""
        return "I am private"

    @security.protected(view_management_screens)
    def protected(self):
        """Protected method"""
        return "I am protected"


InitializeClass(DummyContent)


class TestAttackVector(BaseTest):
    def _makeOne(self, name):
        return PageTemplateFile(os.path.join(path, name)).__of__(self.portal)

    @unittest.skipIf(_os is None, "This Python version has no random._os.")
    def test_template_bad1(self):
        template = self._makeOne("bad1.pt")
        # In some versions, random is not globally available, so we get a NameError.
        # Otherwise our patch should make sure we get a NotFound.
        with self.assertRaises((NotFound, NameError)):
            template()

    def test_template_bad2(self):
        template = self._makeOne("bad2.pt")
        with self.assertRaises(NotFound):
            template()

    def test_template_name(self):
        # Allow accessing __name__ in a skin template or TTW template.
        template = self._makeOne("options_view_name.pt")
        # Pass view in the options.
        self.assertIn("dummy-view", template(view=DummyView()))

    def test_template_authenticator(self):
        # Allow accessing _authenticator in a skin template or TTW template.
        template = self._makeOne("options_authenticator.pt")
        # Pass view in the options.
        self.assertIn("secret", template(view=DummyView()))

    def test_template_single_underscore(self):
        # Allow accessing '_' in a skin template or TTW template.
        # In the merge of the hotfix, Zope allows this, to avoid a test failure.
        template = self._makeOne("options_underscore.pt")
        # Pass view in the options.
        self.assertIn("translation", template(view=DummyView()))

    def test_browser_template_with_name(self):
        # Allow accessing __name__ in a browser view template.
        browser = self.get_anon_browser()
        browser.open(self.portal.absolute_url() + "/hotfix-testing-view-name")
        self.assertIn("<h1>hotfix-testing-view-name</h1>", browser.contents)

    def test_template_accesscontrol_sm(self):
        # Only AccessControl.getSecurityManager is allowed.
        template = self._makeOne("accesscontrol_sm.pt")
        self.assertIn("getSecurityManager is allowed", template())

    def test_template_accesscontrol_sm2(self):
        # Zope main.zpt uses modules/AccessControl/SecurityManagement/getSecurityManager
        # which should have been modules/AccessControl/getSecurityManager.
        # So we need a special case for it, otherwise the ZMI is totally inaccessible.
        template = self._makeOne("accesscontrol_sm2.pt")
        self.assertIn("getSecurityManager is still allowed", template())

    def test_template_accesscontrol_direct(self):
        # Via AccessControl you can access too much.
        template = self._makeOne("accesscontrol_direct.pt")
        with self.assertRaises(NotFound):
            template()

    def test_template_accesscontrol_via_modules(self):
        template = self._makeOne("accesscontrol_via_modules.pt")
        with self.assertRaises(NotFound):
            template()

    def test_template_accesscontrol_via_dict(self):
        template = self._makeOne("accesscontrol_via_dict.pt")
        with self.assertRaises(NotFound):
            template()


class TestDirectAttackVector(BaseTest):

    @unittest.skipIf(_os is None, "This Python version has no random._os.")
    def test_traverse_function_random(self):
        with self.assertRaises(NotFound):
            traverse_function(random, ("_os", "system"), None)
        # trusted traverse should work fine
        result = trusted_traverse_function(random, ("_os", "system"), None)
        self.assertEqual(result, os.system)

    def test_traverse_function_string(self):
        with self.assertRaises(NotFound):
            traverse_function(string, ("_re", "purge"), None)
        result = trusted_traverse_function(string, ("_re", "purge"), None)
        self.assertEqual(result, re.purge)

    def test_traverse_function_name(self):
        # We allow access to __name__ always as a special case.
        view = DummyView()
        self.assertEqual(traverse_function(view, ("__name__",), None), "dummy-view")
        self.assertEqual(trusted_traverse_function(view, ("__name__",), None), "dummy-view")

    def test_traverse_function_authenticator(self):
        # We allow access to _authenticator always as a special case.
        view = DummyView()
        self.assertEqual(traverse_function(view, ("_authenticator",), None), "secret")
        self.assertEqual(trusted_traverse_function(view, ("_authenticator",), None), "secret")

    def test_traverse_function_single_underscore(self):
        # We allow access to '_' always as a special case.
        view = DummyView()
        self.assertEqual(traverse_function(view, ("_",), None), "translation")
        self.assertEqual(trusted_traverse_function(view, ("_",), None), "translation")

    def test_traverse_function_content(self):
        content = DummyContent("dummy")
        self.assertEqual(traverse_function(content, ("public",), None)(), "I am public")
        with self.assertRaises(Unauthorized):
            traverse_function(content, ("private",), None)
        with self.assertRaises(Unauthorized):
            traverse_function(content, ("protected",), None)

        self.assertEqual(trusted_traverse_function(content, ("public",), None)(), "I am public")
        self.assertEqual(trusted_traverse_function(content, ("private",), None)(), "I am private")
        self.assertEqual(trusted_traverse_function(content, ("protected",), None)(), "I am protected")

    def test_traverse_function_accesscontrol_getSecurityManager(self):
        # Only getSecurityManager is allowed.
        self.assertEqual(traverse_function(AccessControl, ("getSecurityManager",), None), AccessControl.getSecurityManager)
        self.assertEqual(trusted_traverse_function(AccessControl, ("getSecurityManager",), None), AccessControl.getSecurityManager)

    def test_traverse_function_accesscontrol_getSecurityManager2(self):
        # Zope main.zpt uses modules/AccessControl/SecurityManagement/getSecurityManager
        # which should have been modules/AccessControl/getSecurityManager.
        # So we need a special case for it, otherwise the ZMI is totally inaccessible.
        self.assertEqual(traverse_function(AccessControl, ("SecurityManagement", "getSecurityManager"), None), AccessControl.getSecurityManager)
        self.assertEqual(trusted_traverse_function(AccessControl, ("SecurityManagement", "getSecurityManager",), None), AccessControl.getSecurityManager)

    def test_traverse_function_accesscontrol_direct(self):
        with self.assertRaises(NotFound):
            traverse_function(AccessControl, ("SecurityManagement",), None)
        self.assertEqual(trusted_traverse_function(AccessControl, ("SecurityManagement",), None), AccessControl.SecurityManagement)

    def test_traverse_function_accesscontrol_via_modules(self):
        from Products.PageTemplates.ZRPythonExpr import _SecureModuleImporter

        modules = _SecureModuleImporter()
        with self.assertRaises(NotFound):
            traverse_function(modules, ("AccessControl", "users"), None)
        self.assertEqual(trusted_traverse_function(modules, ("AccessControl", "users"), None), AccessControl.users)

    def test_traverse_function_accesscontrol_via_dict(self):
        piggyback = {"unsafe": AccessControl}
        with self.assertRaises(NotFound):
            traverse_function(piggyback, ("unsafe", "users"), None)
        self.assertEqual(trusted_traverse_function(piggyback, ("unsafe", "users"), None), AccessControl.users)

    @unittest.skipIf(_os is None or TraverseClass is None, "This Python version has no random._os or there is no BoboAwareZopeTraverse class.")
    def test_traverse_class_random(self):
        with self.assertRaises(NotFound):
            # Note: here the second argument is the request.  None works in the tests.
            TraverseClass.traverse(random, None, ("_os", "system"))
        # trusted traverse should work fine
        result = TrustedTraverseClass.traverse(random, None, ("_os", "system"))
        self.assertEqual(result, os.system)

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_string(self):
        with self.assertRaises(NotFound):
            TraverseClass.traverse(string, None, ("_re", "purge"))
        result = TrustedTraverseClass.traverse(string, None, ("_re", "purge"))
        self.assertEqual(result, re.purge)

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_name(self):
        # We allow access to __name__ always as a special case.
        view = DummyView()
        self.assertEqual(TraverseClass.traverse(view, None, ("__name__",)), "dummy-view")
        self.assertEqual(TrustedTraverseClass.traverse(view, None, ("__name__",)), "dummy-view")

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_content(self):
        content = DummyContent("dummy")
        self.assertEqual(TraverseClass.traverse(content, None, ("public",))(), "I am public")
        with self.assertRaises(Unauthorized):
            TraverseClass.traverse(content, None, ("private",))
        with self.assertRaises(Unauthorized):
            TraverseClass.traverse(content, None, ("protected",))

        self.assertEqual(TrustedTraverseClass.traverse(content, None, ("public",))(), "I am public")
        self.assertEqual(TrustedTraverseClass.traverse(content, None, ("private",))(), "I am private")
        self.assertEqual(TrustedTraverseClass.traverse(content, None, ("protected",))(), "I am protected")

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_accesscontrol_getSecurityManager(self):
        # AccessControl.getSecurityManager is the only item allowed.
        self.assertEqual(TraverseClass.traverse(AccessControl, None, ("getSecurityManager",)), AccessControl.getSecurityManager)
        self.assertEqual(TrustedTraverseClass.traverse(AccessControl, None, ("getSecurityManager",)), AccessControl.getSecurityManager)

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_accesscontrol_getSecurityManager2(self):
        self.assertEqual(TraverseClass.traverse(AccessControl, None, ("SecurityManagement", "getSecurityManager",)), AccessControl.getSecurityManager)
        self.assertEqual(TrustedTraverseClass.traverse(AccessControl, None, ("SecurityManagement", "getSecurityManager",)), AccessControl.getSecurityManager)

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_accesscontrol_direct(self):
        with self.assertRaises(NotFound):
            TraverseClass.traverse(AccessControl, None, ("SecurityManagement",))
        self.assertEqual(TrustedTraverseClass.traverse(AccessControl, None, ("SecurityManagement",)), AccessControl.SecurityManagement)

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_accesscontrol_via_modules(self):
        from Products.PageTemplates.ZRPythonExpr import _SecureModuleImporter

        modules = _SecureModuleImporter()
        with self.assertRaises(NotFound):
            TraverseClass.traverse(modules, None, ("AccessControl", "users"))
        self.assertEqual(TrustedTraverseClass.traverse(modules, None, ("AccessControl", "users")), AccessControl.users)

    @unittest.skipIf(TraverseClass is None, "There is no BoboAwareZopeTraverse class.")
    def test_traverse_class_accesscontrol_via_dict(self):
        piggyback = {"unsafe": AccessControl}
        with self.assertRaises(NotFound):
            TraverseClass.traverse(piggyback, None, ("unsafe", "users"))
        self.assertEqual(TrustedTraverseClass.traverse(piggyback, None, ("unsafe", "users")), AccessControl.users)
