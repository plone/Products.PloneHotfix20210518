Plone hotfix, 2021-05-18
========================

This hotfix fixes several security issues:

- Remote Code Execution via traversal in expressions via aliases.
  Reported by David Miller.
- Remote Code Execution via traversal in expressions (no aliases).
  Reported by Calum Hutton.
- Remote Code Execution via traversal in expressions via string formatter.
  Reported by David Miller.
- Writing arbitrary files via docutils and Python Script.
  Reported by Calum Hutton.
- Stored XSS from file upload (svg, html).
  Reported separately by Emir Cüneyt Akkutlu and Tino Kautschke.
- XSS vulnerability in CMFDiffTool.
  Reported by Igor Margitich.
- Reflected XSS in various spots.
  Reported by Calum Hutton.
- Various information disclosures: GS, QI, all_users.
  Reported by Calum Hutton.
- Stored XSS from user fullname.
  Reported by Tino Kautschke.
- Blind SSRF via feedparser accessing an internal URL.
  Reported by Subodh Kumar Shree.
- Server Side Request Forgery via event ical URL.
  Reported by MisakiKata and David Miller.
- Server Side Request Forgery via lxml parser.
  Reported by MisakiKata and David Miller.
- XSS in folder contents on Plone 5.0 and higher.
  Reported by Matt Moreschi.
  Only included since version 1.5 of the hotfix.
- Remote Code Execution via Python Script.
  Reported by Calum Hutton.
  Only Plone 5.2 on Python 3 is vulnerable.
  Only included since version 1.6 of the hotfix.


Compatibility
=============

This hotfix should be applied to the following versions of Plone:

* Plone 5.2.4 and any earlier 5.2.x version
* Plone 5.1.7 and any earlier 5.1x version
* Plone 5.0.10 and any earlier 5.0.x version
* Plone 4.3.20 and any earlier 4.x version

The hotfix is officially supported by the Plone security team on the
following versions of Plone in accordance with the Plone
`version support policy <https://plone.org/security/update-policy>`_: 4.3.20, 5.0.10, 5.1.7 and 5.2.4.

On Plone 4.3, 5.0 and 5.1 the hotfix is officially only supported on Python 2.7.
On Plone 5.2.X it is supported on Python 2.7 and Python 3.6/3.7/3.8.

The fixes included here will be incorporated into subsequent releases of Plone,
so Plone 5.2.5 and greater should not require this hotfix.


Zope
====

Zope is also affected.
New versions for Zope and other packages are available.
Upgrading to those is the recommended way.

If you cannot upgrade yet, you can try the Plone hotfix.
It has not been tested on Zope only, but we try not to let the Plone-specific code get in the way, so it should be okay.

These vulnerabilities mentioned above are relevant for Zope:

- Remote Code Execution via traversal in expressions via aliases.
  Fixes released in Zope 4.6 and 5.2.
- Remote Code Execution via traversal in expressions (no aliases).
  Fixes released in Zope 4.6.1 and 5.2.1.
- Various information disclosures.
  Fixes released in Products.PluggableAuthService 2.6.0, Products.GenericSetup 2.1.1, and Zope 4.5.5.
- Reflected XSS in various spots.
  Fixes released in Products.CMFCore 2.5.1 and Products.PluggableAuthService 2.6.2.
- Remote Code Execution via traversal in expressions via string formatter.
  Fixes released in Zope 4.6.2, which takes over the already stricter code from Zope 5.2.1.
- Remote Code Execution via Python Script.
  Fixes released in Zope 4.6.3 and 5.3.


Installation
============

Installation instructions can be found at
https://plone.org/security/hotfix/20210518

.. note::

  You may get an error when running buildout::

    Error: Couldn't find a distribution for 'Products.PloneHotfix20210518==1.0'.

  The most likely cause is that you use a too old Python or too old setuptools without "SNI" support.
  See this `community.plone.org post <https://community.plone.org/t/pypi-deprecation-of-support-for-non-sni-clients-breaks-buildout-for-older-plone-versions/13803>`_.

  Another cause could be that your buildout is trying to download the hotfix via http or from an older PyPI index.
  In the buildout section of your buildout, make sure you use the correct index::

    [buildout]
    index = https://pypi.org/simple/


Q&A
===

Q: How can I confirm that the hotfix is installed correctly and my site is protected?
  A: On startup, the hotfix will log a number of messages to the Zope event log
  that look like this::

    2021-05-18 14:07:24,176 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied expressions patch
    2021-05-18 14:07:24,179 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied genericsetup patch
    2021-05-18 14:07:24,181 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied pas patch
    2021-05-18 14:07:24,182 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied propertymanager patch
    2021-05-18 14:07:24,183 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied skinnable patch
    2021-05-18 14:07:24,187 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied xmlrpc_dump_instance patch
    2021-05-18 14:07:24,188 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied difftool patch
    2021-05-18 14:07:24,238 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied event patch
    2021-05-18 14:07:24,244 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied modeleditor patch
    2021-05-18 14:07:24,246 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied namedfile patch
    2021-05-18 14:07:24,283 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied pa_users patch
    2021-05-18 14:07:24,367 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied portlets patch
    2021-05-18 14:07:24,369 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied publishing patch
    2021-05-18 14:07:24,371 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied qi patch
    2021-05-18 14:07:24,372 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied supermodel patch
    2021-05-18 14:07:24,500 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied theming patch
    2021-05-18 14:07:24,634 INFO    [Products.PloneHotfix20210518:43][MainThread] Applied transforms patch
    2021-05-18 14:07:24,634 INFO    [Products.PloneHotfix20210518:51][MainThread] Hotfix installed

  The exact number of patches applied, will differ depending on what packages you are using.
  If a patch is attempted but fails, it will be logged as an error that says
  "Could not apply". This may indicate that you have a non-standard Plone
  installation.  Please investigate, and mail us the accompanying traceback if you think it is a problem in the hotfix.

Q: How can I report problems installing the patch?
  A: Contact the Plone security team at security@plone.org or visit the
  Gitter channel at https://gitter.im/plone/public and the forum at https://community.plone.org

Q: How can I report other potential security vulnerabilities?
  A: Please email the security team at security@plone.org rather than discussing
  potential security issues publicly.
