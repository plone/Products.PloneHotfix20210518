from Acquisition import aq_base
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from plone.testing.z2 import Browser
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
from zope.component import getUtility
from zope.configuration import xmlconfig
from ZPublisher import HTTPResponse

import os
import pkg_resources
import Products.PloneHotfix20210518
import re
import unittest


try:
    # Plone 5+
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:
    # Plone 4.3
    ISecuritySchema = None
try:
    # Plone 5+
    from Products.CMFPlone.interfaces.controlpanel import IMailSchema
except ImportError:
    # Plone 4.3
    IMailSchema = None
try:
    pkg_resources.get_distribution("plone.app.contenttypes")
except pkg_resources.DistributionNotFound:
    HAS_PACT = False
else:
    HAS_PACT = True
try:
    pkg_resources.get_distribution("plone.app.dexterity")
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True
try:
    pkg_resources.get_distribution("plone.protect")
except pkg_resources.DistributionNotFound:
    # When plone.protect is not there, we don't have to do anything special.
    def createToken():
        return ""
else:
    try:
        from plone.protect import createToken
    except ImportError:
        # Not all versions have factored out createToken.
        from plone.keyring.interfaces import IKeyManager
        from plone.protect.authenticator import _getUserName

        import hmac

        try:
            from hashlib import sha1 as sha
        except ImportError:
            import sha

        def createToken():
            manager = getUtility(IKeyManager)
            secret = manager.secret()
            user = _getUserName()
            return hmac.new(secret, user, sha).hexdigest()
try:
    pkg_resources.get_distribution("plone.app.theming")
except pkg_resources.DistributionNotFound:
    HAS_THEMING = False
else:
    HAS_THEMING = True


class HotfixLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Fix subrequest not fallbacking to wrong encoding in test environment:
        HTTPResponse.default_encoding = "utf-8"
        super(HotfixLayer, self).setUpZope(app, configurationContext)

        # Load previous hotfixes, if available.
        z2.installProduct(app, "Products.PloneHotfix20200121")

        # Load ZCML if we have it.
        if "configure.zcml" in os.listdir(
            os.path.dirname(Products.PloneHotfix20210518.__file__)
        ):
            xmlconfig.file(
                "configure.zcml", Products.PloneHotfix20210518, context=configurationContext
            )
        # Same for zcml in the tests directory.
        if "configure.zcml" in os.listdir(
            os.path.dirname(Products.PloneHotfix20210518.tests.__file__)
        ):
            xmlconfig.file(
                "configure.zcml", Products.PloneHotfix20210518.tests, context=configurationContext
            )

        if HAS_DEXTERITY:
            import plone.app.dexterity

            xmlconfig.file(
                "configure.zcml", plone.app.dexterity, context=configurationContext
            )

        if HAS_PACT:
            # prepare installing plone.app.contenttypes
            z2.installProduct(app, "Products.DateRecurringIndex")

            import plone.app.contenttypes

            xmlconfig.file(
                "configure.zcml", plone.app.contenttypes, context=configurationContext
            )

        if HAS_THEMING:
            import plone.app.theming

            xmlconfig.file(
                "configure.zcml", plone.app.theming, context=configurationContext
            )

    def setUpPloneSite(self, portal):
        super(HotfixLayer, self).setUpPloneSite(portal)

        if HAS_PACT:
            # Install into Plone site using portal_setup
            applyProfile(portal, "plone.app.contenttypes:default")
        if HAS_THEMING:
            # Install into Plone site using portal_setup
            applyProfile(portal, "plone.app.theming:default")

        # Enable self registration.
        registry = getUtility(IRegistry)
        if ISecuritySchema is not None:
            security_settings = registry.forInterface(ISecuritySchema, prefix="plone")
            security_settings.enable_self_reg = True
        # Handled via event handler usually:
        portal.manage_permission(
            "Add portal member",
            roles=["Anonymous", "Manager", "Site Administrator"],
            acquire=0,
        )

        # Setup mail settings
        if IMailSchema is not None:
            mail_settings = registry.forInterface(IMailSchema, prefix="plone")
            mail_settings.smtp_host = u"localhost"
            mail_settings.email_from_address = "admin@foo.com"
        else:
            portal.MailHost.smtp_host = u"localhost"
            portal._updateProperty("email_from_address", "admin@foo.com")

        # Setup mock mailhost
        portal._original_MailHost = portal.MailHost
        mail_host = MockMailHost("MailHost")
        mail_host.smtp_host = "localhost"
        portal.MailHost = mail_host
        site_manager = getSiteManager(portal)
        site_manager.unregisterUtility(provided=IMailHost)
        site_manager.registerUtility(mail_host, IMailHost)

    def tearDownPloneSite(self, portal):
        # login(portal, 'admin')

        portal.MailHost = portal._original_MailHost
        sm = getSiteManager(context=portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(portal._original_MailHost), provided=IMailHost)


HOTFIX_FIXTURE = HotfixLayer()
HOTFIX_PLONE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(HOTFIX_FIXTURE,), name="HotfixTesting:Functional"
)
HOTFIX_PLONE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(HOTFIX_FIXTURE,), name="HotfixTesting:Integration"
)
HOTFIX_PLONE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        HOTFIX_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='HotfixTesting:Acceptance',
)


class ThemingLayer(HotfixLayer):
    defaultBases = (HOTFIX_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # load ZCML
        import Products.PloneHotfix20210518.tests
        xmlconfig.file(
            'theming.zcml',
            Products.PloneHotfix20210518.tests,
            context=configurationContext
        )

        # Run the startup hook
        from plone.app.theming.plugins.hooks import onStartup
        onStartup(None)

    def setUpPloneSite(self, portal):
        # install into the Plone site
        applyProfile(portal, 'plone.app.theming:default')


class BaseTest(unittest.TestCase):
    layer = HOTFIX_PLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def create_private_document(self, doc_id):
        """Set workflow chain and create document."""
        wf_tool = self.portal.portal_workflow
        wf_tool.setChainForPortalTypes(["Document"], "simple_publication_workflow")
        self.portal.invokeFactory("Document", doc_id)
        return self.portal[doc_id]

    def get_admin_browser(self):
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        return browser

    def get_anon_browser(self):
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        return browser


class AcceptanceTest(BaseTest):
    # This is for when you need the server to run on an actual port.
    layer = HOTFIX_PLONE_ACCEPTANCE_TESTING


class ResponseWrapper:
    """Decorates a response object with additional introspective methods."""

    _bodyre = re.compile("\r\n\r\n(.*)", re.MULTILINE | re.DOTALL)

    def __init__(self, response, outstream, path):
        self._response = response
        self._outstream = outstream
        self._path = path

    def __getattr__(self, name):
        return getattr(self._response, name)

    def getOutput(self):
        """Returns the complete output, headers and all."""
        return self._outstream.getvalue()

    def getBody(self):
        """Returns the page body, i.e. the output par headers."""
        body = self._bodyre.search(self.getOutput())
        if body is not None:
            body = body.group(1)
        return body

    def getPath(self):
        """Returns the path used by the request."""
        return self._path

    def getHeader(self, name):
        """Returns the value of a response header."""
        return self.headers.get(name.lower())

    def getCookie(self, name):
        """Returns a response cookie."""
        return self.cookies.get(name)


class DummyTestCase(unittest.TestCase):
    """Dummy test case.

    Sometimes we want to override the entire test class because the
    thing it tests cannot be imported.  We need a dummy test then,
    otherwise we get an error:

    TypeError: Module X does not define any tests
    """

    def test_dummy(self):
        pass
