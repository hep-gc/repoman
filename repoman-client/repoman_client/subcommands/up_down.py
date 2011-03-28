from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError
from repoman_client.utils import yes_or_no
from repoman_client import imageutils
from argparse import ArgumentParser
import sys
import logging


class UploadImage(SubCommand):
    command_group = 'advanced'
    command = 'upload-image'
    alias = 'up'
    description = 'Upload an image file to the repository at an existing location'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('image', help='The image you want to upload to')
        p.add_argument('--file', help='Path to the image you are uploading')
        return p

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('UploadImage')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
    
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            repo.upload_image(args.image, args.file)
        except RepomanError, e:
            print e
            sys.exit(1)


class DownloadImage(SubCommand):
    command_group = 'advanced'
    command = 'download-image'
    alias = 'down'
    description = 'Download the specified image file'

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('image')
        p.add_argument('-d', '--dest', metavar='PATH',
                       help='Optional destination to save image to.')
        return p

    def __call__(self, args, extra_args=None):
        log = logging.getLogger('DownloadImage')
        log.debug("args: '%s' extra_args: '%s'" % (args, extra_args))
    
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            repo.download_image(args.image, args.dest)
        except RepomanError, e:
            print e
            sys.exit(1)



class Save(SubCommand):
    command = 'save'
    alias = None
    description = 'snapshot and upload current system'
    parse_known_args = True

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.usage = "save name [-h] [-f] [--metadata value [--metadata value ...]]"
        p.epilog = "See documentation for a list of required and optional metadata"
        p.add_argument('-f', '--force', action='store_true', default=False,
                       help='Force uploading even if it overwrites an existing image')
        p.add_argument('--gzip', action='store_true', default=False,
                       help='Upload the image compressed with gzip.')
        p.add_argument('--resize',help='create an image with a new size (in MB)')
        return p

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

        # this is a bit messy.  Maybe return conflict object from server?
        try:
            log.info("opening /.image.metadata file to store image metadata.")
            meta_file = open('/.image.metadata', 'w')
            image = repo.create_image_metadata(**kwargs)
            print "[OK]     Creating new image meatadata."
        except RepomanError, e:
            if e.status == 409 and not args.force:
                print "An image with that name already exists."
                if not yes_or_no('Do you want to overwrite? [yes]/[n]o: '):
                    print "Aborting.  Please select a new image name or force overwrite"
                    sys.exit(1)
                else:
                    log.info("User has confirmed overwritting existing image.")
                    print "Image will be overwritten."
                    try:
                        # update metedata here!
                        image = repo.describe_image(kwargs['name'])
                    except RepomanError, e:
                        log.error("%s" % e)
                        print e
                        sys.exit(1)
            elif e.status == 409 and args.force:
                log.info("'--force' option found.  Image is being overwritten")
                print "Image will be overwritten."
                try:
                    image = repo.describe_image(kwargs['name'])
                except RepomanError, e:
                    log.error("%s" % e)
                    print e
                    sys.exit(1)
            else:
                log.error("Save failed.")
                log.error("%s" % e)
                print "[FAILED] Creating new image metadata.\n\t-%s" % e
                print "Aborting snapshot."
                sys.exit(1)
        except IOError:
            log.error("could not write to the root of the filesystem")
            print "[Failed] could not write to /.image.metadata, are you root?"
            sys.exit(1)

        # Write metadata to filesystem for later use.
        log.info("writing image metadata to file system")
        for k, v in image.iteritems():
            meta_file.write("%s: %s\n" % (k, v))
        meta_file.close()

        # snapshot here
        image_utils = imageutils.ImageUtils(config.lockfile,
                                            config.snapshot,
                                            config.mountpoint,
                                            config.exclude_dirs,
                                            imagesize=args.resize)
        image_utils.create_snapshot()

        #upload
        name = image.get('name')
        print "Uploading snapshot"
        try:
            repo.upload_image(name, config.snapshot, gzip=args.gzip)
        except RepomanError, e:
            print e
            sys.exit(1)


class Get(DownloadImage):
    command_group = None
    command = 'get'
    alias = None

