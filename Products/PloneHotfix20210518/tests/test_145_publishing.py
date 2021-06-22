# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from OFS.Folder import Folder
from plone.app.testing import logout
from Products.CMFCore.utils import getToolByName
from Products.PloneHotfix20210518.tests import BaseTest
from zExceptions import NotFound
from zExceptions import Unauthorized

import transaction


class TestAttackVector(BaseTest):
    def test_plonetool(self):
        base_url = self.portal.absolute_url() + "/plone_utils"
        browser = self.get_admin_browser()
        method_names = (
            "addPortalMessage",
            "browserDefault",
            "getReviewStateTitleFor",
            "portal_utf8",
            "urlparse",
            "urlunparse",
            "utf8_portal",
            "getOwnerName",
            "normalizeString",
            "getEmptyTitle",
        )
        for method_name in method_names:
            with self.assertRaises(NotFound):
                browser.open(base_url + "/" + method_name)

    def test_old_hotfix(self):
        """Test old hotfix.

        CMFPlone has patches/publishing.py, containing
        the publishing patch from Products.PloneHotfix20160419.
        This avoids publishing some methods inherited from Zope or CMF,
        which upstream does not want to fix, considering it no problem
        to have these methods available.  I can imagine that.
        But in Plone we have decided otherwise.

        Problem: the patch does not work on Python 3.
        """
        self.portal.invokeFactory("Document", "doc")
        transaction.commit()
        portal_url = self.portal.absolute_url()
        doc_url = self.portal.doc.absolute_url()
        browser = self.get_admin_browser()
        method_names = (
            "EffectiveDate",
            "ExpirationDate",
            "getAttributes",
            "getChildNodes",
            "getFirstChild",
            "getLastChild",
            "getLayout",
            "getNextSibling",
            "getNodeName",
            "getNodeType",
            "getNodeValue",
            "getOwnerDocument",
            "getParentNode",
            "getPhysicalPath",
            "getPreviousSibling",
            "getTagName",
            "hasChildNodes",
            "Type",
            # From PropertyManager:
            "getProperty",
            "propertyValues",
            "propertyItems",
            "propertyMap",
            "hasProperty",
            "getPropertyType",
            "propertyIds",
            "propertyLabel",
            "propertyDescription",
        )
        for method_name in method_names:
            with self.assertRaises(NotFound):
                browser.open(portal_url + "/" + method_name)
            with self.assertRaises(NotFound):
                browser.open(doc_url + "/" + method_name)

    def test_pas(self):
        pas = self.portal.acl_users
        plugin = pas.source_users
        roles = pas.portal_role_manager
        browser = self.get_admin_browser()
        pas_methods = (
            "applyTransform",
            "lower",
            "upper",
        )
        pas_url = pas.absolute_url()
        plugin_url = plugin.absolute_url()
        roles_url = roles.absolute_url()
        # I don't really mind if these raise NotFound or Unauthorized,
        # as long as they raise something.
        for method_name in pas_methods:
            with self.assertRaises(Unauthorized):
                browser.open(pas_url + "/" + method_name + "?value=hello")
            with self.assertRaises(Unauthorized):
                browser.open(plugin_url + "/" + method_name + "?value=hello")
        with self.assertRaises(Exception) as cm:
            browser.open(roles_url + "/enumerateRoles")
        self.assertIsInstance(cm.exception, (NotFound, Unauthorized))

    def test_setup_tool(self):
        setup_tool = self.portal.portal_setup
        logs = [x for x in setup_tool.objectIds("File")]
        self.assertTrue(len(logs) > 0)
        base_url = setup_tool.absolute_url()

        # Try as admin.
        browser = self.get_admin_browser()
        try:
            browser.open(base_url)
        except TypeError:
            # On Plone 5.2.1 I get:
            # TypeError: 'ReplaceableWrapper' object is not callable
            pass

        for log in logs:
            browser.open(base_url + "/" + log)

        # Try as anonymous.
        browser = self.get_anon_browser()
        # Here Unauthorized is not raised, but this is not so bad.
        # with self.assertRaises(Unauthorized):
        #     browser.open(base_url)
        for log in logs:
            with self.assertRaises(Unauthorized):
                browser.open(base_url + "/" + log)

    def test_snapshot(self):
        from Products.GenericSetup.context import SnapshotExportContext

        setup_tool = self.portal.portal_setup
        snapshot_id = "snap"
        # This easily fails for various reasons:
        # result = setup_tool.createSnapshot(snapshot_id)
        context = SnapshotExportContext(setup_tool, snapshot_id)
        # I wanted to export typeinfo, but viewing those files gives errors,
        # even for admin, so let me add some files manually.
        # handler = setup_tool.getExportStep("typeinfo")
        # handler(context)
        context.writeDataFile("one.xml", "<xml>text one</xml>", "text/xml")
        context.writeDataFile(
            "two.js", "{'js': 'two'}", "application/javascript", subdir="sub"
        )
        context.writeDataFile("special/three.xml", "text three", "text/plain")
        context.writeDataFile(
            "special/four.xml", "text four", "text/plain", subdir="sub"
        )
        snapshot_folder = context.getSnapshotFolder()
        transaction.commit()

        # Try as admin and anonymous.
        self.view_object_or_items(snapshot_folder)

    def view_object_or_items(self, obj):
        admin_browser = self.get_admin_browser()
        anon_browser = self.get_anon_browser()
        if not isinstance(obj, Folder):
            admin_browser.open(obj.absolute_url())
            with self.assertRaises(Unauthorized):
                anon_browser.open(obj.absolute_url())
            return
        # You could try viewing the folder, but there is nothing to see, really:
        # you just get a standard Plone template rendered with nothing interesting in it.
        # So it is okay if anonymous can view it.
        # So try the sub objects.
        for sub in obj.objectValues():
            self.view_object_or_items(sub)


