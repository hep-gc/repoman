import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

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
from repoman.lib import beautify
from repoman.lib.storage import storage
from repoman.lib import helpers as h
from pylons import app_globals

from time import time
from datetime import datetime
from os import path, remove, rename
import shutil
import tempfile
import subprocess
import gzip
import re
import os
###

log = logging.getLogger(__name__)

def auth_403(message):
    abort(403, "403 Forbidden : '%s'" % message)

class ImagesController(BaseController):
    #TODO: move image streaming and upload functions to a new module
    #TODO: set mime-type for streaming file
    #TODO: calc md5sum for image
    #TODO: set image size after upload

    def __before__(self):
        inline_auth(IsAthuenticated(), auth_403)

    def put_raw_by_user(self, user, image, hypervisor, format='json'):
        log.debug('put_raw_by_user')
        image_q = meta.Session.query(Image)
        image = image_q.filter(Image.name==image)\
                       .filter(Image.owner.has(User.user_name==user)).first()
        
        if image:
            inline_auth(OwnsImage(image), auth_403)
            image_file = request.environ.get('STORAGE_MIDDLEWARE_EXTRACTED_FILE')
            
            if image_file:
                final_path = None
                try:
                    file_name = '%s_%s_%s' % (user, image.name, hypervisor)
                    final_path = path.join(app_globals.image_storage, file_name)
                    log.debug("Moving %s to %s" % (image_file, final_path))
                    shutil.move(image_file, final_path)
                except Exception, e:
                    abort(500, '500 Internal Error - Error uploading file %s' %e)
                finally:
                    pass


                image.checksum.cvalue = request.environ.get('STORAGE_MIDDLEWARE_EXTRACTED_FILE_HASH')
                image.checksum.ctype = request.environ.get('STORAGE_MIDDLEWARE_EXTRACTED_FILE_HASH_TYPE')
                image.size = request.environ.get('STORAGE_MIDDLEWARE_EXTRACTED_FILE_LENGTH')

                # IMPORTANT:
                # Image checksum do not make any sense for multi hypervisor images as we have
                # more than one image file per VM, and only a single checksum in the metadata.
                # Ultimately, we could modify the image metadata to contain a list of checksums
                # (one per hypervisor), but for now, let's simply void the checksum.
                if len(image.hypervisor.split(',')) > 1:
                    log.debug("Voiding image checksum for multi-hypervisor images.")
                    image.checksum.cvalue = None # Reset to no checksum.
                    image.checksum.ctype = None

                image.raw_uploaded = True
                image.uploaded = datetime.utcfromtimestamp(time())
                
                # Add the image path to the image.path metadata attribute.
                image_paths = image.path.split(';')
                if final_path not in image_paths:
                    image_paths.append(final_path)
                image.path = ';'.join(image_paths) # For multi-hypervisor images, this will be ';' delimited
                image.version += 1
                image.modified = datetime.utcfromtimestamp(time())
                meta.Session.commit()
        else:
            abort(404, '404 Item not found')


    def put_raw(self, image, hypervisor, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.put_raw_by_user(user=user, image=image, hypervisor=hypervisor, format=format)

    def user_share_by_user(self, user, image, share_with, format='json'):
        image = meta.Session.query(Image)\
                            .filter(Image.name==image)\
                            .filter(Image.owner.has(User.user_name==user))\
                            .first()

        if image:
            inline_auth(OwnsImage(image), auth_403)
            user = meta.Session.query(User)\
                               .filter(User.user_name==share_with)\
                               .first()
            if not user:
                abort(400, 'The user you are trying to share the image with does not exist.')
            if user in image.shared.users:
                return
            else:
                image.shared.users.append(user)
                meta.Session.commit()
        else:
            abort(404, '404 Not Found')

    def group_share_by_user(self, user, image, share_with, format='json'):
        image = meta.Session.query(Image)\
                            .filter(Image.name==image)\
                            .filter(Image.owner.has(User.user_name==user))\
                            .first()

        if image:
            group = meta.Session.query(Group)\
                                .filter(Group.name==share_with).first()
            if not group:
                abort(400, 'The group you are trying to share the image with does not exist.')

            inline_auth(AllOf(OwnsImage(image), MemberOf(share_with)), auth_403)
            if group in image.shared.groups:
                return
            else:
                image.shared.groups.append(group)
                meta.Session.commit()
        else:
            abort(404, '404 Not Found')

    def user_unshare_by_user(self, user, image, share_with, format='json'):
        image = meta.Session.query(Image)\
                            .filter(Image.name==image)\
                            .filter(Image.owner.has(User.user_name==user))\
                            .first()

        if image:
            inline_auth(OwnsImage(image), auth_403)
            user = meta.Session.query(User)\
                               .filter(User.user_name==share_with).first()
            if not user:
                abort(400, '400 Bad Request')
            if user in image.shared.users:
                image.shared.users.remove(user)
                meta.Session.commit()
        else:
            abort(404, '404 Not Found')

    def group_unshare_by_user(self, user, image, share_with, format='json'):
        image = meta.Session.query(Image)\
                            .filter(Image.name==image)\
                            .filter(Image.owner.has(User.user_name==user))\
                            .first()

        if image:
            inline_auth(OwnsImage(image), auth_403)
            group = meta.Session.query(Group)\
                                .filter(Group.name==share_with).first()
            if not group:
                abort(400, '400 Bad Request')
            if group in image.shared.groups:
                image.shared.groups.remove(group)
                meta.Session.commit()
        else:
            abort(404, '404 Not Found')


    def user_share(self, image, share_with, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.user_share_by_user(user=user,
                                        image=image,
                                        share_with=share_with,
                                        format=format)

    def group_share(self, image, share_with, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.group_share_by_user(user=user,
                                         image=image,
                                         share_with=share_with,
                                         format=format)

    def user_unshare(self, image, share_with, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.user_unshare_by_user(user=user,
                                          image=image,
                                          share_with=share_with,
                                          format=format)

    def group_unshare(self, image, share_with, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.group_unshare_by_user(user=user,
                                           image=image,
                                           share_with=share_with,
                                           format=format)

    def upload_raw_by_user(self, user, image, format='json'):
        log.debug('upload_raw_by_user')
        image_q = meta.Session.query(Image)
        image = image_q.filter(Image.name==image)\
                       .filter(Image.owner.has(User.user_name==user)).first()

        if image:
            inline_auth(OwnsImage(image), auth_403)
            file_names = []
            hypervisors = image.hypervisor.split(',')

            # Check if we are in multi-hypervisor mode and if the image is zipped.
            # We currently don't support multi-hypervisor on zipped images.
            if (len(hypervisors) > 1) and self.is_gzip(request.params['file'].filename):
                abort(501, 'Multi-hypervisor support with compressed images is not implemented yet.')

            for hypervisor in hypervisors:
                try:
                    temp_file = request.params['file']
                    file_name = '%s_%s_%s' % (user, image.name, hypervisor)
                    file_names.append(file_name)
                    temp_storage = file_name + '.tmp'
                    final_path = path.join(app_globals.image_storage, file_name)
                    temp_path = path.join(app_globals.image_storage, temp_storage)
                    permanent_file = open(temp_path, 'w')
                    shutil.copyfileobj(temp_file.file, permanent_file)
                    permanent_file.close()
                    temp_file.file.close()
                    rename(temp_path, final_path)
                except Exception, e:
                    remove(temp_path)
                    remove(final_path)
                    abort(500, '500 Internal Error - Error uploading file %s' %e)

            # If image supports multiple hypervisors, mount each of the images and
            # set the grub.conf symlink accordingly.
            #
            if len(hypervisors) > 1:
                for hypervisor in hypervisors:
                    try:
                        image_path = path.join(app_globals.image_storage, '%s_%s_%s' % (user, image.name, hypervisor))
                        self.create_grub_symlink(image_path, hypervisor)
                    except Exception, e:
                        abort(500, '500 Internal Error - Error creating grub symlinks for image %s\n%s' % (image.name, e))


            image.checksum.cvalue = request.environ.get('STORAGE_MIDDLEWARE_EXTRACTED_FILE_HASH')
            image.size = request.environ.get('STORAGE_MIDDLEWARE_EXTRACTED_FILE_LENGTH')

            # IMPORTANT:
            # Image checksum do not make any sense for multi hypervisor images as we have
            # more than one image file per VM, and only a single checksum in the metadata.
            # Ultimately, we could modify the image metadata to contain a list of checksums
            # (one per hypervisor), but for now, let's simply void the checksum.
            if len(hypervisors) > 1:
                log.debug("Voiding image checksum for multi-hypervisor images.")
                image.checksum.cvalue = None # Reset to no checksum.
                image.checksum.ctype = None

            # No update of size and/or checksum?  TODO: Investigate... (Andre)
            image.raw_uploaded = True
            image.path = ';'.join(file_names)
            image.version += 1
            image.modified = datetime.utcfromtimestamp(time())
            meta.Session.commit()
        else:
            abort(404, '404 Item not found')

    def upload_raw(self, image, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.upload_raw_by_user(user=user, image=image, format=format)

    def show_meta_by_user(self, user, image, format='json'):
        image_q = meta.Session.query(Image)
        image = image_q.filter(Image.name==image)\
                       .filter(Image.owner.has(User.user_name==user))\
                       .first()
        
        if image:
            inline_auth(AnyOf(OwnsImage(image), SharedWith(image)), auth_403)
            if format == 'json':
                response.headers['content-type'] = app_globals.json_content_type
                return h.render_json(beautify.image(image))
            else:
                abort(501, '501 Not Implemented')
        else:
            abort(404, '404 Not Found')

    def modify_meta_by_user(self, user, image, format='json'):
        params = validate_modify_image(request.params)

        image_q = meta.Session.query(Image)
        image = image_q.filter(Image.name==image)\
                       .filter(Image.owner.has(User.user_name==user))\
                       .first()

        if image:
            inline_auth(AnyOf(OwnsImage(image), HasPermission('image_modify')), auth_403)
            # Make sure all given attributes exist in the image object.
            for k,v in request.params.iteritems():
                if not hasattr(image, k):
                    abort(400, 'The "%s" image metadata does not exist.  Please check your syntax and try again.' % (k))

            # Do a check here to make sure we do not overwrite
            # any existing image. (Andre)
            if ('name' in params) and (params['name'] != image.name):
                image2 = image_q.filter(Image.name==params['name'])\
                    .filter(Image.owner.has(User.user_name==user))\
                    .first()
                if image2:
                    log.debug('Conflict detected in image renaming: %s -> %s.  Operation aborted.' % (image.name, params['name']))
                    abort(409, 'Cannot rename an image to an existing image.  Operation aborted.')

            # Here we must have some smarts to check if the new metadata has less hypervisors
            # than the previous one.  If this is true, then we must cleanup the images for the
            # hypervisors that are not listed anymore, else we will end up with stale image
            # files on the server.             
            if image.hypervisor != None and params['hypervisor'] and params['hypervisor'] != None:
                previous_hypervisors = image.hypervisor.split(',')
                new_hypervisors = params['hypervisor'].split(',')
                for previous_hypervisor in previous_hypervisors:
                    if previous_hypervisor not in new_hypervisors:
                        # Cleanup
                        image.delete_image_file_for_hypervisor(previous_hypervisor)

            # Check to see if the user wants to assign the image to a new owner.
            # If that is the case, then we need to rename the image file because
            # it has the owner's username hardcoded in its filename.
            if ('owner' in params) and (params['owner'] != None) and (params['owner'] != image.owner):
                # Verify if target user exist
                user_q = meta.Session.query(User)
                target_user = user_q.filter(User.user_name==params['owner']).first()
                if not target_user:
                    abort(400, 'The new image owner %s does not exist.' % (params['owner']))

                log.debug('Changing ownership of image %s from user %s to user %s.' % 
                          (image.name, image.owner.user_name, target_user.user_name))
                if not image.change_image_files_to_new_owner(target_user):
                    # Could not change owner because of conflict.  Abort operation.
                    abort(409, 'Could not change ownership of the image because it conflicts with an image already owned by the target user.  Operation aborted.')
                # Don't forget to delete the 'owner' parameter (it is a special case) 
                # else the setattr call below will not like it.
                del params['owner']

            for k,v in params.iteritems():
                if v != None:
                    setattr(image, k, v)
            image.modified = datetime.utcfromtimestamp(time())
            meta.Session.commit()
        else:
            abort(404, '404 Not Found')

    def delete_by_user(self, user, image, format='json'):
        image_q = meta.Session.query(Image)
        image = image_q.filter(Image.name==image)\
                       .filter(Image.owner.has(User.user_name==user))\
                       .first()

        if image:
            inline_auth(AnyOf(OwnsImage(image), HasPermission('image_delete')), auth_403)
            if image.raw_uploaded:
                try:
                    image.delete_image_files()
                except Exception, e:
                    abort(500, 'Unable to remove image file from storage')
            meta.Session.delete(image.checksum)
            meta.Session.delete(image.shared)
            meta.Session.delete(image)
            meta.Session.commit()
        else:
            abort(404, '404 Not Found')

    def show_meta(self, image, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.show_meta_by_user(user=user, image=image, format=format)

    def modify_meta(self, image, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.modify_meta_by_user(user=user, image=image, format=format)

    def delete(self, image, format='json'):
        user = request.environ['REPOMAN_USER'].user_name
        return self.delete_by_user(user=user, image=image, format=format)

    def list_all(self, format='json'):
        images = meta.Session.query(Image).all()
        urls = [url('image_by_user', user=i.owner.user_name,
                image=i.name, qualified=True) for i in images]
        if format == 'json':
            response.headers['content-type'] = app_globals.json_content_type
            return h.render_json(urls)
        else:
            abort(501, '501 Not Implemented')

    @authorize(HasPermission('image_create'), auth_403)
    def new(self, format='json'):
        params = validate_new_image(request.params)

        if params['user_name']:
            user_q = meta.Session.query(User)
            user = user_q.filter(User.user_name==params['user_name']).first()
        else:
            user = request.environ['REPOMAN_USER']

        if not user:
                abort(400, '400 Bad Request')

        # check for conflict
        image_q = meta.Session.query(Image).filter(Image.name==params['name'])
        image = image_q.filter(Image.owner.has(User.user_name==user.user_name)).first()
        if image:
            abort(409, '409 Conflict')

        # TODO: setting these values is overly verbose.  make it simple
        new_image = Image()
        # User settable values
        new_image.name = params['name']
        new_image.os_variant = params['os_variant']
        new_image.os_type = params['os_type']
        new_image.os_arch = params['os_arch']
        if params['hypervisor']:
            new_image.hypervisor = params['hypervisor']
        else:
             new_image.hypervisor = 'xen'
        new_image.description = params['description']
        new_image.expires = params['expires']
        new_image.read_only = params['read_only']
        new_image.unauthenticated_access = params['unauthenticated_access']

        # Non-user settable values
        uuid = h.image_uuid()
        current_time = datetime.utcfromtimestamp(time())
        file_name = uuid + '_' + new_image.name

        new_image.owner = user
        new_image.uuid = uuid
        new_image.uploaded = None
        new_image.modified = current_time
        new_image.path = file_name
        new_image.raw_uploaded = False

        meta.Session.add(new_image)
        meta.Session.commit()

        response.headers['content-type'] = app_globals.json_content_type
        response.headers['Location'] = url('get_raw_by_user',
                                           user=user.user_name,
                                           image=new_image.name,
                                           hypervisor='__hypervisor__')
        response.status = ("201 Object created.  upload raw file(s) to 'Location'")
        return h.render_json(beautify.image(new_image))



    def create_grub_symlink(self, imagepath, hypervisor):
        log.debug("Creating grub.conf on %s for hypervisor %s" % (imagepath, hypervisor))
        cmd = ['guestfish', '-a', imagepath, 'launch', ':', 'mount' , '/dev/vda1', '/', ':', 'cp', '/boot/grub/grub.conf-%s' % (hypervisor), '/boot/grub/grub.conf']
        log.debug("grub.conf creation command: %s" % (cmd))
        try:
            p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except OSError, e:
            log.error("Error calling: %s\n%s" % (cmd, e))
            raise e
        stdout = p.communicate()[0]
        log.debug("[%s] output:\n%s" % (cmd, stdout))
        if p.returncode != 0:
            log.error("Multi-hypervisor grub.conf creation command on image %s returned error: %d" % (imagepath, p.returncode))
            raise Exception("Error creating multi-hypervisor grub.conf.")
        else:
            log.debug("Multi-hypervisor grub.conf creation on image %s for hypervisor %s returned successfully." % (imagepath, hypervisor))

    def is_gzip(self, path):
        """
        Test if a file is compressed with gzip or not.
        """
        try:
            log.debug("Checking if %s is a gzip file..." % (path))
            f = gzip.open(path, 'rb')
            b = f.read(1)
            f.close()
            log.debug("%s is a gzip file." % (path))
            return True
        except IOError, e:
            f.close()
        except Exception, e:
            f.close()
            log.error("%s" % (e))
        log.debug("%s is not a gzip file." % (path))
        return False
