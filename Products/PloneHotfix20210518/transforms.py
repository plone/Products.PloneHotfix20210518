from Products.PortalTransforms.transforms.rest import rest


rest._original_convert = rest.convert


def convert(self, orig, data, **kwargs):
    # See https://sourceforge.net/p/docutils/bugs/413/
    kwargs.pop("warnings", None)
    kwargs.pop("stylesheet", None)
    return self._original_convert(orig, data, **kwargs)


rest.convert = convert
