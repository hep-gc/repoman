from repoman_client.subcommand import SubCommand
from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.parsers import parse_unknown_args, ArgumentFormatError
from argparse import ArgumentParser
import sys

class UploadImage(SubCommand):
    command_group = 'advanced'
    command = 'upload-image'
    alias = None
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
    alias = None
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

    def get_parser(self):
        p = ArgumentParser(self.description)
        p.add_argument('-f', '--force', action='store_true', default=False,
                       help='Force uploading even if it overwrites an existing image')
        return p

    def __call__(self, args, extra_args=None):
        pass


class Get(DownloadImage):
    command_group = None
    command = 'get'
    alias = None

