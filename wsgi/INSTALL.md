# Install python3.4
cd tmp
wget http://www.python.org/ftp/python/3.4.1/Python-3.4.1.tgz
tar xvzf Python-3.4.1.tgz
cd Python-3.4.1
./configure --prefix=$HOME/opt/Python-3.4.1
make && make install

# Install R-3.2.1
./configure --prefix=${HOME}/opt/R-3.2.1 --enable-R-shlib
make
make install

# add ${HOME}/opt/Python-3.4.1/bin to PATH variable
# add ${HOME}/opt/R-3.2.1/bin to PATH variable
# export R_HOME="${HOME}/opt/R-3.2.1/lib/R"
easy_install-3.4 virtualenv
cd ~
virtualenv-3.4 venv-3.4
source venv-3.4/bin/activate

# Download numpy-1.9.2 (easy_install failed to install this package automatically)
cd numpy-1.9.2/
python setup.py install

cd projects/dotpipeR/wsgi
python setup.py install

# Install python3
cd /tmp
tar xfvjp ~/Downloads/Python-3.3.0.tar.bz2
cd Python-3.3.0/
./configure --prefix=${HOME}/local
make
make install

# Virtualenv

cd /tmp
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.10.1.tar.gz
tar xfvzp virtualenv*
cd virtualenv*
python3 virtualenv.py --no-site-packages ~/venv 

# Install R project (with R shared library enabled)
./configure --prefix=${HOME}/local --enable-R-shlib
make
make install

# Install R packages
source("http://bioconductor.org/biocLite.R")
biocLite("graph")
install.packages("digest")

# Install other R packages used by my pipelines

#source("http://bioconductor.org/biocLite.R")
#pkgs = c("affy","sva","limma","GEOquery","graph","AnnotationDbi","marray","Rgraphviz")
#for(pkg in pkgs) { biocLite(pkg) }
#install.packages("maps")
#install.packages("mapdata")
#install.packages("ggmap")


R CMD INSTALL dotpipeR

# Install other stuff
cd ~/venv
source bin/activate
easy_install pyramid sqlalchemy zope.sqlalchemy pyramid_tm pyramid_chameleon markdown pygments

# Install pydot
git clone https://github.com/nlhepler/pydot
cd pydot
python3 setup.py install

# Install rpy2

cd /tmp
wget https://bitbucket.org/lgautier/rpy2/get/default.tar.gz
tar xfvzp  default.tar.gz
2to3-3.3  lgautier-rpy2-* -o rpy2-python3.3/ -n -W
cd rpy2-python3.3
cp -nr ../lgautier-rpy2*/* .
python setup.py build --r-home /home/cld/local/lib/R install

## ensure that rpy2 finds the right version of R
rpy2 needs to find the correct version of the R shared library, so LD_LIBRARY_PATH needs to be set so tha
t the linker finds the right library


export LD_LIBRARY_PATH=/home/cld/local/lib/R/lib

# Configure mod_wsgi (optional)

When installing mod_wsgi, ensure that the python system that you use to compile is the same as the system referenced in the mod_wsgi configuration.

For example use:

./configure --with-python=/home/cld/local/bin/python3
make
cp .libs/mod_wsgi.so /usr/lib/apache2/modules/mod_wsgi_homebrew.so

with the following configuration:

In /etc/apache/modules.d/70_mod_wsgi.conf

<IfDefine WSGI>
SetEnv R_HOME /home/cld/local/lib/R
WSGIPythonHome /home/cld/local
LoadModule wsgi_module modules/mod_wsgi_homebrew.so
</IfDefine>

Also, the directory containing the proper R libraries can be added to the LDPATH so that Apache will find it. In Gentoo, this can be done by adding this directory to the LDPATH variable in the /etc/env.d/00basic file, and then running env-update.
# vim: ts=4 filetype=apache


