from AccessControl import getSecurityManager
from AccessControl.Permissions import view
from DateTime.DateTime import DateTime
from ExtensionClass import Base


# xmlrpc support has has been in various spots.
modules = []
try:
    from ZPublisher import xmlrpc as zpublisher_xmlrpc

    modules.append(zpublisher_xmlrpc)
except ImportError:
    pass
try:
    from ZServer.ZPublisher import xmlrpc as zserver_xmlrpc

    modules.append(zserver_xmlrpc)
except ImportError:
    pass
try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib


WRAPPERS = xmlrpclib.WRAPPERS + (DateTime,)


def dump_instance(self, value, write):
    # Check for special wrappers
    if value.__class__ in WRAPPERS:
        self.write = write
        value.encode(self)
        del self.write
    else:
        # Store instance attributes as a struct (really?).
        # We want to avoid disclosing private attributes.
        # Private attributes are by convention named with
        # a leading underscore character.
        ob_dict = dict([(k, v) for (k, v) in value.__dict__.items() if k[:1] != "_"])

        # If the instance attribute is a Zope object we also want to prevent
        # disclosing it to users without at least View permission.
        zope_objects = [(k, v) for (k, v) in ob_dict.items() if isinstance(v, Base)]
        if zope_objects:
            sm = getSecurityManager()
            for ob_id, ob in zope_objects:
                if not sm.checkPermission(view, getattr(value, ob_id)):
                    del ob_dict[ob_id]

        self.dump_struct(ob_dict, write)


if modules:
    for module in modules:
        module.dump_instance = dump_instance

    # Override the standard marshaller for object instances
    # to skip private attributes.
    try:
        from types import InstanceType

        xmlrpclib.Marshaller.dispatch[InstanceType] = dump_instance  # py2
    except ImportError:
        xmlrpclib.Marshaller.dispatch["_arbitrary_instance"] = dump_instance  # py3

    xmlrpclib.Marshaller.dispatch[DateTime] = dump_instance
