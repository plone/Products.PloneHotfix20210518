from Products.PythonScripts.PythonScript import PythonScript
from Testing.makerequest import makerequest
from zExceptions import Unauthorized

import unittest


class TestPythonScripts(unittest.TestCase):
    """Test accessing string classes in Python Scripts.

    Especially the Formatter class could be used by an attacker.
    """

    def test_script_formatter(self):
        src = """
from string import Formatter
return "It worked!"
"""
        script = makerequest(PythonScript("formatterscript"))
        script._filepath = "formatterscript"
        script.write(src)
        self.assertRaises(Unauthorized, script)

    def test_script_template(self):
        src = """
from string import Template
return "It worked!"
"""
        script = makerequest(PythonScript("templatescript"))
        script._filepath = "templategetfieldscript"
        script.write(src)
        self.assertRaises(Unauthorized, script)
