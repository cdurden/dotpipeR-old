from setuptools import setup

requires = [
    'pyramid',
    'sqlalchemy',
    'pyramid_chameleon',
    'zope.sqlalchemy',
    'pyramid_tm',
    'pyramid_authstack',
    'markdown',
    'pygments',
    'networkx',
    'pydotreader',
    'pydot',
    'graphviz',
    'rpy2',
#    'matplotlib'
]

setup(name='dotpipeRwsgi',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = dotpipeRwsgi:main
      [console_scripts]
      initialize_dotpipeRwsgi_db = dotpipeRwsgi.scripts.initializedb:main
      """,
)
