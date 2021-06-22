from .utils import delete_method_docstring
from OFS.PropertyManager import PropertyManager


property_methods = (
    "getProperty",
    "propertyValues",
    "propertyItems",
    "propertyMap",
    "hasProperty",
    "getPropertyType",
    "propertyIds",
    "propertyLabel",
    "propertyDescription",
)
for method_name in property_methods:
    delete_method_docstring(PropertyManager, method_name)
