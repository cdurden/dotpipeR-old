import sys
import os

import settings

os.environ['R_HOME'] = settings.R_home

def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    print('sys.prefix = %s' % repr(sys.prefix),file=sys.stderr)
    print('sys.path = %s' % repr(sys.path),file=sys.stderr)
    print('R_HOME = %s' % repr(os.environ['R_HOME']),file=sys.stderr)
    return [output]
