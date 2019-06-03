from pyramid.security import Allow, Deny, Everyone
from pyramid.security import remember, forget, authenticated_userid, effective_principals

from pyramid.exceptions import NotFound
from networkx import write_dot
#import pygraphviz
#from pydot import Dot as Dot_
#from pydot import Node, Edge
#import pydot
import pydotreader
from networkx import DiGraph as DiGraph_

def convert_networkx_digraph_to_graphviz_digraph(g):
    from graphviz import Digraph as GraphvizDigraph
    graph = GraphvizDigraph()
    for node in g.nodes_iter(data=True):
        #attrs = node[1]
        attrs = dict([(k,v) for k,v in node[1].items() if k != "name"])
        graph.node(node[0],**attrs)

    for edge in g.edges_iter(data=True):
        graph.edge(edge[0],edge[1],**(edge[2]))
    return(graph)

from urllib.parse import urljoin
#from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.error import HTTPError

from sqlalchemy import types, ForeignKey, UniqueConstraint
from sqlalchemy import (
    Column,
    Integer,
    Text,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref

from zope.sqlalchemy import ZopeTransactionExtension

#DBSession = scoped_session(
#    sessionmaker(extension=ZopeTransactionExtension()))

import transaction

#Base = declarative_base()

from pyramid.threadlocal import get_current_registry
from pyramid.settings import asbool
from . import settings
import os
import tempfile
import re

from . import Base, DBSession
from .security import User
from .exceptions import DotReadError, PipelineEditConflict, RViewRuntimeError, RPipelineNodeCacheError, RPipelineReadError, DotRenderError
from .nodeview import NodeView
from .nodeview import get_methods as nodeview_methods

import socket
timeout = 10
socket.setdefaulttimeout(timeout)

os.environ['R_HOME'] = settings.r_home
from rpy2.robjects import r
from rpy2.robjects.vectors import ListVector
from rpy2.rinterface import NULL
#from rpy2.rinterface import RRuntimeError 
from rpy2.rinterface_lib.embedded import RRuntimeError


from urllib import parse as urlparse
   
class Root(object):
    def __init__(self, request):
        self.error = None
        self.request = request
        self.noauth = asbool(request.registry.settings['noauth'])
        if self.noauth:
            self.logged_in = 'guest'
        else:
            self.logged_in = authenticated_userid(request)
        principals = effective_principals(request)
        i = [ i for i, principal in enumerate(principals) if principal.startswith('u:') ]
        if len(i):
            user_principal = principals[i[0]]
            username = user_principal[2:]
            self.user = DBSession.query(User).filter_by(username=username).one()
        else:
            self.user = None
        self.auth = dict(persona = 'auth:persona' in principals, internal = 'auth:internal' in principals)
        if self.user is not None or self.noauth:
            self.__acl__ = [(Allow, Everyone, 'view')]


class PipelineStatic(Root):
    def __init__(self, request):
        super().__init__(request)
        uri_ref = "/".join(self.request.matchdict['subpath'])
        print("uri_ref: "+uri_ref)
        self.pipeline = DBSession.query(Pipeline).filter(Pipeline.uri_ref==uri_ref).one()
        if self.pipeline is None:
            raise(NotFound)
        owner = DBSession.query(User).get(self.pipeline.owner) #FIXME: can map this with SA
        self.__acl__ = []
        p = self.pipeline.permissions
        if bool(p%2):
            self.__acl__.append((Allow, owner.username, 'execute'))
        if bool(remlowerbits(p,2)%4):
            self.__acl__.append((Allow, owner.username, 'write'))
        if bool(remlowerbits(p,3)%8):
            print("adding view permission for user", owner.username)
            self.__acl__.append((Allow, owner.username, 'view'))
        if self.noauth:
            self.__acl__.append((Allow, Everyone, 'view'))
        self.pipeline.load_dot(self.request)


class AccessR(Root):
    def __init__(self, request):
        super().__init__(request)
        self.R_init = False
        self.request = request
        self.cachedir = request.registry.settings['dotpipeR_cachedir']
        self.viewsrc = request.registry.settings['dotpipeR_viewsrc']

    def initR(self):
    #    from rpy2.robjects import r
        if not self.R_init:
            r('library(dotpipeR)')
            r('%s <- new.env()' %settings.dotpipeR_env_name)
            r('attach(%s)' %settings.dotpipeR_env_name)
#            r('as.environment(which(search()=="%s"))[[1]]' %settings.dotpipeR_env_name)
            upload_dir = os.path.join(self.request.registry.settings['uploadpath'],self.logged_in)
            r('setwd("%s")' %upload_dir)
            self.R_init = True
        return


class DotPipeR(AccessR):
    def __init__(self, request, **kwargs):
        super().__init__(request)
        self.conflict = False
        pipeline_id = self.request.matchdict['pipeline_id']
        request.context = self
        self.pipeline = DBSession.query(Pipeline).get(pipeline_id)
        if self.pipeline is None:
            self.msg = "Could not find the requested pipeline"
            raise(NotFound)

        owner = DBSession.query(User).get(self.pipeline.owner) #FIXME: can map this with SA
        self.__acl__ = []
        p = self.pipeline.permissions
        if bool(p%2):
            self.__acl__.append((Allow, owner.username, 'execute'))
        if bool(remlowerbits(p,2)%4):
            self.__acl__.append((Allow, owner.username, 'write'))
        if bool(remlowerbits(p,3)%8):
            print("assing view permission for user", owner.username)
            self.__acl__.append((Allow, owner.username, 'view'))
        if self.noauth:
            self.__acl__.append((Allow, Everyone, 'view'))
        self.pipeline.load_dot(self.request)

class DotPipeREdit(DotPipeR):
    def __init__(self, request):
        super().__init__(request)
        self.load_dot()
        self.request = request

    def load_dot(self):
        try:
            if self.request.session.get('pipeline_id') is None or self.request.params.get('discard_changes')=="1" or self.request.params.get('confirm')=='1': # load original/saved dot file
                print("loading original dot file")
                self.pipeline.load_dot(self.request)
                self.request.session['tmpdot']=self.pipeline.dot.save_to_tmp()
                self.request.session['pipeline_id']=self.pipeline.id
            elif self.request.session.get('pipeline_id') == self.pipeline.id: # no pipeline id conflict; either load from url or load from session dot file
                print("loading dot file")
                dot = Digraph.load_from_file_path(self.request.session.get('tmpdot'))
                print("done loading dot file")
                self.pipeline.dot = dot
                dot.pipeline = self.pipeline
            else:
                raise(PipelineEditConflict(self.request.session.get('pipeline_id'),self.pipeline.id))
        except IOError as e:
            raise(DotReadError(e))
        except TypeError as e:
            raise(DotReadError(e)) #FIXME: need to handle general exception

def listornull(obj):
    if obj == NULL:
        return([])
    else:
        return(list(obj))

def is_absolute(url):
    return bool(urlparse.urlparse(url).scheme)

def remlowerbits(z, n):
    if n<1:
        return(z)
    if n==1:
        return(z-z%2)
    else:
        red = remlowerbits(z,n-1)
        return(red - red%(2**(n-1)))

def validate_dot_node_id(string):
    return(re.match("^[a-zA-Z][a-zA-Z0-9_]*$",string) is not None)

def validate_dot_identifier(s):
    return(not(re.search('^[a-zA-Z\200-\377|_][0-9a-zA-Z\200-\377|_]*$',s) is None and re.search('^[-]?(.[0-9]+|[0-9]+(\.[0-9]*)?)$',s) is None and re.search('^\"([^"]|\\\\")*\"$',s) is None))

def validate_R_identifier(string):
    return(not(re.match("^[a-zA-Z][a-zA-Z0-9\._]*$",string) is None and (re.match("^[\.][a-zA-Z\._][a-zA-Z0-9\._]*$",string) is None or re.match("^\.{3}$|^\.\.[0-9]+$",string) is not None)))

def validate_DotPipeR_fn_param_val(string): #NOTE: this function validates strings that can be used in dot attribute identifiers, either bare or inside double-quoted dot identifiers. You need to call dotunquote on the string if it is possibly a double-quoted dot identifier, to remove possible surrounding double-quotes, because these are interpreted by DotPipeR before being evaluated in R
    return(validate_R_identifier(string) or re.search('^[-]?(.[0-9]+|[0-9]+(\.[0-9]*)?)$',string) is not None or re.match('^\'([^\']|\\\\\')*\'$',string) is not None)
#    return(re.match("^NULL$|^NA$|^Inf$|^NaN$|^TRUE$|^FALSE$|^-?(\.[0-9]+|[0-9]+(\.[0-9]*)?)$|^\"'[^\"']*'\"$",string) is not None)

def dotunquote(s):
#    s = re.sub('^"(.*)"$','\\1',s)
    s = re.sub('^\"(([^"]|\\\\")*)\"$','\\1',s)
    return(s)
    
def dotquote(s):
#    s = re.sub('^"|"$',"'",s)
    if re.search('^[a-zA-Z\200-\377|_][0-9a-zA-Z\200-\377|_]*$',s) is None and re.search('^[-]?(.[0-9]+|[0-9]+(\.[0-9]*)?)$',s) is None: # not standard alphanumeric ID and not a numeral 
        if re.search('^\"([^"]|\\\\")*\"$',s) is None: # not a double-quoted string
            if re.search('^\'([^\']|\\\\\')*\'$',s) is None: # not a single-quoted string
                if not validate_R_identifier(s):
                    s = '\''+s+'\'' # add inner quotes because parameters which are not R identifiers must be quoted strings
            s = '"'+s+'"' # need to add double quotes, because this is not a standard alphanumeric ID, a numeral, nor a double-quoted string
        else: # we're dealing with a double-quoted string, beginning and ending " with no intervening unescaped double quote characters
            r = re.sub('^\"(([^"]|\\\\")*)\"$','\\1',s)
            s = '"\''+r+'\'"' # add inner single-quotes because parameters which are not R identifiers must be interpreted as character strings
#            if not validate_R_identifier(r) and re.search('^\'([^\']|\\\\\')*\'$',r) is None: # quoted string is not a valid R identifier, nor a single-quoted string
#                s = '"\''+r+'\'"' # add inner single-quotes because parameters which are not R identifiers must be interpreted as character strings
    return(s)

class NodeData(object):
    def __init__(self, dot, node):
        self.dot = dot 
        self.node = node
        self.data = None
        self.graphics_data = None

    def view(self, method, context):
        self.eval_in_R(context)
#        node_view = importlib.import_module("nodeviews.%s.%s" %(node_class,method))
        node_class = self.get_class(context)
        nodeview = NodeView(node_class,method)

        if nodeview.R_code is not None:
            try:
                r('source("%s")' %context.viewsrc)
                r(nodeview.R_code)
                here = os.path.dirname(__file__)
                tmpdir = os.path.join(here,'static','tmp')
                graphics_data = r('view(pipeline["%s"],tmpdir="%s")' %(self.node,tmpdir))
            except Exception as e:
                graphics_data = NULL
                raise RViewRuntimeError(node_class,method,str(e))
        else:
            graphics_data = NULL

        self.graphics_data = []
        if type(graphics_data) == ListVector:
            for i in range(0,len(graphics_data)): #FIXME: we are counting on R code to return a well-formatted object
                graphics_elmt = graphics_data.rx2(i+1)
                self.graphics_data.append({})
                print(graphics_elmt)
                for j in range(0,len(graphics_elmt)):
                    name = list(graphics_elmt.names)[j]
                    self.graphics_data[i][name] = graphics_elmt.rx2(j+1)[0]
                self.graphics_data[i]['href'] = context.request.static_url('dotpipeR:'+urljoin('static/tmp/',os.path.basename(self.graphics_data[i]['file']))) # FIXME: this could break
        elif graphics_data is not NULL:
            print(graphics_data)
            self.graphics_data.append({})
            self.graphics_data[0]['format'] = 'png' 
            graphics_elmt = graphics_data.rx2(1)
            self.graphics_data[0]['href'] = context.request.static_url('dotpipeR:'+urljoin('static/tmp/', os.path.basename(graphics_elmt.rx2(1)[0]))) # FIXME: this could break
        nodeview.graphics_data = self.graphics_data 
        R_as = r('as')
        print("rendering node view template")
        nodeview.html = nodeview.template(node=self, node_class=node_class, NULL=NULL, R_as=R_as, r=r)
        print(nodeview.html)
        return(nodeview)
        
    def get_class(self, context):
        Rclass = r('class')
        node_class = Rclass(self.get_data(context))[0]
        return(node_class)

    def get_data(self, context):
        if self.data is None:
            self.eval_in_R(context)
        return(self.data)

    def view_methods(self, context):
        return(nodeview_methods(self.get_class(context)))
#        context.initR()
#        r('source("%s")' %settings.R_views_source)
#        methods = list(r('eval(formals(getMethod("view",signature=c("%s","character")))$method)' %self.get_class(context)) or [])
#        return(methods)

    def eval_in_R(self, context):
        if self.dot.file_path is None:
            self.data = None
        else:
            context.initR()
            try:
                r('pipeline <- read.Pipeline("%s")' %self.dot.file_path) # FIXME: dot file not found error handling
            except RRuntimeError as e:
                raise RPipelineReadError(e)
            try:
                r('envir <- as.environment(which(search()=="%s")[1])' %settings.dotpipeR_env_name)
                r('pipeline <- eval.PipelineNodes(pipeline,"%s",cacheMethod=cacheMethodPipelineDigest,cachedir="%s",envir=envir)' %(self.node,context.cachedir))
            except RRuntimeError as e:
                raise RPipelineNodeCacheError(self.node, e)
            self.data = r('pipeline["%s"]' %self.node)
        return(self.data)

class Node:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def get_name(self):
        return(self.name)
    
class Digraph(object):
    def __init__(self, nx_digraph):
        self.nx_digraph = nx_digraph 
        self.data = {}
        self.file_path = None

    def set_node_attr(self, node, key, value):
        attrs = {key: value}
        self.add_node(node, **attrs)

    def load_from_file_path(file_path):
        nx_digraph = pydotreader.load_networkx_digraph_from_dot(file_path)
        print("loading graph from dot file %s", file_path)
        print(nx_digraph)
        if type(nx_digraph) != DiGraph_:
            raise DotReadError('Could not read DOT file. This is probably a syntax error. If you encounter this error while editing a pipeline, the application has probably generated a bad DOT file.') #FIXME: need to provide a way for the user to fix the problem
        digraph = Digraph(nx_digraph)
        digraph.preprocessor_lines = ""
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith("#"):
                     digraph.preprocessor_lines += line
        digraph.file_path = file_path
        return(digraph)

    def load_from_url(url):
        print("retrieving ", url)
        file_path, headers = urlretrieve(url)
        print(file_path)
        g = Digraph.load_from_file_path(file_path)
        return(g)

    def annotate(self):
        if self.pipeline is not None:
            self.annotations = dict()
            for annotation in self.pipeline.annotations:
                if annotation.node in self.annotations.keys():
                    self.annotations[annotation.node].append(annotation)
                else:
                    self.annotations[annotation.node] = [annotation]
                    node = self.get_node(annotation.node)[0] # FIXME: does this do the right thing?
                    node.set('style','filled')
                    node.set('fillcolor','yellow')
                    print(node.get_name())
        
    def draw_svg(self,request):
        g = self.nx_digraph
        for node in g.nodes_iter(data=False):
            attrs = {'id': node, 'href':'javascript:void();'}
            g.add_node(node, **attrs)
        for edge in g.edges_iter(data=False):
            attrs = {'tooltip':'test'}
            g.add_edge(edge[0],edge[1], **attrs)
        graphviz_digraph = convert_networkx_digraph_to_graphviz_digraph(g)
        graphviz_digraph.attr('graph',tooltip="")
        here = os.path.dirname(__file__)
        dir = os.path.join(here,'static','tmp')
        fd, path = tempfile.mkstemp(suffix='.svg',dir=dir) 
        try:
            with open(path,'w') as f:
                f.write(graphviz_digraph._repr_svg_())
        except IOError as e:
            raise(DotRenderError(e.value))
        return(request.static_path('dotpipeR:'+os.path.join('static','tmp',os.path.split(path)[1])))

#    def add_node(self, node_id):
#        n = Node(node_id)
#        self.node(n)
#        return n # fixme: error handling

#    def add_edge(self, src, dest):
#        edge = Edge(src, dest)
#        self.edge(src, dest)
#        return edge # fixme: error handling

    def del_edge(self, src, dest):
        self.nx_digraph.remove_edge(src, dest)

    def get_nodes(self):
        nodes = [Node(node[0],node[1]) for node in self.nx_digraph.nodes_iter(data=True)]
        return(nodes)
#        return(self.nx_digraph.nodes())

    def get_edges(self):
        return(self.nx_digraph.edges())

    def get_node(self, name):
#        return(self.nx_digraph.node[name])
        return(Node(name,self.get_node_data(name)))

    def del_node(self,name):
        return(self.remove_node(name))

    def excise_node(self,name):
        edges = self.edges()
        for edge in edges:
            src = edge[0]
            dest = edge[1]
            if src == name or dest == name:
                self.del_edge(src,dest)
        return(self.del_node(name))

    def write(self,path):
        write_dot(self.nx_digraph,path)
#        self.dot.write(path)
        print("writing dot file: " + path)    
        with open(path,'a') as f:
            f.write(self.preprocessor_lines)
#            for package in self.pipeline.packages:
#                print(package.package)
#                f.write('#library("%s")\n' %package.package)

    def save_to_tmp(self):
        fd, path = tempfile.mkstemp(suffix='.dot')
        self.write(path)
        return(path)
        
    def source(self): # FIXME: what is the right way to initialize the object?
        source = ''
        with open(self.file_path, 'r') as f:
            for line in f:
                 source += line
        return(source)
        
    def eval_node_in_R(self, node, context):
        context.initR()
        if node in self.data.keys():
            node_data = self.data[node]
        else:
            r('pipeline <- read.Pipeline("%s")' %self.file_path)
#            r('pipeline <- eval.PipelineNode(pipeline,"%s",cacheMethod=cacheMethodPipelineDigest,do.eval=FALSE)' %node)
            r('envir <- as.environment(which(search()=="%s")[1])' %settings.dotpipeR_env_name)
            r('pipeline <- eval.PipelineNodes(pipeline,"%s",cacheMethod=cacheMethodPipelineDigest,cachedir="%s",envir=envir)' %(self.node,context.cachedir))
            node_data = r('pipeline["%s"]$data' %node)
            self.data[node] = node_data
        return(node_data)

# http://docs.sqlalchemy.org/en/rel_0_8/orm/tutorial.html#building-a-relationship
class Note(Base):
    __tablename__ = 'annotations'

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(Integer, ForeignKey('pipelines.id'))
    node = Column(Text)
    note = Column(Text)

    def __init__(self, pipeline, node, note):
        self.pipeline = pipeline
        self.node = node
        self.note = note

    def html(self):
        if self.note is not None:
            import markdown
            html = markdown.markdown(self.note)
            return(html)
#            from docutils.core import publish_parts
#            return(publish_parts(self.note,writer_name='html')['html_body'])
        else:
            return('')


class Package(Base):
    __tablename__ = 'packages'

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(Integer, ForeignKey('pipelines.id'))
    package = Column(Text)

    def __init__(self, pipeline, package):
        self.pipeline = pipeline
        self.package = package
   
class Pipeline(Base):
    __tablename__ = 'pipelines'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    exec_status = Column(types.Enum('none','running','completed','error'),default='none')
    error_msg = Column(Text)
    uri_ref = Column(Text)
    owner = Column(Integer)
    group = Column(Integer)
    permissions = Column(Integer)
    __table_args__ = (UniqueConstraint('name', 'owner', name='_name_owner_uc'),)

    annotations = relationship("Note", order_by="Note.id", backref="pipeline")
#    annotations = relationship("Note", order_by="Note.id")
    packages = relationship("Package", order_by="Package.id", backref="pipeline") # this backref should cause the Package constructor to populate the packages list here
   
#    def lookup(pipeline_id):
#        pipeline = DBSession.query(Pipeline).filter(Pipeline.id==pipeline_id).one()
#        return(pipeline)
    
#    def commit(self):
#        DBSession.add(self)
#        transaction.commit()

    def __init__(self, name, uri_ref, owner, group, permissions):
        self.name = name 
        self.uri_ref = uri_ref
        self.owner = owner
        self.group = group
        self.permissions = permissions
        return

    def R_fn_formals(self, fn, context):
        context.initR()
        r('pipeline <- read.Pipeline("%s")' %self.dot.file_path) # FIXME: dot file not found error handling
        r('envir <- as.environment(which(search()=="%s")[1])' %settings.dotpipeR_env_name)
        r('run.PipelinePreprocessor(pipeline,envir=envir)')
        print(fn)
        names = list(r('names(formals("%s"))' %dotunquote(fn))) #FIXME: need to prevent injection attacks
        vals = list(r('sapply(formals("%s"),deparse)' %dotunquote(fn)))
        if "..." in names:
            i = names.index("...")
            names.pop(i)
            vals.pop(i)
        return(dict(fn_params=dict(zip(names, vals)), key_list=names))
    
    def R_get_fns(self, context):
        context.initR()
        print("loading pipeline into R: %s" %self.dot.file_path)
        r('pipeline <- read.Pipeline("%s")' %self.dot.file_path) # FIXME: dot file not found error handling
        r('envir <- as.environment(which(search()=="%s")[1])' %settings.dotpipeR_env_name)
        r('run.PipelinePreprocessor(pipeline,envir=envir)')
#        fns = list(r('ls(envir=envir)'))
        fns = listornull(r('names(which(lapply(mget(ls(pos="%s"),envir), mode)=="function"))' %settings.dotpipeR_env_name))
#        fns = list(r('ls()'))
        for package in self.packages:
            fns.extend(listornull(r('names(which(lapply(mget(ls(pos="package:%s"),as.environment(which(search()=="package:%s")[1])), mode)=="function"))' %(package.package,package.package)))) #FIXME: we should be running everything in a clean environment and then we can ls this environment
#            fns.extend(list(r('ls(envir=envir)'))) #FIXME: we should be running everything in a clean environment and then we can ls this environment

        print(str(fns))
        return(fns)

    def dot_modified_time(self, request):
        import os.path, time
        file_path, headers = urlretrieve(self.dot_url(request))
        modified = time.ctime(os.path.getmtime(file_path))
        return(modified)

    def load_dot(self, request):
        self.dot = Digraph.load_from_url(self.dot_url(request))
        try:
#            url = self.dot_url(request)
#            print(url)
            self.dot = Digraph.load_from_url(self.dot_url(request))
        except IOError as e:
            raise(DotReadError(e.strerror))
        except TypeError as e:
            raise(DotReadError(e)) #FIXME: need to handle general exception
        self.dot.pipeline = self
        return(self.dot)
 
    def run(self, context):
        self.exec_status = 'running'
        DBSession.add(self)
        DBSession.flush()
        if os.fork() == 0:
            try:
                context.initR()
            except EnvironmentError as e:
                self.exec_status = 'none'
                self.error_msg = e.strerror
            except Exception as e:
                self.exec_status = 'none'
                self.error_msg = str(e.args)
            else:
                try:
                    r('pipeline <- read.Pipeline("%s")' %self.dot.file_path)
                    r('envir <- as.environment(which(search()=="%s")[1])' %settings.dotpipeR_env_name)
                    r('pipeline <- eval.Pipeline(pipeline,cachedir="%s",envir=envir)' %context.cachedir)
                except EnvironmentError as e:
                    self.exec_status = 'error'
                    self.error_msg = e.strerror
                except Exception as e:
                    self.exec_status = 'error'
                    self.error_msg = str(e.args)
                else:
                    self.exec_status = 'completed'
            finally:
                DBSession.add(self)
                DBSession.flush()

    def dot_url(self, request):
#        settings = get_current_registry().settings
#        url = urljoin(settings['base_uri'],self.uri_ref)
        print("self.uri_ref: "+self.uri_ref)
        if is_absolute(self.uri_ref):
            return(self.uri_ref)
        else:
#            url = urljoin(urljoin("file://",request.registry.settings['dot_path']),self.uri_ref)
            url = urljoin(urljoin("file://",settings.dot_path),self.uri_ref)
        return(url)

