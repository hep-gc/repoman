#Repoman-Client
A client to connect to the Repoman VM repository.

##Install Process
1.  Install prerequisites
        yum install python-setuptools
        easy_install pip

2.  Install repoman-client
        pip install repoman-client

3.  Generate a configuration file
        repoman make-config

This will create a configuration file in `~/.repoman/.repoman.conf`

4.    Run repoman-client with the command `repoman`.

Repoman uses grid certificates to authenticate users with the server.
Ensure that you have a valid, RFC-compliant grid proxy certificate before running repoman.
(e.g. `$ grid-proxy-init -rfc`)

