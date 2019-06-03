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

setup(name='dotpipeR',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = dotpipeR:main
      [console_scripts]
      initialize_dotpipeR_db = dotpipeR.scripts.initializedb:main
      """,
)
