from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.utils import yes_or_no
from repoman_client.imageutils import ImageUtils, ImageUtilError
import sys
import logging
import re



class Save(SubCommand):
    command = 'save-image'
    alias = 'si'
    short_description = 'Takes  a  snapshot  of  your  running  system\'s.'
    description = 'Takes  a  snapshot  of  your  running  system\'s filesystem (except paths listed under system-excludes and  user-excludes in repoman configuration file).  If name is not in your user\'s domain, an image-slot entry is created with  the supplied metadata information.  If name does exist, the image-slot is updated with any given metadata.  Finally, the snapshot is uploaded to the image-slot on the repoman repository.'
    metadata_file = '/.image.metadata'
    require_sudo = True

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The name of the newly created or existing image-slot on the repository.  This will be used to  reference the image when running other repoman commands.  It can only contain ([a-Z][0-9][_][-]) characters.')
        self.get_arg_parser().add_argument('-u', '--unauthenticated_access', choices=['true', 'false'], help = 'Defaults  to false. If set to true, the image may be retrieved by anybody who has the correct URL.')
        self.get_arg_parser().add_argument('--clean', action = 'store_true', default = False, help = 'Remove any existing local snapshots before creating a new one.')
        self.get_arg_parser().add_argument('-c', '--comment', metavar = 'comment', help='Add/Replace the image comment at the end of the description.')
        self.get_arg_parser().add_argument('-d', '--description', metavar = 'value', help = 'Description of the image.')
        self.get_arg_parser().add_argument('-f', '--force', action = 'store_true', default = False, help = 'Force uploading even if it overwrites an existing image.')
        self.get_arg_parser().add_argument('--gzip', action='store_true', default = False, help = 'Upload the image compressed with gzip.')
        self.get_arg_parser().add_argument('-h', '--hypervisor', metavar = 'value', help = 'The hypervisor. Ex: xen, kvm, etc.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image. The default is the ID of the current repoman user which can  be determined with the command "repoman whoami" command.')
        self.get_arg_parser().add_argument('--os_arch', choices = ['x86', 'x86_64'], help = 'The operating system architecture.')
        self.get_arg_parser().add_argument('--os_type', metavar = 'value', help = 'The operating system type. Ex: linux, unix, windows, etc.')
        self.get_arg_parser().add_argument('--os_variant', metavar = 'value', help = 'The operating system variant. Ex: redhat, centos, ubuntu, etc.')
        self.get_arg_parser().add_argument('--resize', type=int, metavar = 'SIZE', help = 'Create  an image with a size of SIZE MB.  The size selected must be big enough to contain the entire filesystem image.  If the size specified is not big enough, repoman will issue an error mesage and exit.')
        self.get_arg_parser().add_argument('--verbose', action='store_true', default = False, help = 'Display verbose output during snapshot.')


    def validate_args(self, args):
        if not re.match('^[a-zA-Z0-9_-]+$', args.image):
            log.info('Invalid image name syntax detected: %s' % (args.image))
            print 'Error: Invalid image name syntax.  Please see "repoman help %s" for acceptable image name syntax.' % (self.command)
            sys.exit(1)


    def write_metadata(self, metadata, metafile):
        # Write metadata to filesystem for later use.
        metafile = open(metafile, 'w')
        for k, v in metadata.iteritems():
            metafile.write("%s: %s\n" % (k, v))
        metafile.close()

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        kwargs={}

        name = args.image
        # Check for proper Gzip extension (if needed)
        if args.gzip:
            if name and name.endswith('.gz'):
                pass
            else:
                log.info("Enforcing '.gz' extension.")
                name += '.gz'
                print ("WARNING: gzip option found, but your image name does not"
                       " end in '.gz'.  Modifying image name to enforce this.")
                print "New image name: '%s'" % (name)

        kwargs['name'] = name

        exists = False
        try:
            image = repo.describe_image(name)
            if image:
                log.info("Found existing image")
                exists = True
        except RepomanError,e:
            if e.status == 404:
                log.debug("Did not find an existing image in repository with same name.")
                pass
            else:
                log.error("Unexpected response occurred when testing if image exists.")
                log.error("%s" % e)
                print "Unexpected response from server.  exiting."
                sys.exit(1)
        
        if exists:
            if args.force:       
                log.info("User is forcing the overwriting of existing image.")
            else:
                print "An image with that name already exists."
                if not yes_or_no('Do you want to overwrite? [yes]/[n]o: '):
                    print "Aborting.  Please select a new image name or force overwrite"
                    sys.exit(1)
                else:
                    log.info("User has confirmed overwritting existing image.")
                    print "Image will be overwritten."
                    
        image_utils = ImageUtils(config.lockfile,
                                 config.snapshot,
                                 config.mountpoint,
                                 config.system_excludes.split(),
                                 config.user_excludes.split(),
                                 size=args.resize*1024*1024)
        
        try:
            # Set image metadata from given arguments.
            if args.unauthenticated_access and args.unauthenticated_access.lower() == 'true':
                kwargs['unauthenticated_access'] = True
            if args.unauthenticated_access and args.unauthenticated_access.lower() == 'false':
                kwargs['unauthenticated_access'] = False
            if args.description:
                kwargs['description'] = args.description
            if args.hypervisor:
                kwargs['hypervisor'] = args.hypervisor
            if args.owner:
                kwargs['owner'] = args.owner
            if args.os_arch:
                kwargs['os_arch'] = args.os_arch
            if args.os_type:
                kwargs['os_type'] = args.os_type
            if args.os_variant:
                kwargs['os_variant'] = args.os_variant

            self.write_metadata(kwargs, self.metadata_file)
        except IOError, e:
            log.error("Unable to write to root fs.")
            log.error("%s" % e)
            print "[Failed] could not write to %s, are you root?" % self.metadata_file
            sys.exit(1)
            
        try:
            print "Starting the snapshot process.  Please be patient, this will take a while."
            image_utils.snapshot_system(verbose=args.verbose, clean=args.clean)
        except ImageUtilError, e:
            print e
            log.error("An error occured during the snapshot process")
            log.error(e)
            sys.exit(1)
            
        if not exists:
            try:
                image = repo.create_image_metadata(**kwargs)
                print "[OK]    Creating image metadata on server."
            except RepomanError, e:
                log.error("Error while creating image slot on server")
                log.error(e)
                print e
                sys.exit(1)
            
        #upload
        print "Uploading snapshot"
        try:
            repo.upload_image(name, config.snapshot, gzip=args.gzip)
        except RepomanError, e:
            log.error("Error while uploading the image")
            log.error(e)
            print e
            sys.exit(1)

        if args.comment:
            try:
                image = repo.describe_image(name)
                if image:
                    # Here we will search for an existing comment and replace it
                    # with the new comment (if it exist).  If it does not exist,
                    # then a new comment will be added at the end of the existing
                    # description.
                    comment_re = '\[\[Comment: .+\]\]'
                    comment_string = '[[Comment: %s]]' % (args.comment)
                    old_description = image.get('description')
                    new_description = ''
                    if image.get('description') is None:
                        new_description = comment_string
                    elif re.search(comment_re, old_description):
                        new_description = re.sub(comment_re, comment_string, old_description)
                    else:
                        new_description = '%s %s' % (old_description, comment_string)
                    kwargs = {'description':new_description}
                    try:
                        repo.modify_image(image.get('name'), **kwargs)
                    except RepomanError, e:
                        print "Failed to add/update image save comment.\n\t-%s" % e
                        sys.exit(1)

            except RepomanError,e:
                if e.status == 404:
                    log.debug("Did not find the image to update the save commant.  This might be caused by someone else who deleted the image just before we were able to update the comment.")
                else:
                    log.error("Unexpected response occurred when testing if image exists.")
                    log.error("%s" % e)
                    print "Unexpected response from server.  Image save comment not updated."
            
