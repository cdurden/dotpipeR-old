#import colander
#import deform.widget

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPCreated, HTTPNotAcceptable, HTTPNotImplemented, HTTPUnauthorized, HTTPOk
from pyramid.exceptions import NotFound
from pyramid.renderers import get_renderer
from pyramid.security import remember, forget, authenticated_userid
from pyramid.view import view_config, forbidden_view_config
from pyramid.response import FileResponse, Response

import os, shutil, re, uuid, glob
#import json

from . import settings

from . import DBSession
from .models import Pipeline, DotPipeREdit, DotPipeR, Package, Note
from .models import Dot, NodeData
from .models import dotquote, dotunquote, validate_dot_node_id, validate_dot_identifier, validate_R_identifier, validate_DotPipeR_fn_param_val

from .security import User

from .exceptions import Error, InputError, PipelineEditConflict, RViewMethodNotImplemented, ValidationError, DotNodeExistsError, DotNodeDoesNotExistError

def dotunquote_dict(d):
    new = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = dotunquote_dict(v)
            new[k] = v
        else:
            new[k] = dotunquote(v)
    return new

def dotquote_dict(d):
    new = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = dotquote_dict(v)
            new[k] = v
        else:
            new[k] = dotquote(v)
    return new

def set_node_attrs(dot, node_id, fn_params):
    node = dot.get_node(node_id)[0]
    node.obj_dict['attributes'] = {} # FIXME: this is a hack
    for edge in dot.get_edges():
        dest = edge.get_destination()
        if dest == node_id:
            src = edge.get_source()
            dot.del_edge(src,dest)
    try:
        fn_param_type_keys = []
#a = {'a[][1]':1, 'a[][4]':2, 'b':3, 'a[][3]':4}
        for k in fn_params.keys():
            if re.match('^fn_param_types\[\]',k) is not None:
                fn_param_type_keys.append(k)
        fn_param_type_keys.sort()
        fn_param_types = []
        for k in fn_param_type_keys:
            fn_param_types.append(fn_params[k][0])
    except KeyError:
        raise ValidationError('fn_param_types[]','') #FIXME: need to return some message to the user
    if len(fn_param_types) > 0:
        try:
            fn_param_names = fn_params['fn_param_names[]']
        except KeyError:
            raise ValidationError('fn_param_names[]','') #FIXME: need a different Exception type
        try:
            fn_param_vals = fn_params['fn_param_vals[]']
        except KeyError:
            raise ValidationError('fn_param_vals[]','')
        for i in range(0,len(fn_param_names)):
            if fn_param_types[i] == "node":
                if not validate_dot_node_id(fn_param_vals[i]):
                    raise(ValidationError('fn_param_vals[]',fn_param_vals[i]))
                if dot.get_node(fn_param_vals[i]) == []:
                    raise(ValidationError('fn_param_vals[]',fn_param_vals[i]))
                edge = dot.add_edge(fn_param_vals[i], node_id) #FIXME: change conditional structure
                edge.set("arg",dotquote(fn_param_names[i]))
            elif fn_param_types[i] == "file" or fn_param_types[i] == "text":
                name = dotquote(fn_param_names[i])
                val = dotquote(fn_param_vals[i])
                if validate_dot_identifier(name) and validate_R_identifier(dotunquote(name)):
                    if validate_DotPipeR_fn_param_val(dotunquote(val)):
                        print("name: %s; val: %s" %(name,val))
                        node.set(name,val)
                    else:
                        raise(ValidationError(name,val))
                else:
                    raise(ValidationError('fn_param_names[]',name))
    #        elif fn_param_types[i] == "text":
    #            node.set(dotquote(fn_param_names[i]),dotquote(fn_param_vals[i]))
            else:
                raise(ValidationError('fn_param_types[]',fn_param_types[i]))

#class WikiPage(colander.MappingSchema):
#    title = colander.SchemaNode(colander.String())
#    body = colander.SchemaNode(
#        colander.String(),
#        widget=deform.widget.RichTextWidget()
#    )

