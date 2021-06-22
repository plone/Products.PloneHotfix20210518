import unittest


try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib


class FauxResponse(object):
    def __init__(self):
        self._headers = {}
        self._body = None

    def setBody(self, body):
        self._body = body

    def setHeader(self, name, value):
        self._headers[name] = value

    def setStatus(self, status):
        self._status = status


class FauxInstance(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


class XMLRPCResponseTests(unittest.TestCase):
    """Adapted from Zope 4.5.5 src/ZPublisher/tests/test_xmlrpc.py

    Note: Plone 5.2.4 already contains Zope 4.5.5, so it already includes the fix.
    """

    def _getTargetClass(self):
        try:
            from ZPublisher.xmlrpc import Response
        except ImportError:
            from ZServer.ZPublisher.xmlrpc import Response
        return Response

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_instance_security(self):
        # Make sure instances' Zope permission settings are respected
        from AccessControl.Permissions import view
        from OFS.Folder import Folder
        from OFS.Image import manage_addFile

        folder = Folder("folder")
        manage_addFile(folder, "file1")
        folder.file1.manage_permission(view, ("Manager",), 0)
        manage_addFile(folder, "file2")
        folder.file2.manage_permission(view, ("Manager", "Anonymous"), 0)

        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(folder)
        data, method = xmlrpclib.loads(faux._body)

        self.assertFalse("file1" in data[0].keys())
        self.assertTrue("file2" in data[0].keys())
