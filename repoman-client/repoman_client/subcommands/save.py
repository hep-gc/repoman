from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError
from repoman_client.utils import yes_or_no
from repoman_client.imageutils import ImageUtils, ImageUtilError
from argparse import ArgumentParser
import sys
import logging
import re



class Save(SubCommand):
    command = 'save'
    alias = None
    description = 'Snapshot and upload current system'
    parse_known_args = False
    metadata_file = '/.image.metadata'
    require_sudo = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "save name [-h] [-f] [--gzip] [--resize RESIZE] [--verbose] [--clean] [--comment COMMENT]"
        p.add_argument('name', help='the name of the new image')
        p.add_argument('-f', '--force', action='store_true', default=False,
                       help='Force uploading even if it overwrites an existing image')
        p.add_argument('--gzip', action='store_true', default=False,
                       help='Upload the image compressed with gzip.')
        p.add_argument('--resize', type=int, default=0,
                       help='Create an image with a new size (in MB)')
        p.add_argument('--verbose', action='store_true', default=False,
                       help='Display verbose output during snapshot')         
        p.add_argument('--clean', action='store_true', default=False,
                       help='Remove any existing local snapshots before creating a new one.')
        p.add_argument('--comment', help='Add/Replace the image comment at the end of the description.')
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
        kwargs={}

        name = args.name
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
        name = image.get('name')
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
            