@view_config(context=Error, renderer='templates/errors/error.pt')
def error(exc, request):
    return(dict(title='Error', exc=exc, view=Root()))

@view_config(context=PipelineEditConflict, renderer='templates/errors/conflict.pt')
def input_error(exc, request):
    return(dict(title='Warning', exc=exc, view=Root()))

class Root(object):
    @reify
    def layout(self):
        renderer = get_renderer("templates/layout.pt")
        return(renderer.implementation().macros['layout'])

    @reify
    def macros(self):
        renderer = get_renderer("templates/macros/macros.pt")
        return(renderer.implementation().macros)

    @reify
    def files_macros(self):
        renderer = get_renderer("templates/macros/files.pt")
        return(renderer.implementation().macros)

    @reify
    def create_macros(self):
        renderer = get_renderer("templates/macros/create.pt")
        return(renderer.implementation().macros)


class App(Root):
    def __init__(self, request):
        self.request = request
        self.user = self.request.context.user
#        if self.request.context.logged_in:
#            self.user = DBSession.query(User).filter(User.username==self.request.context.logged_in).one()
#        else:
#            self.user = None


class RAccess(App):
    def __init__(self, request):
        super().__init__(request)

#    @view_config(renderer="json", route_name='R_fn_params', permission='view')
#    def fn_params(self):
#        package = self.request.json_body['package']
#        fn = self.request.json_body['fn']
#        print(fn)
#        if fn is not None:
#            print("got function params")
#            return(dict(fn_params=self.request.context.R_fn_formals(package, fn)))
#        else:
#            return(dict())
#
#    @view_config(renderer="json", route_name='R_get_fns', permission='view')
#    def get_fns(self):
#        package = self.request.json_body['package']
#        if package is not None:
#            print("got function params")
#            return(self.request.context.R_get_fns(package))
#        else:
#            return([])

class NonPipelineViews(App):
    def __init__(self, request):
        super().__init__(request)

    @view_config(route_name='browse',
                 permission='view',
                 renderer='templates/browse.pt')
    def browse(self):
        if self.user:
            mypipelines = DBSession.query(Pipeline).filter(Pipeline.owner==self.user.uid).order_by(Pipeline.id)
        else:
            mypipelines = None
        public_pipelines = DBSession.query(Pipeline).filter(Pipeline.permissions%2==1).order_by(Pipeline.id)
        return dict(title='Pipelines', mypipelines=mypipelines, public_pipelines=public_pipelines)

    @view_config(route_name='create', permission='view')
    def create(self):
        temp_file_name = '%s.dot' % uuid.uuid4()
        temp_file_path = os.path.join('/tmp', temp_file_name + '~')
        file_path = os.path.join(settings.dot_path,temp_file_name)
        print(settings.upload_dir)
#        print(self.request.context.logged_in)
        dot_file_input = self.request.params.get("dot_file")
        packages = self.request.params.getall("packages")
        print("selected packages~~~~~~~~~~~~~~~"+str(packages))
        if dot_file_input is not None and hasattr(dot_file_input,"filename") and hasattr(dot_file_input,"file"): #FIXME: is it necessary to check the last condition?
            filename = self.request.params.get("dot_file").filename
#        filename = self.request.POST['dot_file'].filename
            input_file = self.request.POST['dot_file'].file
        # Note that we are generating our own filename instead of trusting
        # the incoming filename since that might result in insecure paths.
        # Please note that in a real application you would not use /tmp,
        # and if you write to an untrusted location you will need to do
        # some extra work to prevent symlink attacks.

        # We first write to a temporary file to prevent incomplete files from
        # being used.
            input_file = self.request.POST['dot_file'].file
#            output_file = open(temp_file_path, 'wb')
        
            # Finally write the data to a temporary file
