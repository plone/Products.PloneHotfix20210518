# -*- coding: utf-8 -*-
from Products.PloneHotfix20210518.tests import BaseTest

import os


class TestAttackVector(BaseTest):
    def test_rest_convert(self):
        from Products.PortalTransforms.data import datastream
        from Products.PortalTransforms.transforms.rest import rest

        # Try to convert ReStructuredText resulting in a warning.
        orig = "Hello *world"
        data = datastream("foo")
        transform = rest()
        # With the warnings parameter you could write to the filesystem.
        # With the stylesheet parameter you could read from the filesystem.
        # https://sourceforge.net/p/docutils/bugs/413/
        here = os.path.dirname(__file__)
        warnings_file = os.path.join(here, "write.txt")
        css_file = os.path.join(here, "read.css")
        read_contents = "Arbitrary file read from OS."
        with open(css_file, "w") as css:
            css.write(read_contents)
        bad_keyword_arguments = {
            "warnings": warnings_file,
            "stylesheet": css_file,
        }
        try:
            result = transform.convert(orig, data, **bad_keyword_arguments)
            output = result.getData()
            # There should be a warning for the wrong ReStructuredText.
            self.assertIn("WARNING", output)
            # The contents of the css file should not be in the result.
            self.assertNotIn(read_contents, output)
            self.assertNotIn(css_file, output)
            # No file should have been written to the system.
            self.assertFalse(os.path.exists(warnings_file))
        finally:
            # cleanup
            if os.path.exists(warnings_file):
                os.remove(warnings_file)
            if os.path.exists(css_file):
                os.remove(css_file)
