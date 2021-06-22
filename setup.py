from setuptools import find_packages
from setuptools import setup

import os

with open(os.path.join("Products", "PloneHotfix20210518", "README.txt")) as myfile:
    readme = myfile.read()
with open(os.path.join("Products", "PloneHotfix20210518", "CHANGES.rst")) as myfile:
    changes = myfile.read()
long_description = readme + "\n" + changes
with open(os.path.join("Products", "PloneHotfix20210518", "version.txt")) as myfile:
    version = myfile.read().strip()

setup(
    name="Products.PloneHotfix20210518",
    version=version,
    description="Various Plone hotfixes, 2021-05-18",
    long_description=long_description,
    # Get more strings from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 5.2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="plone security hotfix patch",
    author="Plone Security Team",
    author_email="security@plone.org",
    url="https://plone.org/security/hotfix/20210518",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["Products"],
    include_package_data=True,
    zip_safe=False,
    install_requires=["setuptools"],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