#            input_file.seek(0)
#            while True:
#                data = input_file.read(2<<16)
#                if not data:
#                    break
#            with open(temp_file_path, 'wb') as output_file:
#                output_file.write(data)
#            output_file.write(data)
#            output_file.close()
    
            with open( temp_file_path, 'wb') as f:
                input_file.seek(0)
                data = input_file.read(2<<16)
                f.write(data)
                f.close()
            os.rename(temp_file_path, file_path)

    
        # Finally write the data to a temporary file
#            input_file.seek(0)
#            while True:
#                data = input_file.read(2<<16)
#                if not data:
#                    break
#            with open(temp_file_path, 'wb') as output_file:
#                output_file.write(data)
            # Now that we know the file has been fully saved to disk move it into place.

#            os.rename(temp_file_path, file_path)

            # If your data is really critical you may want to force it to disk first
            # using output_file.flush(); os.fsync(output_file.fileno())
    
        else:
            shutil.copy2(settings.dot_template_path, file_path)

        name = self.request.params.get("name")
        pipeline = Pipeline(name=name, uri_ref=temp_file_name, owner=self.user.uid, group=1, permissions='7') #FIXME: need to check if logged in?
        for package in packages:
            print(package)
            Package(pipeline,package)
#        pipeline.load_dot(self.request) #FIXME: we are doing some extra lookup here
        pipeline.dot = Dot.load_from_file_path(file_path) #NOTE: whenever we use this, we have to set the dot's pipeline manually
        pipeline.dot.pipeline = pipeline
        for package in pipeline.packages:
            pipeline.dot.preprocessor_lines += '#library("%s")\n' %package.package
        pipeline.dot.write(file_path)
        DBSession.add(pipeline)
        DBSession.flush()
        print(pipeline.id)
        return HTTPFound(location = self.request.route_url('view', pipeline_id=pipeline.id))

    @view_config(route_name='files', permission='view', renderer='templates/files.pt')
    def files(self):
        from os import listdir
        from os.path import isfile, join
        try:
            path = os.path.join(settings.upload_dir,self.request.context.user.username)
            files = [ f for f in listdir(path) if isfile(join(path,f)) ]
        except Exception:
            files = []
        return dict(title='User files', files=files)

    def get_file_size(self, file):
        file.seek(0, 2) # Seek to the end of the file
        size = file.tell() # Get the position of EOF
        file.seek(0) # Reset the file position to the beginning
        return size

    def validate(self, file):
        if file['size'] < settings.MIN_FILE_SIZE:
            file['error'] = 'minFileSize'
        elif file['size'] > settings.MAX_FILE_SIZE:
            file['error'] = 'maxFileSize'
#        elif not ACCEPT_FILE_TYPES.match(file['type']):
#            file['error'] = 'acceptFileTypes'
        else:
            return True
        return False

    @view_config(route_name='upload', request_method='POST')
    def post(self):
        results = []
        for name, fieldStorage in self.request.POST.items():
            result = {}
            result['name'] = os.path.basename(fieldStorage.filename)
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                filename_pattern = "[a-zA-Z0-9_]{1,200}\.[a-zA-Z0-9]{1,10}"
                if re.match(filename_pattern, result['name']) is None:
                    raise HTTPNotAcceptable
                else:
                    if not os.path.exists(settings.upload_dir):
                        os.makedirs(settings.upload_dir)
                    d = os.path.join(settings.upload_dir,self.request.context.user.username)
                    if not os.path.exists(d):
                        os.makedirs(d)
                    # prevent symlink attacks.
                    file_path = os.path.join(d,result['name'])
        
                    with open( file_path, 'wb') as f:
                        fieldStorage.file.seek(0)
                        data = fieldStorage.file.read()
                        f.write(data)
                        f.close()
        
                    results.append(result)
        #        return results
        return HTTPFound(location = self.request.route_url('files'))
#        return(Response('OK'))

