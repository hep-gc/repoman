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


class Get(DownloadImage):
    command_group = None
    command = 'get'
    alias = None

