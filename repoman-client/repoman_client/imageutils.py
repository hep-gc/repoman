import os, sys
import stat
import subprocess
import logging
import fcntl
import tempfile

log = logging.getLogger('ImageUtils')

class ImageUtilError(Exception):
    pass


class ImageUtils(object):
    def __init__(self, lockfile, imagepath, mountpoint, excludes, size=None):
        self.lockfile = lockfile
        self.imagepath = imagepath
        self.mountpoint = mountpoint
        self.excludes = excludes
        self.imagesize = size
        
    def statvfs(self, path='/'):
        stats = os.statvfs(path)
        return {'size':stats.f_bsize*stats.f_blocks,
                'free':stats.f_bsize*stats.f_bfree,
                'used':stats.f_bsize*(stats.f_blocks-stats.f_bfree)}
    
    def stat(self, path):
        stats = os.lstat(path)
        return {'uid':stats.st_uid,
                'gid':stats.st_gid,
                'mode':stats.st_mode,
                'size':stats.st_size}
                
    def recreate(self, origin, dest_root):
        if not os.path.exists(origin):
            return
        stats = self.stat(origin)
        dest = os.path.join(dest_root, origin.lstrip('/'))
        if os.path.exists(dest):
            self.destroy_files(dest)
        if os.path.isdir(origin):
            os.mkdir(dest)
        elif os.path.isfile(origin):
            open(dest).close()
        os.chmod(dest, stats['mode'])
        os.chown(dest, stats['uid'], stats['gid'])
        log.debug("Recreated '%s' at '%s' (uid:%s,gid:%s,mode:%s)" 
                 % (origin, dest, stats['uid'], stats['gid'], stats['mode']))
        
    def get_volume_name(self, path='/'):
    	#TODO: fixme
        return '/'
        
    def label_image(self, path, label='/'):
        cmd = "/sbin/tune2fs -L %s %s" % (label, path)
        log.debug("Labeling image: '%s'" % cmd)
        if subprocess.Popen(cmd, shell=True).wait():
            log.error("Unable to label image")
            raise ImageUtilError("Unable to label Image")
        
    def dd_sparse(self, path, size_bytes):
        cmd = ("dd if=/dev/zero of=%s count=0 bs=1 seek=%s" 
               % (path, size_bytes))
        log.debug("Creating sparse file: '%s'" % cmd)
        null_f = open('/dev/null', 'w')
        if subprocess.Popen(cmd, shell=True, stdout=null_f, stderr=null_f).wait():
            log.error("Unable to create sparse file")
            raise ImageUtilError("Error creating sparse file")
        null_f.close()
    
    def detect_fs_type(self, path):
        #TODO: fixme
        return 'ext3'
    
    def mkfs(self, path, fs_type='ext3', label='/'):
        cmd = "/sbin/mkfs -t %s -F -L %s %s" % (fs_type, label, path)
        log.debug("Creating file system: '%s'" % cmd)
        null_f = open('/dev/null', 'w')
        if subprocess.Popen(cmd, shell=True, stdout=null_f, stderr=null_f).wait():
            log.error("Unable to create filesystem")
            raise ImageUtilError("Error creating filesystem.")
        null_f.close()
            
    def mount_image(self):
        if self.check_mounted():
            log.debug('Image Already Mounted')
            return
        if not os.path.exists(self.mountpoint):
            log.debug("Creating mount point")
            os.makedirs(self.mountpoint)
        cmd = "mount -o loop %s %s" % (self.imagepath, self.mountpoint)
        if subprocess.Popen(cmd, shell=True).wait():
            raise ImageUtilError("Unable to Mount image")
        log.debug("Image mounted: '%s'" % cmd)
        
            
    def umount_image(self):
        if not self.check_mounted():
            log.debug('Image already unmounted')
            return
        cmd = "umount %s" % self.mountpoint
        if subprocess.Popen(cmd, shell=True).wait():
            raise ImageUtilError("Unable to unmount image")
        log.debug("Image unmounted: '%s'" % cmd)

    def check_mounted(self):
        for line in open("/etc/mtab"):
            if self.imagepath in line or self.mountpoint in line:
                log.debug("Found image mounted in mtab: '%s'" % line)
                return True
        return False
        
    def obtain_lock(self):
        fd = open(self.lockfile, 'w')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.lock = fd
            return True
        except IOError:
            return False
        
    def destroy_lock(self):
        if self.lock:
            self.lock.close()
            self.lock = None

    def destroy_files(self, *args):
        items = " ".join(args)
        cmd = "rm -rf %s" % items
        subprocess.call(cmd, shell=True)
        log.debug("Destroyed files: '%s'" % cmd)

    def image_exists(self):
        if os.path.exists(self.imagepath):
            return True

    def create_image(self, imagepath, size=None):
        base_dir = os.path.dirname(imagepath)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            log.debug("Created image base dir: '%s'" % imagepath)
        
        root_stats = self.statvfs()
        snapshot_stats = self.statvfs(base_dir)
        
        # See if there is enough free space to create a snapshot (>50% free)
        if root_stats['used'] > snapshot_stats['free']:
            log.error("Not enought free space. (used:%s free:%s)" % 
                      (root_stats['used'], snapshot_stats['free']))
            raise ImageUtilError("ERROR.  not enough free space")    
        
        # If specified, see if the requested size is enough
        if size:
            if size < root_stats['used']:
                log.error("Specified Image size less then required")
                log.error("Required:%s  Requested:%s" % (root_stats['used'], size))
                raise ImageUtilError("Specified partition size is less then needed.")
        else:
            size = root_stats['size']            

        self.dd_sparse(imagepath, size)
        self.mkfs(imagepath)
    
    def sync_fs(self, verbose):
        #TODO: add progress bar into rsync somehow
        log.info("Starting Sync Process")
        exclude_list =  "--exclude " + " --exclude ".join(self.excludes)
        flags = ''
        if verbose:
            flags += '--stats --progress ' 
        cmd = "rsync -a --sparse %s --delete %s / %s" % (flags, exclude_list, self.mountpoint)
        log.debug("%s" % cmd)
        p = subprocess.Popen(cmd, shell=True).wait()
        if p:
            log.error("Rsync encountered an issue. return code: '%s'" % p)
            raise ImageUtilError("Rsync failed.  Aborting.")
        log.info("Sync Complete")
        
        # Recread all excluded files with correct permissions
        for item in self.excludes:
            self.recreate(item, self.mountpoint)
        
    def snapshot_system(self, start_fresh=False, verbose=False, clean=False):
        if verbose:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter("%(levelname)s - %(message)s")
            ch.setFormatter(formatter)
            log.addHandler(ch)

        log.debug("Obtaining lock")
        if not self.obtain_lock():
            log.error("Unable to obtain lock")
            raise ImageUtilError("Unable to obtain lock")
        try:
            self._snapshot_system(start_fresh, verbose, clean)
        finally:
            log.debug("Releasing lock")
            self.destroy_lock()
            log.info("Unmounting Image")
            self.umount_image()
        
    def _snapshot_system(self, start_fresh=False, verbose=False, clean=False):
        exists = self.image_exists()
        if clean:
            log.info("Cleaning existing snapshot first.")
            start_fresh=True
        elif not exists:
            log.info("No existing image found, creating a new one")
            start_fresh=True
        elif exists:
            log.info("Existing image found, attempting to use.")
            image_stats = self.stat(self.imagepath)
            if self.imagesize:
                # requested size does not match current size
                if self.imagesize != image_stats['size']:
                    log.warning("Requested size does not match current file.  Starting from scratch.")
                    start_fresh = True
            else:
                # image size does not match partition size
                log.warning("Root partition size does not match image size.  Starting from scratch")
                if image_stats['size'] != self.statvfs()['size']:
                    start_fresh = True

        if start_fresh:
            # makesure image is unmounted, then destroy and recreate image.
            log.info("Unmounting Image")
            self.umount_image()
            log.info("Destroying old files")
            self.destroy_files(self.imagepath, self.mountpoint)
            log.info("Creating new image")
            self.create_image(self.imagepath, self.imagesize)
        
        log.info("Mounting image")
        self.mount_image()
        log.info("Syncing file system")
        self.sync_fs(verbose)
