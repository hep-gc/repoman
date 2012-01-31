from repoman_client.client import RepomanClient, RepomanError
from repoman_client.config import config
from repoman_client.subcommand import SubCommand
from repoman_client import display
import sys
import logging
import ConfigParser




class DescribeImage(SubCommand):
    command = "describe-image"
    alias = "di"
    description = 'Display all information about an image.'

    def __init__(self):
        SubCommand.__init__(self)

    def init_arg_parser(self):
        self.get_arg_parser().add_argument('image', help='The image to describe.  Use repoman list-images to see possible values.')
        self.get_arg_parser().add_argument('-o', '--owner', help='The owner of the named image.  The default is the ID of the current repoman user which can be determined with the "repoman whoami" command.')

    def __call__(self, args):
        try:
            image_path = args.image
            if args.owner:
                image_path = args.owner + '/' + args.image
            image = self.get_repoman_client(args).describe_image(image_path)
            display.describe_image(image, long_output=True)
        except RepomanError, e:
            print e
            sys.exit(1)