#    @view_config(route_name='upload', request_method='POST')
    def upload(self):
        filename = self.request.POST['file'].filename
        print(settings.upload_dir)
        print(self.request.context.user.username)
        print(filename)
        input_file = self.request.POST['file'].file
#        try:
#            file_input = self.request.params.get("file")
#            filename = file_input.filename
#            file_path = os.path.join(os.path.join(settings.upload_dir,self.logged_in),filename)
#            input_file = self.request.POST['file'].file
#        except Exception as e:
#            print(e)
#            raise HTTPNotImplemented # FIXME: handle this exception

        filename_pattern = "[a-zA-Z0-9_]{1,200}\.[a-zA-Z0-9]{1,10}"
        if re.match(filename_pattern, filename) is None:
            raise HTTPNotAcceptable
        else:
            if not os.path.exists(settings.upload_dir):
                os.makedirs(settings.upload_dir)
            d = os.path.join(settings.upload_dir,self.request.context.user.username)
            if not os.path.exists(d):
                os.makedirs(d)
            # prevent symlink attacks.
            file_path = os.path.join(d,filename)
    
            # write to a temporary file to prevent incomplete files from being used.
            temp_file_name = '%s' % uuid.uuid4()
            temp_file_path = os.path.join('/tmp', temp_file_name + '~')
            output_file = open(temp_file_path, 'wb')
        
            # Finally write the data to a temporary file
            input_file.seek(0)
            while True:
                data = input_file.read(2<<16)
                if not data:
                    break
            output_file.write(data)
            output_file.close()

#            os.rename(temp_file_path, file_path)
            return(Response('OK'))
#            raise HTTPCreated


class PipelineViews(App):
    def __init__(self, request):
        super().__init__(request)
        self.request = request
        self.pipeline = self.request.context.pipeline
#        renderer = get_renderer("templates/layout.pt")
#        self.layout = renderer.implementation().macros['layout']
        self.confirm = False

    @reify
    def pipeline_macros(self):
        renderer = get_renderer("templates/macros/pipeline.pt")
        return(renderer.implementation().macros)

    @reify
    def notes_macros(self):
        renderer = get_renderer("templates/macros/notes.pt")
        return(renderer.implementation().macros)

    @reify
    def addnode_macros(self):
        renderer = get_renderer("templates/macros/addnode.pt")
        return(renderer.implementation().macros)

    @reify
    def editnode_macros(self):
        renderer = get_renderer("templates/macros/editnode.pt")
        return(renderer.implementation().macros)

    @reify
    def pipe_macros(self):
        renderer = get_renderer("templates/macros/pipe.pt")
        return(renderer.implementation().macros)

    @reify
    def simple_edit_fns_macros(self):
        renderer = get_renderer("templates/macros/simple_edit_fns.pt")
        return(renderer.implementation().macros)

    @view_config(route_name='pipelines_static',permission='view')
    def static(self):
        return FileResponse(self.pipeline.dot.file_path, request=self.request)

    @view_config(route_name='status',permission='view', renderer='templates/status.pt')
    def status(self):
        return dict(pipeline=self.pipeline, title=self.pipeline.name, request=self.request, dot=self.pipeline.dot)

    @view_config(route_name='run',permission='view')
    def run(self):
        self.pipeline.run(self.request.context)
        return HTTPFound(location = self.request.route_url('status', pipeline_id=self.pipeline.id))

    @view_config(route_name='notes',
                 permission='view',
                 renderer='templates/notes.pt')
    def notes(self):
        node = self.request.matchdict['node']
        self.pipeline.dot.annotate() #FIXME: do I want this here?
        return dict(pipeline=self.pipeline, title=self.pipeline.name, node=node, request=self.request, dot=self.pipeline.dot)

    @view_config(route_name='addnote', permission='view')
    def addnote(self):
        node = self.request.matchdict['node']
        note_text = self.request.params.get('note')
        note = Note(self.pipeline, node, note_text)
        DBSession.add(note)
