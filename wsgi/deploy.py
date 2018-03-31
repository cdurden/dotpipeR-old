import os
from dotpipeRwsgi import settings

from pyramid.paster import get_app
application = get_app(os.path.join(settings.appdir,'development.ini'), 'main')
