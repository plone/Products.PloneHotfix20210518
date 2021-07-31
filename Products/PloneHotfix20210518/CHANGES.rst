Changelog
=========


1.6 (2021-07-31)
----------------

- Fix Remote Code Execution via Python Script and string Formatter.
  This is a variant of earlier vulnerabilities in this hotfix.
  Only Plone 5.2 on Python 3 is vulnerable.
  Alternatively on Python 5.2, you can upgrade to ``AccessControl`` 4.3.
  On earlier versions of Plone and Python, the fix is not needed,
  but it is fine to upgrade to this new hotfix version.


1.5 (2021-06-28)
----------------


- Fixed new XSS vulnerability in folder contents on Plone 5.0 and higher.

- Added support for environment variable ``STRICT_TRAVERSE_CHECK``.

  - Default value is 0, which means as strict as the code from version 1.4.
  - Value 1 is very strict, the same as the stricter code introduced in Zope 5.2.1
    and now taken over in Zope 4.6.2.
    There are known issues in Plone with this, for example in the versions history view.
  - Value 2 means: try to be strict, but if this fails we show a warning and return the found object anyway.
    The idea would be to use this in development or production for a while, to see which code needs a fix.

- Fix Remote Code Execution via traversal in expressions via string formatter.
  This is a variant of two earlier vulnerabilities in this hotfix.


1.4 (2021-06-08)
----------------

- Use safe html transform instead of escape for richtext diff.
  Otherwise the inline diff is not inline anymore.

- With PLONEHOTFIX20210518_NAMEDFILE_USE_DENYLIST=1 in the OS environment,
  use a denylist for determining which mimetypes can be displayed inline.
  By default we use an allowlist with the most used image types, plain text, and PDF.
  The denylist contains svg, javascript, and html,
  which have known cross site scripting possibilities.

- By popular request, allow showing PDF files inline.
  Note: browser preference plays a part in what actually happens.

- In untrusted path expressions with modules, check that each module is allowed.
  In the first version of the hotfix we disallowed modules that were available
  as a 'private' alias, for example ``random._itertools``.
  But if ``random.itertools`` without underscore would have been available,
  it was still allowed, even though ``itertools`` has not been explicitly allowed.
  (``itertools`` might be fine to allow, it is just an example.)
  This version is a recommended upgrade for all users.


1.3 (2021-06-01)
----------------

- Moved ``CHANGES.rst`` to main directory and add a ``version.txt`` there.
  This makes it easier to check that you have the correct version when you use the zip download
  from https://plone.org/security/hotfix/20210518.
  This file is cached, so you might get an earlier version.
  Check the sha1 or md5 checksum to be sure.

- Define a set ``ALLOWED_UNDERSCORE_NAMES`` with allowed names.
  This currently contains ``__name__``, ``_`` and ``_authenticator``.
  This makes it easier for projects to add a name in a patch if this is really needed.
  Be sure you know what you are doing if you override this.

- Allow accessing a single underscore ``_``.
  After the merge of the hotfix, Zope allows this to fix a test failure.
  Seems wise to allow it in the hotfix too.

- Allow accessing ``_authenticator`` from plone.protect in more cases.
  The previous version did this for a traverse class, and now also for a traverse function.


1.2 (2021-05-19)
----------------

- Allow accessing ``_authenticator`` from plone.protect.
  It fixes a NotFound error when submitting a PloneFormGen form,
  see `issue 229 <https://github.com/smcmahon/Products.PloneFormGen/pull/229>`_.
  Should solve similar cases as well.

- Fixed the expressions patch.
  It unintentionally changed the behavior of the ``TrustedBoboAwareZopeTraverse`` class as well.
  Most importantly, it let this class use ``restrictedTraverse``, so it did unwanted security checks:
  this class is used for expressions in trusted templates on the file system.
  Needed for all Plone versions, except 4.3 when it does not have the optional ``five.pt`` package.
  One test is: login as Editor and go to the ``@@historyview`` of a page.
  If you get an ``Unauthorized`` error, you should upgrade to the new version.
  If you are unsure: install this version.


1.1 (2021-05-18)
----------------

- Allow using ``__name__`` in untrusted expressions.
  The previous expressions patch was too strict.
  This may be needed in case you have templates that use `__name__`.
  This does not happen often, but one example is the ``caching-controlpanel`` view,
  which with the previous version may give a 404 NotFound error.
  In some Plone versions browser views are affected (Plone 4.3 with five.pt, 5.0, 5.1, 5.2.0-5.2.2).
  In all Plone versions skin or through-the-web templates are affected.
  When you see more NotFound errors than normal, you should install this new version.
  If you are unsure: install this version.


1.0 (2021-05-18)
----------------

- Initial release
