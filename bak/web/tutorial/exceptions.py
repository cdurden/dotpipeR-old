#from pyramid.security import Allow, Deny, Everyone
#from pyramid.security import remember, forget, authenticated_userid

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

#class Root(Error):
#    def __init__(self, request):
#        self.error = None
#        self.request = request
#        self.logged_in = authenticated_userid(request)
#        if self.logged_in is not None:
#            self.__acl__ = [(Allow, Everyone, 'view')]

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """
    pass
            
class DotReadError(InputError):
    def __init__(self, msg):
        self.msg = msg

class DotNodeExistsError(Error):
    def __init__(self, node):
        self.msg = "The chosen node identifier '%s' is already used by another node" %node

class DotNodeDoesNotExistError(Error):
    def __init__(self, node):
        self.msg = "The pipeline does not contain a node matching the given identifier '%s' " %node


class PipelineEditConflict(Error):
    def __init__(self, old, new):
        self.msg = "You have chosen to edit a pipeline while an editing session for a different pipeline already exists. If you confirm this action, you will lose any unsaved changes from your existing editing session."
        self.old = old
        self.new = new

class ValidationError(Error):
    def __init__(self, param, value):
        self.msg = "The chosen value '%s' for the parameter '%s' is invalid." %(value, param)

#class RNoDefaultView(Error):
#    def __init__(self, cls):
#        self.msg = "There is no default view method for class: %s" %cls

class RViewMethodNotImplemented(Error):
    def __init__(self, cls, view_method):
        self.msg = "The data for the selected node cannot be displayed using the '%s' view method, because this method has not been implemented for objects of class '%s'." %(view_method, cls)

class RViewRuntimeError(Error):
    def __init__(self, cls, view_method, msg):
        self.msg = "The data for the selected node cannot be displayed using the '%s' view method, because there was an error running the view method for this object of class '%s': %s" %(view_method, cls, msg)

class RPipelineReadError(Error):
    def __init__(self, msg):
        self.msg = "The pipeline could not be loaded. Error message: %s" %(msg)

class RPipelineNodeCacheError(Error):
    def __init__(self, node, msg):
        self.msg = "The data for the selected node '%s' could not be loaded. This usually means that a cached version was not found because execution of the pipeline has not been completed. Error message: %s" %(node, msg)