#        return HTTPFound(location = self.request.route_url('view', pipeline_id=self.pipeline.id))
        return HTTPFound(location = self.request.route_url('notes', pipeline_id=self.pipeline.id, node=node))

    @view_config(route_name='rmnote', permission='view')
    def rmnote(self):
        node = self.request.matchdict['node']
        note = self.request.matchdict['note']
        DBSession.query(Note).filter(Note.id==note).delete()
        return HTTPFound(location = self.request.route_url('notes', pipeline_id=self.pipeline.id, node=node))

    @view_config(route_name='mod_attr', permission='view')
    def mod_attr(self):
        if 'form.submitted' in self.request.params:
            self.pipeline.name = self.request.session.get('name')
            DBSession.add(self.pipeline)
        return HTTPFound(location = self.request.route_url('browse'))

    @view_config(route_name='view',
                 permission='view',
                 renderer='templates/view_pipeline.pt')
    def view(self):
        self.pipeline.dot.annotate() #FIXME: do I want this here?
        return dict(pipeline=self.pipeline, title=self.pipeline.name, request=self.request, dot=self.pipeline.dot)

    @view_config(route_name='view_node_data',
                 permission='view',
                 renderer='templates/view_node_data.pt')
    def view_node_data(self):
#        pipeline = Pipeline.lookup(self.request.matchdict['pipeline_id'])
        from rpy2.rinterface import NULL
        node = self.request.matchdict['node']
#        dot = Dot.load_from_url(pipeline.url(self.request))
        node_data = NodeData(self.pipeline.dot,node)
#        node_data = dot.node_data(node)
        view_method = self.request.params.get('view_method')
        node_class = node_data.get_class(self.request.context)
        if view_method is None:
            view_method = "default"
#        try:
        nodeview = node_data.view(view_method,self.request.context)
        view_methods = node_data.view_methods(self.request.context)
#        view_methods = []
#        for tmpl in map(os.path.basename,glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)),"nodeview","matrix")+"/*.pt")):
#            view_methods.append(re.sub("\.pt$","",tmpl))
#        view_methods = glob.glob(os.path.join(os.path.dirname(os.path.realpath(__file__)),"nodeview","matrix")+"/*.pt"))
#            view_methods = node_data.view_methods(self.request.context)
#            if view_method in view_methods::
#                node_data.view(view_method,self.request.context)
#             node_data.view(view_method,self.request.context)
#            else:
#                raise(RViewMethodNotImplemented(node_class,view_method)) #FIXME: this probably never gets raised because this condition would produce an error
#        except Exception:
#            raise RViewMethodNotImplemented(node_class,view_method)
        
       
        return dict(pipeline=self.pipeline, title=node, node=node_data, node_class=node_class, selected_view_method=view_method, view_methods=view_methods, nodeview=nodeview)
#        return dict(pipeline=self.pipeline, title=node, node=node_data, node_class=node_class, selected_view_method=view_method, view_methods=view_methods, NULL=NULL)
        
    @view_config(renderer="json", route_name='get_node_info', permission='view')
    def get_node_info(self):
        try:
            node_id = self.request.json_body['node_id'] #FIXME: can use routes instead?
        except KeyError:
            raise NotFound
        if node_id is not None:
            node = self.pipeline.dot.get_node(node_id)
            args = node[0].get_attributes()
            node_call = args.pop('call')
            nodeargs = {}
            for edge in self.pipeline.dot.get_edges():
                dest = edge.get_destination()
                if dest == node_id:
                    src = edge.get_source()
                    arg = edge.get("arg")
                    nodeargs[arg] = src
            fn_params=self.pipeline.R_fn_formals(node_call, self.request.context)
            fn_params_typed = {}
            key_list = []
            for key in fn_params['key_list']:
                if key in args.keys():
                    key_list.append(key)
                    fn_params_typed[key] = {'type': 'text', 'val': dotunquote(args[key])}
                    print(dotunquote(args[key]))
                if key in nodeargs.keys():
                    key_list.append(key)
                    fn_params_typed[key] = {'type': 'node', 'val': dotunquote(nodeargs[key])}
                    print(dotunquote(nodeargs[key]))

