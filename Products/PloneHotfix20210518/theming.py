from lxml import etree
from plone.app.theming import utils

import os


class FailingFileProtocolResolver(etree.Resolver):
    """Resolver that fails for security when file: urls are tried.

    Note: an earlier version only checked for "file://", not "file:",
    and did not catch relative paths.
    """
    def resolve(self, system_url, public_id, context):
        if system_url.startswith('file:') and system_url != 'file:///__diazo__':
            # The error will be caught by lxml and we only see this in the traceback:
            # XIncludeError: could not load <system_url>, and no fallback was found
            raise ValueError("File protocol access not allowed: '%s'" % system_url)


utils.FailingFileProtocolResolver = FailingFileProtocolResolver


class FailingFileSystemResolver(etree.Resolver):
    """Resolver that fails for security when accessing the file system.

    Problem 1: none of the current plone.app.theming resolvers
    resolve file system paths, and yet they get resolved.
    So somewhere in etree there is a fallback.

    Problem 2: the InternalResolver of plone.app.theming can resolve paths
    internal in the Plone Site.  If that happens, then our failing resolver
    should not be called.  But the order in which resolvers are called,
    seems random, so we cannot rely on the InternalResolver being called first.

    So what do we do?

    Situation:
    - The Plone Site has a theme.html in the site root.
    - On the file system there is a file theme.html in the root.

    Possibilities when resolving /theme.html:

    A. The InternalResolver is called first, and resolves it correctly.
    B. Our FailingFileSystemResolver is called first,
       sees that the file exists, and raises an error.

    In this situation, the resolving would randomly work and not work.
    This seems unavoidable, but also seems a corner case
    which will not happen very often.

    In case the file does not exist on the file system,
    our resolver should return nothing.
    Then the InternalResolver or other resolvers can have a go.
    """
    def resolve(self, system_url, public_id, context):
        if system_url and os.path.exists(system_url):
            # The error will be caught by lxml and we only see this in the traceback:
            # XIncludeError: could not load <system_url>, and no fallback was found
            raise ValueError("File system access not allowed: '%s'" % system_url)


utils.FailingFileProtocolResolver = FailingFileProtocolResolver
utils.FailingFileSystemResolver = FailingFileSystemResolver


def getParser(type, readNetwork):
    """Set up a parser for either rules, theme or compiler
    """
    if type == 'rules':
        parser = etree.XMLParser(recover=False, resolve_entities=False, remove_pis=True)
    elif type == 'theme':
        parser = etree.HTMLParser()
    elif type == 'compiler':
        parser = etree.XMLParser(resolve_entities=False, remove_pis=True)
    # Note: the order in which resolvers are called, seems random.
    # They end up in a set.
    parser.resolvers.add(utils.InternalResolver())
    parser.resolvers.add(utils.PythonResolver())
    if readNetwork:
        parser.resolvers.add(utils.NetworkResolver())
    parser.resolvers.add(FailingFileProtocolResolver())
    parser.resolvers.add(FailingFileSystemResolver())
    return parser


utils.getParser = getParser
