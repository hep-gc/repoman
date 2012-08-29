from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient
from repoman_client.exceptions import RepomanError, SubcommandFailure
from repoman_client.config import config
from repoman_client.utils import yes_or_no
from repoman_client import imageutils
import sys
import logging


class UploadImage(SubCommand):
    command = 'put-image'
    alias = 'pi'
    description = 'Upload an image file from local disk space to the repoman repository and associate it with an existing image-slot.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('file', help = 'The local image file to upload to the repository.')
        self.get_arg_parser().add_argument('-f', '--force', action='store_true', default=False, help='Overwrite destination image (if present) without confirmation.')
        self.get_arg_parser().add_argument('-h', '--hypervisor', metavar = 'hypervisor', help = 'The hypervisor of the given image.  Ex: xen, kvm.  This argument is optional for single hypervisor images.')
        self.get_arg_parser().add_argument('image', help = 'The name of the image slot to be used.  Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image.  The default is the ID of the current repoman user whih can be determined with the "repoman whoami" command.')

    def __call__(self, args):
        hypervisor = None
        try:
            image_name = args.image
            if args.owner:
                image_name = "%s/%s" % (args.owner, args.image)

            image = self.get_repoman_client(args).describe_image(image_name)

            # Check if image is multi-hypervisor.  If yes, then make sure the user specified
            # the hypervisor at command line.
            if (len(image['hypervisor'].split(',')) > 1) and (not args.hypervisor):
                print "ERROR:  This %s image is a multi-hypervisor image.  You must specify an hypervisor using the --hypervisor command line argument.  Do a 'repoman help put-image' for more information." % args.image
                return

            # If the image is multi-hypervisor and an hypervisor was given at command line,
            # check to make sure it is in the list of hypervisors of that image.
            if args.hypervisor and (args.hypervisor not in image['hypervisor'].split(',')):
                print "ERROR:  The given hypervisor is not supported by this image.  Supported hypervisors for this image are: %s" % (image['hypervisor'])
                return

            if args.hypervisor:
                hypervisor = args.hypervisor
            else:
                hypervisor = image['hypervisor'].strip()

            # Check if destination image already contains an image.
            if self.get_repoman_client(args).uploaded_image_exist(args.image, args.owner, hypervisor=hypervisor) == True and not args.force:
                if not yes_or_no("Image '%s' already contains an image file for hypervisor %s.  Overwrite? [yes]/[n]o:" % (args.image, hypervisor)):
                    return

            print "Uploading %s to image '%s', hypervisor %s ..." % (args.file, args.image, hypervisor)
            self.get_repoman_client(args).upload_image(args.image, args.owner, args.file, hypervisor=hypervisor)
            print "[OK]     %s uploaded to image '%s', hypervisor %s" % (args.file, args.image, hypervisor)
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not upload %s to image '%s', hypervisor %s" % (args.file, args.image, hypervisor), e)


class DownloadImage(SubCommand):
    command = 'get-image'
    alias = 'gi'
    description = 'Download an image from the repository to the specified path.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The image to download.  Use "repoman list-images" to see possible values.') 
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image.  The default is the ID of the current repoman user which can be determined with the "repoman whoami" command.')
        self.get_arg_parser().add_argument('-p', '--path', metavar = 'path', help = 'The destination of the downloaded image.  If omitted, the image is downloaded to a file with the same name as the image into your current working directory.')

    def __call__(self, args):
        try:
            image_name = args.image
            if args.owner:
                image_name = "%s/%s" % (args.owner, args.image)
            print "Downloading image '%s'..." % (args.image)
            self.get_repoman_client(args).download_image(image_name, args.path)
            print "[OK]     Image %s downloaded." % (args.image)
        except RepomanError, e:
            raise SubcommandFailure(self, "Could not download image '%s'..." % (args.image), e)