#            node_info = dotunquote_dict({'node_call': node_call, 'fn_params': fn_params_typed})
#            node_info['key_list'] = key_list
            node_info = {'node_call': node_call, 'fn_params': fn_params_typed, 'key_list': key_list}
            return(node_info)
        else:
            return(dict())

    @view_config(route_name='select_nodes',
                 permission='view',
                 renderer='templates/select_nodes.pt')
    def select_nodes_form(self):
        return dict(dot=self.pipeline.dot)

    @view_config(route_name='edit',
                 permission='view',
                 renderer='templates/edit_pipeline.pt')
    def edit(self):
        print(self.pipeline.dot.get_nodes())
        print(self.pipeline.dot.file_path)
        print(self.request.session['tmpdot'])
        return dict(pipeline=self.pipeline, title=self.pipeline.name, request=self.request, dot=self.pipeline.dot)

    @view_config(renderer="json", route_name='R_fn_params', permission='view')
    def fn_params(self):
        package = self.request.json_body['package']
        fn = self.request.json_body['fn']
        print(fn)
        if fn is not None:
            print("got function params")
            fn_params=self.pipeline.R_fn_formals(fn, self.request.context)
            print(fn_params)
            return(fn_params)
        else:
            return(dict(fn_params={},key_list=()))

    @view_config(renderer="json", route_name='R_get_fns', permission='view')
    def get_fns(self):
        package = self.request.json_body['package']
        if package is not None:
            print("got function params")
            return(self.pipeline.R_get_fns(self.request.context))
        else:
            return([])

    @view_config(renderer="json", route_name='addnode', permission='view')
    def addnode(self):
        node_id = self.request.json_body['node_id']
        call = self.request.json_body['node_call']
        if not validate_dot_node_id(node_id):
            raise(ValidationError('node_id', node_id))
        if self.pipeline.dot.get_node(node_id) != []:
            raise(DotNodeExistsError(node_id))
        if not validate_R_identifier(call):
            raise(ValidationError('call', call))
        node = self.pipeline.dot.add_node(node_id)
        node.set('call',call)
        print("1")
#        print(self.request.json_body)
        fn_params = self.request.json_body['fn_params']
        print(fn_params)
        set_node_attrs(self.pipeline.dot, node_id, fn_params)
        print("2")
        self.pipeline.dot.write(self.request.session['tmpdot'])
        print("3")
        return(dict(url=self.request.route_url('edit', pipeline_id=self.pipeline.id)))
        
    @view_config(renderer="json", route_name='editnode', permission='view')
    def editnode(self):
        node_id = self.request.json_body['node_id']
        call = self.request.json_body['node_call']
        if not validate_dot_node_id(node_id):
            raise(ValidationError('node_id', node_id))
        if self.pipeline.dot.get_node(node_id) == []:
            raise(DotNodeDoesNotExistError(node_id))
        if not validate_R_identifier(call):
            raise(ValidationError('call', call))
        node = self.pipeline.dot.get_node(node_id)[0]
        node.obj_dict['attributes'] = {} # FIXME: this is a hack
#        print(self.request.json_body)
        fn_params = self.request.json_body['fn_params']
        print(fn_params)
        set_node_attrs(self.pipeline.dot, node_id, fn_params)
        node.set('call',call)
        print("2")
        self.pipeline.dot.write(self.request.session['tmpdot'])
        print("3")
        return(dict(url=self.request.route_url('edit', pipeline_id=self.pipeline.id)))

    @view_config(route_name='rmnodes',
                 permission='view')
    def rmnodes(self):
        pipe_to = []
