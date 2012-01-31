from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
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
        self.get_arg_parser().add_argument('image', help = 'The name of the image slot to be used.  Use "repoman list-images" to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image.  The default is the ID of the current repoman user whih can be determined with the "repoman whoami" command.')

    def __call__(self, args):
        try:
            image_name = args.image
            if args.owner:
                image_name = "%s/%s" % (args.owner, args.image)
            print "Uploading %s to image '%s'..." % (args.file, args.image)
            self.get_repoman_client(args).upload_image(image_name, args.file)
            print "[OK]     %s uploaded to image '%s'" % (args.file, args.image)
        except RepomanError, e:
            print "[FAILED] Uploading %s to image '%s'.\n\t-%s" % (args.file, args.image, e)
            sys.exit(1)


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
            self.get_repoman_client(args).download_image(image_name, args.path)
        except RepomanError, e:
            print e
            sys.exit(1)


