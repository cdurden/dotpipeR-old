import os
#import settings
#import importlib
#settings = importlib.import_module("tutorial.settings")
#os.environ['R_HOME'] = settings.R_home

from pyramid.paster import get_app
application = get_app('/home/cld/projects/dotpipeR_webapp/development.ini', 'main')