class TestSkinsTool(BaseTest):
    def test_getSkinNameFromRequest(self):
        # Test adapted from Products.CMFCore 2.5.1.
        stool = self.portal.portal_skins

        # by default, no special skin name is set
        self.assertEqual(self.portal.getSkinNameFromRequest(self.request), None)

        # provide a value, but at this point that skin is not registered
        self.request[stool.getRequestVarname()] = "skinA"
        self.assertEqual(self.portal.getSkinNameFromRequest(self.request), None)

        # After registering the skin name ``skinA`` it will be found
        stool.addSkinSelection("skinA", ("foo", "bar"))
        self.assertEqual(self.portal.getSkinNameFromRequest(self.request), "skinA")

        # test for non-existent http header variable
        # see https://dev.plone.org/ticket/10071
        stool.request_varname = "HTTP_SKIN_NAME"
        self.assertEqual(self.portal.getSkinNameFromRequest(self.request), None)

        # test for http header variable
        self.request["HTTP_SKIN_NAME"] = "skinB"
        stool.addSkinSelection("skinB", ("bar, foo"))
        self.assertEqual(self.portal.getSkinNameFromRequest(self.request), "skinB")


class QITests(BaseTest):
    def test_instance_security(self):
        qi = getToolByName(self.portal, "portal_quickinstaller", None)
        if qi is None:
            return

        # We are logged in, with role Manager.
        sm = getSecurityManager()
        self.assertIn("Manager", sm.getUser().getRoles())
        self.assertTrue(sm.checkPermission("View", qi))
        for obj in qi.objectValues():
            self.assertTrue(sm.checkPermission("View", obj))

        # Now go anonymous.
        logout()
        sm = getSecurityManager()
        self.assertNotIn("Manager", sm.getUser().getRoles())

        # The View permissin check fails on 5.1 and lower.
        # 5.2.4 already contains the fix, so it passes there.
        # self.assertFalse(sm.checkPermission("View", qi))
        # for obj in qi.objectValues():
        #     self.assertFalse(sm.checkPermission("View", obj))
        # TODO: this means that with an xmlrpc call you could still access them.
        # At least accessing QI already gives you a nice dictionary.

        # But I finally realized that we can also check if traversal would work.
        # Unrestricted traversal should work, restricted not.
        qi = self.portal.unrestrictedTraverse("portal_quickinstaller")
        with self.assertRaises(Unauthorized):
            self.portal.restrictedTraverse("portal_quickinstaller")
        for obj_id in qi.objectIds():
            qi.unrestrictedTraverse(obj_id)
            with self.assertRaises(Unauthorized):
                qi.restrictedTraverse(obj_id)
