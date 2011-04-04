from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError
from repoman_client.utils import yes_or_no
from repoman_client.imageutils import ImageUtils, ImageUtilError
from argparse import ArgumentParser
import sys
import logging



class Save(SubCommand):
    command = 'save'
    alias = None
    description = 'snapshot and upload current system'
    parse_known_args = True
    metadata_file = '/.image.metadata'
    require_sudo = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "save name [-h] [-f] [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
        p.add_argument('-f', '--force', action='store_true', default=False,
                       help='Force uploading even if it overwrites an existing image')
        p.add_argument('--gzip', action='store_true', default=False,
                       help='Upload the image compressed with gzip.')
        p.add_argument('--resize', type=int, default=0,
                       help='create an image with a new size (in MB)')
        p.add_argument('--verbose', action='store_true', default=False,
                       help='display verbose output during snapshot')                       
        return p

    def write_metadata(self, metadata, metafile):
        # Write metadata to filesystem for later use.
        metafile = open(metafile, 'w')
        for k, v in metadata.iteritems():
            metafile.write("%s: %s\n" % (k, v))
        metafile.close()

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('Save')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
        
        repo = RepomanClient(config.host, config.port, config.proxy)
        if extra_args:
            try:
                kwargs = parse_unknown_args(extra_args)
            except ArgumentFormatError, e:
                print e.message
                sys.exit(1)
        else:
            kwargs={}
            
        log.debug("kwargs: '%s'" % kwargs)

        if not kwargs.get('name'):
            log.error("Aborting due to insufficient metadata")
            print "You need to specify '--name IMAGE-NAME' at a minimum."
            sys.exit(1)

        # Check for proper Gzip extension (if needed)
        if args.gzip:
            name = kwargs.get('name') 
            if name and name.endswith('.gz'):
                pass
            else:
                log.info("Enforcing '.gz' extension.")
                kwargs.update({'name':name+'.gz'})
                print ("WARNING: gzip option found, but your image name does not"
                       " end in '.gz'.  Modifying image name to enforce this.")
                print "New image name: '%s'" % (name + '.gz')

        exists = False
        try:
            image = repo.describe_image(kwargs['name'])
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
                                 config.exclude_dirs.split(),
                                 size=args.resize*1024*1024)
        
        try:
            self.write_metadata(kwargs, self.metadata_file)
        except IOError, e:
            log.error("Unable to write to root fs.")
            log.error("%s" % e)
            print "[Failed] could not write to %s, are you root?" % self.metadata_file
            sys.exit(1)
            
        extra_flags = ''
        if args.verbose:
            extra_flags = '--progress --stats'
            
        try:
            print "Starting the snapshot process.  Please be patient, this will take a while."
            image_utils.snapshot_system(rsync_flags=extra_flags)
        except ImageUtilError, e:
            print e
            log.error("An error occured during the snapshot process")
            log.error(e)
            sys.exit(1)
            
        if not exists:
            try:
                repo.create_image_metadata(**kwargs)
                print "[OK]    Creating image metadata on server."
            except RepomanError, e:
                log.error("Error while creating image slot on server")
                log.error(e)
                print e
                sys.exit(1)
            
        #upload
        name = image.get('name')
        print "Uploading snapshot"
        try:
            repo.upload_image(name, config.snapshot, gzip=args.gzip)
        except RepomanError, e:
            log.error("Error while uploading the image")
            log.error(e)
            print e
            sys.exit(1)
