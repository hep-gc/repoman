Repoman-Client 0.2
================================
A client to connect to the Repoman VM repository.

Install Process
--------------------------------

1.  Install prerequisites

        $ yum install python-setuptools
    
        $ easy_install pip

2.  Install repoman-client

        $ pip install repoman-client

3.  Run repoman 

        make-config --repo REPO
     
This will create a configuration file in `~/.repoman-client`.  If you need to specify a different userkey/usercertificate than a grid proxy certificate, use `--usercert USER_CERT --userkey USER_KEY`.  You can also specify a custom configuration file by exporting the REPOMAN_CLIENT_CONFIG variable in your BASH terminal, and custom snapshotting locations with  `--snapshot_location SNAPSHOT_IMAGE_LOCATION --mount_location SNAPSHOT_MOUNT_LOCATION`
      
4.    Run repoman-client with the command `repoman`.

Repoman-client uses grid certificates to authenticate with the repoman server.
Ensure that you have a valid, RFC-compliant grid proxy certificate before running repoman.
(e.g. `$ grid-proxy-init -rfc`)

Command Listing
--------------------------------

help                     |   h

make-config              |   mc

about                    |   a

whoami                   |   whoami

list-user                |   lu

list-groups              |   lg

list-images              |   li

create-user              |   cuser

create-group             |   cg

create-image             |   ci

describe-user            |   du

describe-group           |   dg

describe-image           |   di

modify-user              |   mu

modify-group             |   mg

modify-image             |   mi

remove-user              |   ru

remove-group             |   rg

remove-image             |   ri

upload-image             |   ui

download-image           |   get

share-image              |   si

unshare-image            |   usi

add-users-to-group       |   aug

remove-users-from-group  |   rug

add-permissions          |   ap

remove-permissions       |   rp

snapshot-system          |   ss

upload-snapshot          |   us


Command Usage
--------------------------------

    help | h | --help | -h
        returns this message
    
    make-config | mc --repo REPO --snapshot_location SNAPSHOT_IMAGE_LOCATION --mount_location SNAPSHOT_MOUNT_LOCATION [--usercert CUSTOM_CERT] [--userkey CUSTOM_KEY]
        creates the config file in ~/.repoman-client.  --usercert and --userkey allow the user to specify custom certificates/keys (rather than proxies)

    about | a
        returns information about the client
        
    list-users | lu [--long] [--group GROUP]
        list-users 
            list all users
        list-users --group GROUP
            list all the users in GROUP

    list-groups | lg [--all] [--long] [--user USER]
        list-groups 
            list current users groups
        list-groups --all 
            list all groups
        list-groups --user USER 
            list all groups USER is part of

    list-images | li [--long] [--sharedwith] [--all | --user USER | --group GROUP]
        list-images 
            list the current users images
        list-images --all
            list all images for ALL users
        list-images --sharedwith 
            list all images shared with you
        list-images --user USER 
            list images for the USER
        list-images --sharedwith --user USER 
            list images shared with USER
        list-images --sharedwith --group GROUP
            list images shared with GROUP

    create-user | cu --METAVAR VALUE ...
        create a new user based on metadata specified

    create-group | cg --METAVAR VALUE ...
        create a new group based on metadata specified

    create-image | ci [--file FILE] [--METAVAR VALUE ...]
        create a new image based on metadata specified
        create-image --variable value ... 
            creates the metadata for an image. You need to upload the image seperatly.
        create-image --file FILE --variable value ... 
            creates the image metadata and uploads the file in one go.

    modify-user | mu USER [--METAVAR VALUE ...]
        update the user USER with the metadata specified

    modify-group | mg GROUP [--METAVAR VALUE ...]
        update the group GROUP with the metadata specified

    modify-image | mi [USER/]IMAGE [--METAVAR VALUE ...]
        update the existing image IMAGE with the metadata specified

    remove-user | ru USER
        remove the user USER from repoman

    remove-group | rg GROUP
        remove the group GROUP from repoman

    remove-image | ri [USER/]IMAGE
        remove the image [USER/]IMAGE from repoman

    download-image | get [USER/]IMAGE [--dest DEST]
        download the raw image [USER/]IMAGE and optionally save it to DEST

    upload-image | ui [USER/]IMAGE --file FILE
        upload FILE to the existing repoman image [USER/]IMAGE

    describe-user | du USER
        view the metadata for the user USER

    describe-group | dg GROUP
        view the metadata for the group GROUP

    describe-image | di [USER/]IMAGE
        view the metadata for the image '[USER/]IMAGE'

    share-image | si [USER/]IMAGE (--user USER | --group GROUP)
        share the image [USER/]IMAGE with either GROUP or USER

    unshare-image | usi [USER/]IMAGE (--user USER | --group GROUP)
        unshare the image [USER/]IMAGE with either GROUP or USER

    add-users-to-group | aug GROUP --users USER1 [USER2 ...]
        add users USER1, USER2, ... to the group GROUP

    remove-users-from-group | rug GROUP --users USER1 [USER2 ...]
        remove the users USER1, USER2, ... from the group GROUP

    add-permissions | ap GROUP --permissions PERMISSION1 [PERMISSION2 ...]
        add the PERMISSION, PERMISSION2, ... permissions to the group GROUP

    remove-permissions | rp GROUP --permissions PERMSISSION1 [PERMISSION2 ...]
        remove the PERMISSION1, PERMISSION2, ... permissions from the group GROUP

    whoami
        get the currently logged in user

    snapshot-system | ss [--upload] [--force] [--METAVAR VALUE ...]
        snapshot-system 
            snapshot your system locally (to the destination specified in repoman-client.conf), but do not yet bundle for upload
        snapshot-system --upload --name test_image.gz --description "blah blah balh"
            snapshot the system, bundle it and upload it.
        snapshot-system --force --upload --name test_image.gz --description "blah blah balh"
            same as the command without the --force option, with the exception that it will overwrite an existing image if there is a naming conflict.

    upload-snapshot | us [--force] --METAVAR VALUE ...
        bundle and upload the latest snapshot
        upload-snapshot --name test_image.gz --description "blah blah balh"
            upload the latest snapshot to the server with the specified metadata.
            if the image destination already exists an error will be generated
        upload-snapshot --force --name test_image.gz --description "blah blah balh"
            the --force option will overwrite an existing image if there is a name conflict

