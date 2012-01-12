from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
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
    command = 'get-image'
    alias = 'gi'
    description = 'Download an image from the repository to the specified path.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help = 'The image to download.  Use "repoman list-images" to see possible values.') 
        self.get_arg_parser().add_argument('-o', '--owner', metavar = 'user', help = 'The owner of the named image.  The default is the ID of the current repoman user which can be determined with the "repoman whoami" command.')
        self.get_arg_parser().add_argument('-p', '--path', metavar = 'path', help = 'The destination of the downloaded image.  If omitted, the image is downloaded to a file with the same name as the image into your current working directory.')
        self.get_arg_parser().set_defaults(func=self)

    def __call__(self, args):
        repo = RepomanClient(config.host, config.port, config.proxy)
        try:
            image_name = args.image
            if args.owner:
                image_name = "%s/%s" % (args.owner, args.image)
            repo.download_image(image_name, args.path)
        except RepomanError, e:
            print e
            sys.exit(1)


