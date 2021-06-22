#!/usr/bin/env python
import os
import shutil
import sys
import subprocess


basedir = os.path.dirname(os.path.abspath(__file__))
products_path = os.path.join(basedir, "Products")
target = ""
os.chdir(products_path)
for path in os.listdir("."):
    # Look for the PloneHotfix directory so we can use it as target name.
    if os.path.isdir(path):
        target = path
        break
if not target:
    sys.stderr.write('PloneHotfix directory not found.\n')
    sys.exit(1)

# make sure we won't get OS X resource forks
os.environ['COPY_EXTENDED_ATTRIBUTES_DISABLE'] = 'true'
os.environ['COPYFILE_DISABLE'] = 'true'

# clean up any old dists
if os.path.exists('dist'):
    shutil.rmtree('dist')

# get version from setup.py
os.chdir(basedir)
py = sys.executable
version = subprocess.check_output([py, 'setup.py', '--version']).strip()

# Go one dir above target and make a zip version of the target.
os.chdir(products_path)
# Remove any previous zips that might be here.
os.system('rm -f %s-*.zip' % target)
filename = '%s-%s.zip' % (target, version)
os.system("zip -r {filename} {target} -x '*.pyc' -x '*{s}tests{s}*' -x '*{s}__pycache__{s}*'".format(
    target=target,
    filename=filename,
    s=os.path.sep))

os.chdir(basedir)
if not os.path.exists('dist'):
    os.mkdir('dist')

shutil.move(os.path.join(products_path, filename),
            os.path.join(basedir, 'dist', filename))

# print checksums
os.chdir(os.path.join(basedir, 'dist'))
print
print '* MD5 checksums:'
os.system('md5 *')
print '* SHA checksums:'
os.system('shasum *')
