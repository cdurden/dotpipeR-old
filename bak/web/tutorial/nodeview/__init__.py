from chameleon import PageTemplateLoader
from ..exceptions import RViewMethodNotImplemented
import os
import re 
import glob

def get_methods(node_class):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),node_class)
    methods = [re.sub("\.pt$","",tmpl) for tmpl in map(os.path.basename,glob.glob(path+"/*.pt"))]
#    methods = [re.sub(r'\.pt$', '', f) for f in re.match(r'.*\.pt$',os.listdir(path))]
    return(methods)
    
class NodeView(object):
    def __init__(self,node_class,method):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)),node_class)
        templates = PageTemplateLoader(path, encoding="utf-8")
        try:
            self.template = templates[method+'.pt']
        except ValueError:
            raise RViewMethodNotImplemented(node_class,method)
        try:
            with open(os.path.join(path,method+'.R'),'r') as f:
                self.R_code = f.read()
        except FileNotFoundError:
            self.R_code = None
            pass

