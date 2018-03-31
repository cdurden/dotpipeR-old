# package settings.py
import os

homedir = os.environ['HOME']
appdir = os.path.join(homedir,"dotpipeR/wsgi")

R_views_source = os.path.join(appdir,"R/views.R")
#upload_dir = os.path.join(appdir,"uploads/")

dot_path = os.path.join(homedir,"dotpipeR/dot/")
dot_template_path = os.path.join(dot_path,"template.dot")
#dotpipeR_cachedir = os.path.join(homedir,"tmp/dotpipeR")
dotpipeR_wd = '/tmp'
dotpipeR_env_name = "DotPipeR"
r_home = os.path.join(homedir,"opt/lib/R")


MIN_FILE_SIZE = 1 # bytes
MAX_FILE_SIZE = 5000000 # bytes
