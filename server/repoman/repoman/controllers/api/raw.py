import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect, etag_cache

from repoman.lib.base import BaseController, render

# custom imports
from sqlalchemy import join

from repoman.model import meta
from repoman.model.image import Image
from repoman.model.group import Group
from repoman.model.user import User
from repoman.model.form import validate_new_image, validate_modify_image
from repoman.lib.authorization import AllOf, AnyOf, NoneOf
from repoman.lib.authorization import authorize, inline_auth
from repoman.lib.authorization import HasPermission, IsAthuenticated, IsUser, OwnsImage, SharedWith, MemberOf
from repoman.lib import beautify, storage
from repoman.lib import helpers as h
from pylons import app_globals

from time import time
from datetime import datetime
from os import path, remove, rename
import shutil
import sys
###

log = logging.getLogger(__name__)

def auth_403(message):
    abort(403, "403 Forbidden : '%s'" % message)

class RawController(BaseController):

    def test_raw_by_user(self, user, image, hypervisor=None, format='json'):
        """
        This method is use to test if an image has an uploaded file for a given hypervisor.
        Returns only the headers.
        """
        image_q = meta.Session.query(Image)
        image = image_q.filter(Image.name==image)\
                       .filter(Image.owner.has(User.user_name==user))\
                       .first()

        if not image:
            abort(404, '404 Not Found')
        else:
            #pass through http requests and unauthenticated https requests
            if not image.unauthenticated_access:
                inline_auth(AnyOf(AllOf(OwnsImage(image), IsAthuenticated()),
                                  AllOf(SharedWith(image), IsAthuenticated())),
                                  auth_403)

            # If no hypervisor is given, and the image has the hypervisor
            # metadata variable set to something, then lets set the
            # hypervisor to the metadata variable.
            if (hypervisor == None) and (image.hypervisor != None):
                hypervisor = image.hypervisor.split(',')[0]

            # If hypervisor is still None, then let's default to 'xen'.
            # This is mostly to support images that do not have the hypervisor variable
            # set. (pre multi-hypervisor support)
            if hypervisor == None:
                hypervisor = 'xen'

            file_path = path.join(app_globals.image_storage, '%s_%s_%s' % (user, image.name, hypervisor))

            # Check if file actually exists
            if not path.exists(file_path):
                abort(404, '404 Not Found')

            try:
            	content_length = path.getsize(file_path)
            	response.headers['X-content-length'] = str(content_length)
                etag_cache(str(('%s_%s_%s' % (user, image.name, hypervisor)) + '_' + str(image.version)))
            except Exception, e:
            	abort(500, '500 Internal Error')

            return


    def test_raw(self, image, hypervisor=None, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.test_raw_by_user(user=user, image=image, hypervisor=hypervisor, format=format)


    def get_raw_by_user(self, user, image, hypervisor=None, format='json'):
        image_q = meta.Session.query(Image)
        image = image_q.filter(Image.name==image)\
                       .filter(Image.owner.has(User.user_name==user))\
                       .first()

        if not image:
            abort(404, '404 Not Found')
        else:
            if not image.raw_uploaded:
                abort(404, '404 Not Found')

            #pass through http requests and unauthenticated https requests
            if not image.unauthenticated_access:
                inline_auth(AnyOf(AllOf(OwnsImage(image), IsAthuenticated()),
                                  AllOf(SharedWith(image), IsAthuenticated())),
                                  auth_403)

            # If no hypervisor is given, and the image has the hypervisor
            # metadata variable set to something, then lets set the
            # hypervisor to the metadata variable.
            if (hypervisor == None) and (image.hypervisor != None):
                hypervisor = image.hypervisor.split(',')[0]

            # If hypervisor is still None, then let's default to 'xen'.
            # This is mostly to support images that do not have the hypervisor variable
            # set. (pre multi-hypervisor support)
            if hypervisor == None:
                hypervisor = 'xen'

            file_path = path.join(app_globals.image_storage, '%s_%s_%s' % (user, image.name, hypervisor))

            # Check if file actually exists
            if not path.exists(file_path):
                abort(404, '404 Not Found')

            try:
            	content_length = path.getsize(file_path)
            	response.headers['X-content-length'] = str(content_length)
            except Exception, e:
            	abort(500, '500 Internal Error')

            # Set the filename
            #response.headers['Content-Disposition'] = str('attachment; filename="%s"' % (image.name))

            etag_cache(str(('%s_%s_%s' % (user, image.name, hypervisor)) + '_' + str(image.version)))

            image_file = open(file_path, 'rb')

            try:
                return h.stream_img(image_file)
            except Exception, e:
                abort(500, '500 Internal Error')

    def get_raw(self, image, hypervisor=None, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.get_raw_by_user(user=user, image=image, hypervisor=hypervisor, format=format)

