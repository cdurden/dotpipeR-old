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

from .settings import R_home
import os
os.environ['R_HOME'] = R_home

from sqlalchemy import engine_from_config

#from .models import DBSession, Base

from .security import groupfinder, persona_groupfinder

def main(global_config, **settings):
    engine = engine_from_config(settings, 'pipelines.')
#    engine.execute("ATTACH DATABASE 'notes.sqlite' as notes")
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
#    config = Configurator(settings=settings,
#                          root_factory='tutorial.models.Root')

    # Security policies
#    authn_policy = AuthTktAuthenticationPolicy(
#        'sosecret', callback=groupfinder, hashalg='sha512')
    config = Configurator(settings=settings,
                          session_factory=session_factory,
                          root_factory='tutorial.models.Root')

    authn_policy = AuthenticationStackPolicy()
# Add an authentication policy with a one-hour timeout to control
# access to sensitive information.
# Add a second authentication policy with a one-year timeout so
# we can identify the user.
    authn_policy.add_policy( 'internal', AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512'))
    authn_policy.add_policy( 'persona', AuthTktAuthenticationPolicy(settings['persona.secret'], callback=persona_groupfinder))

#    config.include('pyramid_authstack')
    config.include('pyramid_chameleon')
    config.include('pyramid_persona')

#    policies = [ AuthTktAuthenticationPolicy('sosecret', callback=groupfinder, hashalg='sha512'),
#                 AuthTktAuthenticationPolicy(settings['persona.secret'], callback=persona_groupfinder) ]
#    authn_policy = MultiAuthenticationPolicy(policies)
#    authn_policy = AuthTktAuthenticationPolicy(settings['persona.secret'], callback=persona_groupfinder)

    authz_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

#    config.add_route('login_persona', '/login_persona')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('browse', '/')
    config.add_route('create', '/create')
    config.add_route('upload', '/upload')
    config.add_route('files', '/files')

    config.add_route('pipelines_static', '/pipelines/*subpath', factory='tutorial.models.PipelineStatic')

    config.add_route('mod_attr', '/mod_attr/{pipeline_id}/', factory='tutorial.models.DotPipeR')
    config.add_route('status', '/status/{pipeline_id}/', factory='tutorial.models.DotPipeR')
    config.add_route('run', '/run/{pipeline_id}/', factory='tutorial.models.DotPipeR')
    config.add_route('view', '/view/{pipeline_id}/', factory='tutorial.models.DotPipeR')
    config.add_route('view_node_data', '/data/{pipeline_id}/{node}/', factory='tutorial.models.DotPipeR')
    config.add_route('notes', '/notes/{pipeline_id}/{node}/', factory='tutorial.models.DotPipeR')
    config.add_route('addnote', '/addnote/{pipeline_id}/{node}/', factory='tutorial.models.DotPipeR')
    config.add_route('rmnote', '/rmnote/{pipeline_id}/{node}/{note}/', factory='tutorial.models.DotPipeR')

    config.add_route('get_node_info', '/get_node_info/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('select_nodes', '/select_nodes/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('edit', '/edit/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('rmnodes', '/rmnodes/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('R_fn_params', '/R_fn_params/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('R_get_fns', '/R_get_fns/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('addnode', '/addnode/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('editnode', '/editnode/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('save', '/save/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')
    config.add_route('pipeto', '/pipeto/{pipeline_id}/', factory='tutorial.models.DotPipeREdit')

    config.add_static_view(name='static', path='tutorial:static')
#    config.add_static_view('deform_static', 'deform:static/')
    config.scan()
    return config.make_wsgi_app()
