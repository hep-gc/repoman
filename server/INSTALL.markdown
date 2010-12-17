# REPOMAN

## Install from PyPi 
1.  Install prerequisites
        yum install python-setuptools gcc sqlite sqlite-devel
        easy_install pip virtualenv

1.  Create a Virtual Environment
        virtualenv --no-site-packages /opt/repoman

1.  Activate the virtual env
        cd /opt/repoman
        source bin/activate

1.  Install repoman
        pip install repoman

1.  Create a file for populating the database with administrators
        vim  $HOME/repoman_admins

    The file should contain lines containing `username,email,client_dn', with no trailing space or lines.

    Example file:
        bob,bob@uvic.ca,/C=CA/O=Grid/OU=phys.uvic.ca/CN=Bob McKenzie
        doug,doug@uvic.ca,/C=CA/O=Grid/OU=phys.uvic.ca/CN=Doug McKenzie

1.  Create and edit the application config
        paster make-config repoman deploy.ini

    Make sure to point `admin_file` to the file you created in the previous step

1.  Create the database
        paster setup-app deploy.ini

    If using the default sqlite DB, ensure that the `apache` user has read/write
    permissions on the database file and the base directory the database file is in.

1.  Create the apache configs
        paster --plugin=repoman make-wsgi-config deploy.ini

1.  Modify the `repoman.conf`

    Make `SSLCertificateFile` point to your host certificate

    Make `SSLCertificateKeyFile` point to your host certificate key

    Make `SSLCACertificatePath` point the directory that contains your Root CA certificates for verifying clients

    Make `SSLCARevocationPath` point to the directory that contains your CRLs for the Root CA certificates

1.  Copy `repoman.conf` to your apache config directory
        cp repoman.conf /etc/httpd/conf.d

1.  Start Apache
        sudo service httpd restart


