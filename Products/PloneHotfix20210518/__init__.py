import logging
import pkg_resources


logger = logging.getLogger("Products.PloneHotfix20210518")

# First import any current CMFPlone patches.
try:
    pkg_resources.get_distribution("Products.CMFPlone")
    HAS_PLONE = True
except pkg_resources.DistributionNotFound:
    HAS_PLONE = False
else:
    from Products.CMFPlone import patches  # noqa

# General hotfixes for all, including Zope/CMF.
hotfixes = [
    "expressions",
    "genericsetup",
    "pas",
    "propertymanager",
    "skinnable",
    "xmlrpc_dump_instance",
]
# This could theoretically be used outside of Plone:
try:
    pkg_resources.get_distribution("Products.CMFDiffTool")
    hotfixes.append("difftool")
except pkg_resources.DistributionNotFound:
    pass
if HAS_PLONE:
    # Extra hotfixes for Plone:
    try:
        pkg_resources.get_distribution("plone.app.event")
        hotfixes.append("event")
    except pkg_resources.DistributionNotFound:
        pass
    try:
        pkg_resources.get_distribution("plone.app.dexterity")
        hotfixes.append("modeleditor")
    except pkg_resources.DistributionNotFound:
        pass
    try:
        pkg_resources.get_distribution("plone.namedfile")
        hotfixes.append("namedfile")
    except pkg_resources.DistributionNotFound:
        pass
    try:
        pkg_resources.get_distribution("plone.app.users")
        hotfixes.append("pa_users")
    except pkg_resources.DistributionNotFound:
        pass
    try:
        pkg_resources.get_distribution("plone.supermodel")
        hotfixes.append("supermodel")
    except pkg_resources.DistributionNotFound:
        pass
    try:
        pkg_resources.get_distribution("plone.app.theming")
        hotfixes.append("theming")
    except pkg_resources.DistributionNotFound:
        pass
    hotfixes.append("portlets")
    hotfixes.append("publishing")
    hotfixes.append("qi")
    hotfixes.append("transforms")

# Apply the fixes
for hotfix in hotfixes:
    try:
        __import__("Products.PloneHotfix20210518.%s" % hotfix)
        logger.info("Applied %s patch" % hotfix)
    except:  # noqa
        # This is an error that the user should investigate.
        # Log an error and continue.
        logger.exception("Could not apply %s" % hotfix)
if not hotfixes:
    logger.info("No hotfixes were needed.")
else:
    logger.info("Hotfix installed")
