from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
#from pyramid_multiauth import MultiAuthenticationPolicy
from pyramid_authstack import AuthenticationStackPolicy
from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension

session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

from sqlalchemy import engine_from_config

from .security import groupfinder
#from .security import persona_groupfinder

from pyramid.events import NewRequest
import wsgiref.util

# remap urls (for use with Sagemath cloud)
def urlmap(event):
    wsgiref.util.shift_path_info(event.request.environ)
    wsgiref.util.shift_path_info(event.request.environ)
    wsgiref.util.shift_path_info(event.request.environ)
    event.request.scheme = "http"

def main(global_config, **settings):
    engine = engine_from_config(settings, 'pipelines.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    config = Configurator(settings=settings,
                          session_factory=session_factory,
                          root_factory='dotpipeRwsgi.models.Root')
#    config.add_subscriber(urlmap, NewRequest)

    # Security policies
    authn_policy = AuthenticationStackPolicy()
    authn_policy.add_policy( 'internal', AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512'))
#    authn_policy.add_policy( 'persona', AuthTktAuthenticationPolicy(settings['persona.secret'], callback=persona_groupfinder))
    authz_policy = ACLAuthorizationPolicy()

#    config.include('pyramid_authstack')
#    config.include('pyramid_persona')

#    multiauth configuration
#    policies = [ AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512'),
#                 AuthTktAuthenticationPolicy(settings['persona.secret'], callback=persona_groupfinder) ]
#    authn_policy = MultiAuthenticationPolicy(policies)
#    authn_policy = AuthTktAuthenticationPolicy(settings['persona.secret'], callback=persona_groupfinder)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')

#    config.add_route('login_persona', '/login_persona')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('browse', '/')
    config.add_route('create', '/create')
    config.add_route('upload', '/upload')
    config.add_route('files', '/files')

    config.add_route('pipelines_static', '/pipelines/*subpath', factory='dotpipeRwsgi.models.PipelineStatic')
#    config.add_route('view_dot', '/dot/*subpath', factory='dotpipeRwsgi.models.PipelineStatic')
#    config.add_route('view_dot_node_data', '/dot/*subpath', factory='dotpipeRwsgi.models.PipelineStatic')

    config.add_route('mod_attr', '/mod_attr/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('status', '/status/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('run', '/run/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('view', '/view/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('view_source', '/view_source/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('view_node_data', '/data/{pipeline_id}/{node}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('notes', '/notes/{pipeline_id}/{node}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('addnote', '/addnote/{pipeline_id}/{node}/', factory='dotpipeRwsgi.models.DotPipeR')
    config.add_route('rmnote', '/rmnote/{pipeline_id}/{node}/{note}/', factory='dotpipeRwsgi.models.DotPipeR')

    config.add_route('get_node_info', '/get_node_info/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('select_nodes', '/select_nodes/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('edit', '/edit/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('rmnodes', '/rmnodes/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('R_fn_params', '/R_fn_params/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('R_get_fns', '/R_get_fns/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('addnode', '/addnode/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('editnode', '/editnode/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('save', '/save/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')
    config.add_route('pipeto', '/pipeto/{pipeline_id}/', factory='dotpipeRwsgi.models.DotPipeREdit')

    config.add_static_view(name='static', path='dotpipeRwsgi:static')
#    config.add_static_view('deform_static', 'deform:static/')
    config.scan()
    return config.make_wsgi_app()
