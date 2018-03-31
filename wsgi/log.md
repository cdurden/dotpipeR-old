cd /tmp
wget 
tar xfvjp Python-3.3.0.tar.bz2
cd Python-3.3.0
../configure --prefix=${HOME}/local
make
make install
pyvenv ${HOME}/venv/
cd ${HOME}/venv/
source bin/activate
curl -O http://python-distribute.org/distribute_setup.py
python distribute_setup.py
easy_install-3.3 pyramid nose webtest deform sqlalchemy pyramid_tm zope.sqlalchemy
easy_install-3.3 docutils
cd /tmp
wget https://bitbucket.org/prologic/pydot/get/default.tar.gz
cd prologic-pydot-ac76697320d6/
python setup.py install
cd ${HOME}/venv/

git clone https://github.com/nlhepler/pydot-py3.git
cd pydot-py3/
patch -Np1 dot_parser.py py3.3_noncomma.patch
python setup.py install

cd /tmp
wget https://bitbucket.org/lgautier/rpy2/get/default.tar.gz
tar xfvzp  default.tar.gz 
2to3-3.3  lgautier-rpy2-* -o rpy2-python3.3/ -n -W
cd rpy2-python3.3
cp -nr ../lgautier-rpy2*/* .
python setup.py build --r-home /home/cld/local/lib/R install

rpy2 needs to find the correct version of the R shared library, so LD_LIBRARY_PATH needs to be set so that the linker finds the right library



# import Dot class in tutorial/models.py

    from pydot import Dot

# add GraphViews class to tutorial/views.py:

    class GraphViews(object):
        def __init__(self, request):
            self.request = request
            renderer = get_renderer("templates/layout.pt")
            self.layout = renderer.implementation().macros['layout']
            self.logged_in = authenticated_userid(request)
    
        @view_config(route_name='wikipage_view',
                     renderer='templates/wikipage_view.pt')
        def dot_view(self):
            uid = self.request.matchdict['uid']
            page = pages[uid]
            return dict(page=page, title=page['title'])

# create pipelines directory

This directory will need to provide access to static files and allow control of permissions.


# link pipelines/mypipelines/ to ${HOME}/projects/dotpipelines
    
## accessing pipeline files

I think I want to use URLs to provide a flexible way for my application to access pipeline files. This means that I need to register my pipelines into a database, either a file, a section of code, or with an SQL server. I have chosen SQL because the schema is easy to define and it has a convenient interface that is accessible through python. I don't need a description or author attribute because I can specify a way to record using comments in the DOT files. A function to search for text patterns in descriptions could be implemented through a function that parses these fields from the available pipeline files, perhaps also with a caching system.

Categorization of pipelines can be done through mapping tables.

The schema for storing pipelines might also serve to define access permissions and to associate annotations with the pipelines, structures that are essential to the functions of the webapp. However, these constructs might be implemented equally well and concisely with more abstraction, i.e. for general classes for which read, write, and execute permissions might apply. For example, permissions could be defined for a permissions table which maps objects from multiple tables to permissions data, by prefixing a unique type-identifier to the object id (which could be non-unique across classes).

For now, it seems sensible for the pipeline schema to simply define a map from pipeline unique pipeline identifiers to their URLs.

What is the scope of the pipeline identifiers? Are these to be used only internally or also externally to reference pipelines? Should pipeline ids be numeric values? yes.

Do we need to be able to use relative-path references in pipeline URLs? If so, I think the technical term for the field should be URI-reference, and we need to know how to establish a base URI (see RFC-3986 Section 5).

In RFC-3986 Section 4.1
<http://tools.ietf.org/html/rfc3986#section-4.1>
"   A URI-reference is either a URI or a relative reference.  If the URI-reference's prefix does not match the syntax of a scheme followed by its colon separator, then the URI-reference is a relative reference."

<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/assets.html#advanced-static> provides instructions about serving "static assets" manually, so that authentication can be performed for them.

### Addressing cross-system flexibility of mechanism for serving pipeline files as static assets

Could use a configuration variable to set a pipelines directory (see <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/startup.html#deployment-settings>). Then, when register a view callable for every

Can study the static_view class to derive a "view callable" that can process permissions and serve files. This class 
<http://docs.pylonsproject.org/projects/pyramid/en/latest/api/static.html#pyramid.static.static_view>

request.subpath may be of use within a view callable to determine permissions and control access to a static asset.

Per "Pyramid concepts" we can create a route for serving static files which uses a factory that sets __acl__ attributes based on the permissions of a pipeline that matches the 

## Pyramid concepts

pyramid apps serve WSGI apps, which are objects created through one of the Pyramic constructor functions, for example those provided by pyramid.config.Configurator. Configurator optionally takes a root_factory, which is "a callable which accepts a request and returns an arbitrary Python object." the root_factory is the default context resources that is passed to a view found by URL Dispatch. A custom factory can be passed to route to provide authorization through the __acl__ attribute (see <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/urldispatch.html#using-pyramid-security-with-url-dispatch>).

See also <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/security.html#security-chapter>

Some relevant snippets:

"Security in Pyramid, unlike many systems, cleanly and explicitly separates authentication and authorization. Authentication is merely the mechanism by which credentials provided in the request are resolved to one or more principal identifiers. These identifiers represent the users and groups in effect during the request. Authorization then determines access based on the principal identifiers, the view callable being invoked, and the context resource."

"Permissions are used by the active security policy to match the view permission against the resources?s statements about which permissions are granted to which principal in a context in order to answer the question ?is this user allowed to do this?."

## Entensibility

<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extending.html#building-an-extensible-app>

## Pyramid operation 

The following page provides a sense of how a WSGI app works:
<http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/getting_started/01-helloworld/index.html>

Comparing this code to the next, we can see that apparently the following command associates a function with a route name. 

    config.add_view(hello_world, route_name='hello')

In the sequel, the route is "registered" using a configuration directive which is apparently processed by the procedure config.scan. So instead of calling config.add_view, the hello_world procedure is "decorated with": 

    @view_config(route_name='hello')

and the configuration directives are processed by calling

##

It is not obvious how a pyramid configuration .ini works. The section "Analysis" describes the basic processing of this file.
<http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/getting_started/03-config/index.html>




# Questions

How is 

initialize_tutorial_db development.ini

#adding a pipeline

vim tutorial/scripts/initializedb.py