#        print(self.request.body.decode('utf-8'))
#        json_body = json.loads(self.request.body.decode('utf-8'))
#        for k, v in json_body.items():
        for k, v in self.request.json_body['selected_nodes'].items():
            if str(v) == '1':
                print("deleting node %s" %k)
                self.pipeline.dot.excise_node(k)
        self.pipeline.dot.write(self.request.session['tmpdot'])
        return HTTPFound(location=self.pipeline.dot.draw_svg(self.request))

    @view_config(route_name='pipeto',
                 permission='view')
    def pipeto(self):
        pipeline = Pipeline.lookup(self.request.matchdict['pipeline_id'])
#        node_id = self.request.matchdict['node_id']
#        call = self.request.matchdict['node_call']
        if self.request.session.get('pipeline_id') != pipeline.id:
            raise NotFound #FIXME: we should return an error message to the user saying that the pipeline_id passed to the app does not match the pipeline stored in the session for editing
        if self.request.session['tmpdot'] is None:
            raise NotFound
        dot = Dot.load_from_file_path(self.request.session['tmpdot'])
        if dot is None:
            raise NotFound
        pipe_to = []
        for k, v in self.request.json_body['pipe_to'].items():
            if str(v) == '1':
                pipe_to.append(k)
        for k, v in self.request.json_body['pipe_from'].items():
            print(k)
            print(str(v))
            if str(v) == '1':
                for to in pipe_to:
                    print("adding edge from %s to %s " %(k, to))
                dot.add_edge(k, to)
        print(self.request.json_body['pipe_to'])
        print(self.request.json_body['pipe_from'])
        dot.write(self.request.session['tmpdot'])
        return HTTPFound(location=self.pipeline.dot.draw_svg(self.request))

    @view_config(renderer="json", route_name='save', permission='view')
    def save(self):
#        pipeline = Pipeline.lookup(self.request.matchdict['pipeline_id'])
#        if self.request.session.get('pipeline_id') != pipeline.id:
#            raise NotFound #FIXME: we should return an error message to the user saying that the pipeline_id passed to the app does not match the pipeline stored in the session for editing
        if self.request.session['tmpdot'] is None:
            raise NotFound # FIXME: should tell the user that there was nothing to save
#        dot = Dot.load_from_file_path(self.request.session['tmpdot'])
#        if dot is None:
#            raise NotFound
        file_path = os.path.join(settings.dot_path,self.pipeline.uri_ref)
        self.pipeline.dot.write(file_path)
        self.request.session['pipeline_id']=None
        self.request.session['tmpdot']=None
        return(dict(url=self.request.route_url('view', pipeline_id=self.pipeline.id)))

class Login(App):
    def __init__(self, request):
        super().__init__(request)
#        self.request = request
        renderer = get_renderer("templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
#        self.logged_in = authenticated_userid(request)
        self.confirm = False

#    @view_config(route_name='login_persona',renderer='templates/login_persona.pt')
#    def login_persona(self):
#        return dict(request=self.request)

    @view_config(route_name='login', renderer='templates/login.pt')
    @forbidden_view_config(renderer='templates/login.pt')
    def login(self):
        request = self.request
        login_url = request.route_url('login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            try:
                user = DBSession.query(User).filter(User.username==login).one()
            except:
                raise HTTPUnauthorized
                pass # FIXME: handle user not 
            else:
                if user.validate_password(password):
                    headers = remember(request, login, policies=['internal'])
                    return HTTPFound(location=came_from,
                                     headers=headers)
            print("error:", user.username, " cf. ", login)
            message = 'Failed login'
            raise HTTPUnauthorized

        return dict(
            title='Login',
            message=message,
            came_from=came_from,
            login=login,
            password=password,
        )

    @view_config(route_name='logout')
    def logout(self):
        request = self.request
#        request.response.headers.extend(forget(request))
#        return request.response
        headers = forget(request)
        url = request.route_url('login')
        return HTTPFound(location=url,
                         headers=headers)