Example Workflow
--------------------------------

    $ repoman make-config --repo https://myrepo.com:443
        Config file successfully written.
    $ repoman about
        Repoman-client
        Version:                     0.2
        User certificate:            /tmp/x509up_u102474
        User key:                    /tmp/x509up_u102474
        Repository:                  https://myrepo.com:443
        Snapshot image location:     /tmp/fscopy.img
        Snapshot mount location:     /mnt/fscopy/
    $ repoman whoami
        dbharris
    $ repoman list-images
        Images for user dbharris:
        image-002
        image-004
        image-005
    $ repoman create-image --name image-001 --description "This is my first image." --os_type linux --os_variant "RHEL 5.5"
        Creating image image-001 with metadata: 
        os_variant: RHEL 5.5
        os_type: linux
        name: image-001
        description: This is my first image.
        Metadata uploaded, image created.
    $ repoman describe-image image-001
        uploaded:       Fri Dec 10 23:57:57 2010
        read_only:      False
        uuid:   4fbd797004b911e09f78000e0c68b880
        name:   image-001
        unauthenticated_access:         False
        checksum:       {'type': None, 'value': None}
        os_variant:     RHEL 5.5
        expires:        None
        file_url:       https://localhost:443/api/images/raw/dbharris/image-001
        modified:       Fri Dec 10 23:57:57 2010
        os_arch:        None
        shared_with:    {'users': [], 'groups': []}
        owner_user_name:        dbharris
        version:        0
        hypervisor:     None
        owner:  https://localhost:443/api/users/dbharris
        os_type:        linux
        raw_file_uploaded:      False
        http_file_url:  None
        description:    This is my first image.
    $ repoman upload-image image-001 --file /opt/images/image_1
        Uploading image /opt/images/image_1 with name image-001
          % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                         Dload  Upload   Total   Spent    Left  Speed
        100 5000k    0     0  100 5000k      0  4780k  0:00:01  0:00:01 --:--:-- 5144k
    $ repoman download-image image-001 --dest ~/
        Downloading image dbharris/image-001 and storing it at /hepuser/dbharris/image-001.
          % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                         Dload  Upload   Total   Spent    Left  Speed
        100 5000k    0 5000k    0     0  9247k      0 --:--:-- --:--:-- --:--:-- 10.3M
        Image downloaded successfully.

