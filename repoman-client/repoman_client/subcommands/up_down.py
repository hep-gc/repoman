from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError
from repoman_client.utils import yes_or_no
from repoman_client import imageutils
from argparse import ArgumentParser
import sys

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
        return p

    def __call__(self, args, extra_args=None):
        repo = RepomanClient(config.host, config.port, config.proxy)
        if extra_args:
            try:
                kwargs = parse_unknown_args(extra_args)
            except ArgumentFormatError, e:
                print e.message
                sys.exit(1)
        else:
            kwargs={}

        # this is a bit messy.  Maybe return conflict object from server?
        try:
            image = repo.create_image_metadata(**kwargs)
            print "[OK]     Creating new image meatadata."
        except RepomanError, e:
            if e.status == 409 and not args.force:
                print "An image with that name already exists."
                if not yes_or_no('Do you want to overwrite? [yes]/[n]o: '):
                    print "Aborting.  Please select a new image name or force overwrite"
                    sys.exit(1)
                else:
                    print "Image will be overwritten."
                    try:
                        # update metedata here!
                        image = repo.describe_image(kwargs['name'])
                    except RepomanError, e:
                        print e
                        sys.exit(1)
            elif e.status == 409 and args.force:
                print "Image will be overwritten."
                try:
                    image = repo.describe_image(kwargs['name'])
                except RepomanError, e:
                    print e
                    sys.exit(1)
            else:
                print "[FAILED] Creating new image metadata.\n\t-%s" % e
                print "Aborting snapshot."
                sys.exit(1)

        # snapshot here
        image_utils = imageutils.ImageUtils(config.lockfile,
                                            config.snapshot,
                                            config.mountpoint,
                                            config.exclude_dirs)
        image_utils.create_snapshot()

        #upload
        name = image.get('name')
        print "Uploading snapshot"
        try:
            repo.upload_image(name, config.snapshot)
        except RepomanError, e:
            print e
            sys.exit(1)


class Get(DownloadImage):
    command_group = None
    command = 'get'
    alias = None

