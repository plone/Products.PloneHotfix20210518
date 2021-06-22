Releasing
=========

Do a normal pypi release with zest.releaser:

- Go to the top directory of the repository.
- Run fullrelease.
  If you have multiple accounts in your ``~/.pypirc`` maybe export one of them as ``TWINE_REPOSITORY`` first.
- On pypi.org manage the project and invite a few more users. At least invite the plone user.

Use the mkdists.py script on the tag you just created.

Example::

  git checkout 1.0
  python mkdists.py PloneHotfix20210518
  git checkout master

This creates the zip file in the dist directory.
Edit the hotfix page on plone.org and upload this.

Note: such an old-style product zip only works in Plone 5.1 and lower (Zope 2).
So at some point in the future we can skip this.

When a new release 1.1 is needed, and you upload the zip to plone.org,
you should probably ask someone to purge a cache on CloudFlare,
as the older zip may still get served.
Actually, no one seems to know how to do this.
