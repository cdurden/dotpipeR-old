import os
import sys
import transaction

from sqlalchemy import engine_from_config, exc

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import (
    DBSession,
    Pipeline,
    Base,
    Package,
    Note
    )
from ..security import (
    User,
    Group,
    Permission,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'pipelines.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = Pipeline(name='Calvi lab endocycle experiment, full gene expression analysis',uri_ref='gse19029.dot', owner=2, group=1, permissions='7')
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Calvi lab endocycle experiment, regression against Dimova E2F/Rb targets',uri_ref='dimova_regression.dot', owner=2, group=1, permissions='7')
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Hello, world!', uri_ref='hello_world.dot', owner=2, group=2, permissions='7')
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Sargasso Sea richness estimation', uri_ref='richest.dot', owner=2, group=2, permissions='7')
        Package(model,"richest")
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Finnish words from Helsinki Sanomat', uri_ref='finnishwords.dot', owner=2, group=2, permissions='7')
        Package(model,"RCurl")
        Package(model,"XML")
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Geographical and climate data associated with Morel mushroom sightings', uri_ref='morelpatterns.dot', owner=2, group=2, permissions='7')
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Gaussian Markov Random Field simulation of gene expression for Escherichia coli regulatory network', uri_ref='sim_ecoli_gmrf.dot', owner=2, group=2, permissions='7')
        Package(model,"GMRF")
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Alok Singh expression analysis of medulloblastom stem cell mouse model', uri_ref='csc_mousemodel.dot', owner=2, group=2, permissions='7')
        Package(model,"GEOquery")
        Package(model,"limma")
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)
        model = Pipeline(name='Sjölunden analysis of food nutrition', uri_ref='diet_analysis.dot', owner=2, group=2, permissions='7')
        if not DBSession.query(Pipeline).filter_by(name=model.name,owner=model.owner).count():
            DBSession.add(model)

        g = Group(group_name='group1')
        if not DBSession.query(Group).filter_by(group_name=g.group_name).count():
            DBSession.add(g)
        else:
            g = DBSession.query(Group).filter_by(group_name=g.group_name).first()

        u = User(username='cld',password='cld',persona_email='cdurden@gmail.com',gid=1)
        
        if not DBSession.query(User).filter_by(username=u.username).count():
            DBSession.add(u)
            g.users.append(u)

        g = Group(group_name='group2')
        if not DBSession.query(Group).filter_by(group_name=g.group_name).count():
            DBSession.add(g)
        else:
            g = DBSession.query(Group).filter_by(group_name=g.group_name).first()

        u = User(username='guest',password='guest',gid=1)
        if not DBSession.query(User).filter_by(username=u.username).count():
            DBSession.add(u)
            g.users.append(u)
        
        p = Permission()
        p.permission_name = 'manage'
        
        if not DBSession.query(Permission).filter_by(permission_name=p.permission_name).count():
            DBSession.add(p)
        else:
            p = DBSession.query(Permission).filter_by(permission_name=p.permission_name).first()
            p.groups.append(g)
