# Sagemath cloud

## syncing dotpipeR

### Setting up rsync module
[dotpipeR]
    path = /home/cld/projects/dotpipeR
    read only = yes
    auth users = cloud
    secrets file = /etc/rsyncd.secrets
    gid = 1000

### Set up rsyncd secrets file

cloud:password

### on the cloud

rsync -av cloud@aceventura.dyndns.org::dotpipeR/ ~/dotpipeR/

## installing dotpipeR components

See INSTALL.md file in dotpipeR/wsgi directory

### Sagemath URL

https://cloud.sagemath.com/5da1561d-13c8-4ad3-b44e-872df00336f5/port/6547/
