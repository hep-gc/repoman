from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship, backref

from repoman.model.meta import Base
from repoman.model.associations import imageshare_user_association
from repoman.model.associations import imageshare_group_association
from repoman.model.checksum import Checksum
from pylons import app_globals
import os
import logging
import shutil

log = logging.getLogger(__name__)

class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True)      # ID unique to the database
    uuid = Column(String(64), unique=True)      # 32-char representation

    uploaded = Column(DateTime())               # use GMT
    modified = Column(DateTime())               # use GMT
    expires = Column(DateTime())                # use GMT
    version = Column(Integer, default=0)        # incrimented on new upload
    size = Column(Integer)                      # bytes

    name = Column(String(256))                  # name of image
    description = Column(String(256))           # Human description

    os_variant = Column(String(100))            # sl55, debian, etc
    os_type = Column(String(100))               # linux, windows, unix, etc.
    os_arch = Column(String(100))               # x86, x86_64
    hypervisor = Column(String(100))            # xen, kvm, etc.  (for multi-hypervisor images, multiple hypervisors can be specified by separating them with a comma.)

    path = Column(String(256), default='')      # path to file (';' seperated for multi-hypervisor images)

    # flags
    deleted = Column(Boolean(), default=False)          # image deleted?
    read_only = Column(Boolean(), default=False)        # protect from overwrite
    raw_uploaded = Column(Boolean(), default=False)     # has it been uploaded?
    unauthenticated_access = Column(Boolean(), default=False)   # gettable from http?

    # Adjacency list relationship
    # track what images were based on what images
    #  parent_image - the image this image is based from
    #  child_images - list of images based off this image
    parent_image_id = Column(Integer, ForeignKey('image.id'))
    child_images = relationship("Image", backref=backref("parent_image", remote_side=id))

    # checksum ref
    checksum_id = Column(Integer, ForeignKey('checksum.id'))
    checksum = relationship("Checksum", backref=backref("image", uselist=False))

    # owner ref
    owner_id = Column(Integer, ForeignKey('user.id'))
    #owner = relationship("User", backref=backref('image', uselist=False))

    # sharing ref
    shared_id = Column(Integer, ForeignKey('image_share.id'))
    shared = relationship("ImageShare", backref=backref("image", uselist=False))

    def __repr__(self):
        return "<Image('%s', '%s')>" % (self.name, self.owner.user_name)

    def __init__(self):
        self.checksum = Checksum()
        self.shared = ImageShare()

    def delete_image_files(self):
        paths = self.get_image_paths_by_hypervisor()
        for hypervisor in paths:
            self.delete_image_file_for_hypervisor(hypervisor)

    def delete_image_file_for_hypervisor(self, hypervisor):
        try:
            path = os.path.join(app_globals.image_storage, 
                                '%s_%s_%s' % (self.owner.user_name, self.name, hypervisor))
            os.remove(path)
            log.debug("Image file %s deleted." % (path))
        except Exception, e:
            log.error("Error deleting image file for %s, hypervisor %s\n%s" % (self.name, hypervisor, e))
        
    def get_image_paths_by_hypervisor(self):
        paths = {}
        hypervisors = []
        if self.hypervisor == None:
            hypervisors = ['xen']
        else:
            hypervisors = self.hypervisor.split(',')
        for hypervisor in hypervisors:
            path = os.path.join(app_globals.image_storage, 
                                '%s_%s_%s' % (self.owner.user_name, self.name, hypervisor))
            paths[hypervisor] = path
        return paths

    def change_image_files_to_new_owner(self, new_owner):
        """
        This method will change the image's filename to a new owner.
        The image filename has the owner hardcoded in them, hence why we
        need to change the filenames when we assign the image to another
        owner.
        Note that thie method will only change the owner if it does not conflict
        with any existing image already owned by the target user.
        """
        new_paths = []
        hypervisors = []

        if self.hypervisor == None:
            hypervisors = ['xen']
        else:
            hypervisors = self.hypervisor.split(',')

        # Let's do a dry run first to make sure we are not overwriting any existing
        # image.
        log.debug("Checking to make sure image ownership change will not overwrite any existing image files.")
        for hypervisor in hypervisors:
            path = os.path.join(app_globals.image_storage, 
                                '%s_%s_%s' % (self.owner.user_name, self.name, hypervisor))
            new_path = os.path.join(app_globals.image_storage, 
                                '%s_%s_%s' % (new_owner.user_name, self.name, hypervisor))
            if os.path.exists(new_path):
                # Abort operation.
                log.warn("Image ownership change aborted because of image collision: %s" % (new_path))
                return False

        log.debug("No conflict detected; proceeding with image ownership change.")

        for hypervisor in hypervisors:
            path = os.path.join(app_globals.image_storage, 
                                '%s_%s_%s' % (self.owner.user_name, self.name, hypervisor))
            new_path = os.path.join(app_globals.image_storage, 
                                '%s_%s_%s' % (new_owner.user_name, self.name, hypervisor))
            if os.path.exists(path):
                log.debug("Moving %s to %s" % (path, new_path))
                shutil.move(path, new_path)
                new_paths.append(new_path)

        # Finally, let's change the image owner and path metadata.
        log.debug("Changing image's owner metadata variable to the new owner.")
        self.owner = new_owner
        log.debug("Updating image's path metadata variable to point to new image paths after ownership change.")
        self.path = ';'.join(new_paths)

        return True




class ImageShare(Base):
    __tablename__ = "image_share"

    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean, default=True)

    # One-to-many relationship (ImageShare<->User(s))
    users = relationship("User", secondary='imageshare_user_association',
                         backref='shared_images')

    # One-to-many relationship (ImageShare<->Groups(s))
    groups = relationship("Group", secondary='imageshare_group_association',
                          backref='shared_images')

