import os, sys
import re
import stat
import subprocess
import logging
import fcntl
import tempfile
from repoman_client.logger import log
from repoman_client.exceptions import ImageUtilError


class ImageUtils(object):
    def __init__(self, lockfile, imagepath, mountpoint, system_excludes, user_excludes, size=None, partition=False):
        self.lockfile = lockfile
        self.imagepath = imagepath
        self.mountpoint = mountpoint
        self.system_excludes = system_excludes
        self.user_excludes = user_excludes
        self.imagesize = size
        self.partition = partition
        # The following is used to keep track of where is the device map
        # for partitioned images.  Not used when images are not partitioned.
        self.device_map = None
        
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
                
    #
    # This method is used to recreate a file or directory on the
    # destination if it is present in the origin.
    # If the file or directory does not exist in the origin, then
    # this method does nothing.
    #
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

    def create_bootable_partition(self, path):
        cmd = "sfdisk %s" % (path)
        log.debug("Creating bootable partition on %s" % (path))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        if not p:
            log.error("Error calling: %s" % (cmd))
            raise ImageUtilError("Error creating bootable partition.")
        p.stdin.write(',,L,*\n')
        p.stdin.close()
        p.wait()
        if p.returncode != 0:
            log.error("Command to create bootable partition returned error: %d" % (p.returncode))
            raise ImageUtilError("Error creating bootable partition.")
        log.debug("Bootable partition created on %s" % (path))

    
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
            
    def create_device_map(self, path):
        cmd = "kpartx -av %s" % (path)
        log.debug("Creating device map for %s" % (path))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if not p:
            log.error("Error calling: %s" % (cmd))
            raise ImageUtilError("Error creating device map.")
        stdout = p.communicate()[0]
        log.debug("[%s] output:\n%s" % (cmd, stdout))
        if p.returncode != 0:
            log.error("Device map creation command returned error: %d" % (p.returncode))
            raise ImageUtilError("Error creating device map.")
        # Search the output to extract the location of the new device map
        m = re.match('^add map (\w+) .+$', stdout, flags=re.M)
        if not m:
            log.error("Error extracting location of new device map from:\n%s" % (stdout))
            raise ImageUtilError("Error extracting location of new device map.")
        log.debug("Device map created for %s" % (path))
        return '/dev/mapper/%s' % (m.group(1))

    def delete_device_map(self, path):
        cmd = "kpartx -d %s" % (path)
        log.debug("Deleting device map for %s" % (path))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if not p:
            log.error("Error calling: %s" % (cmd))
            raise ImageUtilError("Error deleting device map.")
        stdout = p.communicate()[0]
        log.debug("[%s] output:\n%s" % (cmd, stdout))
        if p.returncode != 0:
            log.error("Error deleting device map for %s" % (path))
            raise ImageUtilError("Error deleting device map.")
        log.debug("Device map deleted for %s" % (path))

    def install_mbr(self, path):
        cmd = "grub"
        log.debug("Creating MBR on %s" % (path))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        if not p:
            log.error("Error calling: %s" % (cmd))
            raise ImageUtilError("Error creating bootable partition.")
        p.stdin.write('device (hd0) %s\n' % (path))
        p.stdin.write('root (hd0,0)\n')
        p.stdin.write('setup (hd0)\n')
        p.stdin.write('quit\n')
        p.stdin.close()
        p.wait()
        if p.returncode == 0:
            log.debug("MBR created on %s" % (path))
        else:
            log.error("Error creating MBR on %s\nReturn code: %d" % (path, p.returncode))
            raise ImageUtilError("Error creating MBR.")
        
    def mount_image(self):
        if self.check_mounted():
            log.debug('Image Already Mounted')
            return
        if not os.path.exists(self.mountpoint):
            log.debug("Creating mount point")
            os.makedirs(self.mountpoint)
        cmd = None
        if self.partition:
            cmd = "mount %s %s" % (self.device_map, self.mountpoint)
        else:
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
            fields = line.split(' ')
            if self.partition and (fields[0] == self.device_map):
                log.debug("Found image mounted in mtab: '%s'" % line)
                return True
            elif self.imagepath in line or (fields[1] == self.mountpoint):
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
        if self.partition:
            self.create_bootable_partition(imagepath)
            self.device_map = self.create_device_map(imagepath)
            self.mkfs(self.device_map, label='root')
        else:
            self.mkfs(imagepath)
    
    def sync_fs(self, verbose):
        #TODO: add progress bar into rsync somehow
        log.info("Starting Sync Process")

        exclude_list = ""
        if self.system_excludes != None and len(self.system_excludes) > 0:
            for exclude_item in self.system_excludes:
                exclude_list += '--exclude "%s" ' % (exclude_item)
        if self.user_excludes != None and len(self.user_excludes) > 0:
            for exclude_item in self.user_excludes:
                exclude_list += '--exclude "%s" ' % (exclude_item)
        # Let's not forget to add the --delete-exclude flag to rsync else
        # previously synced files which now match an exclude rule will not get
        # deleted and will stay in the synced image.
        if len(exclude_list) > 0:
            exclude_list += " --delete-excluded"

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
        snapshot_success = False
        try:
            self._snapshot_system(start_fresh, verbose, clean)
            snapshot_success = True
        finally:
            log.debug("Releasing lock")
            self.destroy_lock()
            log.info("Unmounting Image")
            self.umount_image()
            if self.partition and self.device_map != None:
                log.debug("Deleting %s device map for image %s" % (self.device_map, self.imagepath))
                self.delete_device_map(self.imagepath)
        if self.partition and snapshot_success:
                self.install_mbr(self.imagepath)
        
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
            log.debug("Image stats:\n%s" % (image_stats))
            if self.imagesize:
                # requested size does not match current size
                if self.imagesize != image_stats['size']:
                    log.warning("Requested size (%d) does not match current file (%d).  Starting from scratch." % (self.imagesize, image_stats['size']))
                    start_fresh = True
            else:
                # image size does not match partition size
                if image_stats['size'] != self.statvfs()['size']:
                    log.warning("Root partition size does not match image size.  Starting from scratch")
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
