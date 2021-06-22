# -*- coding: utf-8 -*-
from ._compat import PY2
from ._compat import text_type
from .utils import protect_class
from AccessControl.Permissions import view
from AccessControl.Permissions import view_management_screens


try:
    from Products.GenericSetup.context import SnapshotExportContext
    from Products.GenericSetup.tool import SetupTool
except ImportError:
    SetupTool = None
    SnapshotExportContext = None

if SetupTool is not None:
    # Protect new Files and Folders in portal_setup.
    # This is for logs and snapshots.
    protect_class(SetupTool, view_management_screens)

    # Patch _createReport
    SetupTool._orig_createReport = SetupTool._createReport

    def _createReport(self, basename, steps, messages):
        """Record the results of a run."""
        self._orig_createReport(basename, steps, messages)
        # It would be cleaner (but a bit hard) to only protect the added File.
        # But really we want to protect them all.
        for ob in self.objectValues("File"):
            ob.manage_permission(view, ("Manager", "Owner"), 0)

    SetupTool._createReport = _createReport

    # Patch _ensureSnapshotsFolder
    SnapshotExportContext._orig_ensureSnapshotsFolder = (
        SnapshotExportContext._ensureSnapshotsFolder
    )

    def _ensureSnapshotsFolder(self, subdir=None):
        folder = self._orig_ensureSnapshotsFolder(subdir=subdir)
        folder.manage_permission(view, ("Manager", "Owner"), 0)
        return folder

    SnapshotExportContext._ensureSnapshotsFolder = _ensureSnapshotsFolder

    # Patch writeDataFile
    SnapshotExportContext._orig_writeDataFile = SnapshotExportContext.writeDataFile

    def writeDataFile(self, filename, text, content_type, subdir=None):
        """See IExportContext."""
        if subdir is not None:
            filename = "/".join((subdir, filename))

        sep = filename.rfind("/")
        if sep != -1:
            subdir = filename[:sep]
            filename = filename[sep + 1 :]

        # if six.PY2 and isinstance(text, six.text_type):
        if PY2 and isinstance(text, text_type):
            encoding = self.getEncoding() or "utf-8"
            text = text.encode(encoding)

        folder = self._ensureSnapshotsFolder(subdir)

        # MISSING: switch on content_type
        ob = self._createObjectByType(filename, text, content_type)
        folder._setObject(str(filename), ob)  # No Unicode IDs!
        # Tighten the View permission on the new object.
        # Only the owner and Manager users may view the log.
        # file_ob = self._getOb(name)
        ob.manage_permission(view, ("Manager", "Owner"), 0)

    SnapshotExportContext.writeDataFile = writeDataFile
