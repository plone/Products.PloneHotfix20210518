try:
    from AccessControl.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass


try:
    from AccessControl.security import _getSecurity
except ImportError:
    from Products.Five.security import _getSecurity


def protect_class(klass, permission_name):
    security = _getSecurity(klass)
    security.declareObjectProtected(permission_name)
    # security.apply(klass)
    InitializeClass(klass)


def delete_method_docstring(klass, method_name):
    # Delete the docstring from the class method.
    # Objects must have a docstring to be published.
    # So this avoids them getting published.
    method = getattr(klass, method_name, None)
    if method is None:
        return
    if hasattr(method, "im_func"):
        # Only Python 2 has im_func.
        # Python 3 has __func__, but only on methods of instances, not classes.
        if hasattr(method.im_func, "__doc__"):
            del method.im_func.__doc__
    else:
        # This would fail on Python 2 with an AttributeError:
        # "attribute '__doc__' of 'instancemethod' objects is not writable"
        if hasattr(method, "__doc__"):
            del method.__doc__
