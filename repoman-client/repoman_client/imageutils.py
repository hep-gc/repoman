'''
Created on Oct 4, 2010

@author: fransham
'''

from os import makedirs,path,mkdir
import os
from commands import getstatusoutput
from subprocess import Popen, PIPE
import sys

class ImageUtils(object):

    def __init__(self, lockfile, snapshot, mountpoint, exclude_dirs):
        self.lockfile = lockfile
        self.snapshot = snapshot
        self.mountpoint = mountpoint
        self.exclude_dirs = exclude_dirs

    def create_snapshot(self):
        if not self.check_mounted(self.snapshot, self.mountpoint):
            print "Creating new Image"
            os.system("rm -rf %s %s" % (self.snapshot, self.mountpoint))
            self.create_local_bundle()
        elif self.sync_is_running():
            print "Sync is already running...what?"
            self.create_local_bundle()
        else:
            print "Syncing image."
            self.sync_filesystem(self.mountpoint, self.exclude_dirs)
        print "Snapshot process complete."

    def sync_is_running(self):
        if os.path.exists(self.lockfile):
            return True
        return False

    def create_local_bundle(self):
        if self.sync_is_running():
            pid=open(self.lockfile,'r').read()
            print "The local image creation is already in progress."
            print "If you're sure this is an error, cancel this script and delete: %s " % self.lockfile
            sys.exit(1)
            #os.system("renice -19 "+pid);
            #os.waitpid(int(pid),0)
            #print "Local image copy created"
        else:
            pid = os.getpid()
            lf = open(self.lockfile,'w')
            lf.write(str(pid))
            lf.close()
            try:
                self.create_image(self.snapshot)
                self.label_image(self.snapshot)
                self.mount_image(self.snapshot, self.mountpoint)
                self.sync_filesystem(self.mountpoint, self.exclude_dirs)
                os.remove(self.lockfile)
            except MountError,e:
                print e.msg
                os.remove(self.lockfile)
                sys.exit(1)

    def create_image(self, imagepath):

        dir = path.dirname(imagepath)
        if not path.exists(dir):
            makedirs(dir)
        ret1, fs_size = getstatusoutput("df /")
        ret2, fs_bytes_used = getstatusoutput("df /")
        ret3, image_dirsize = getstatusoutput("df "+dir)

        if (ret1 or ret2 or ret3):
            raise MountError("df ", "error getting filesystem sizes: \n"+ret1+ret2+ret3)

        fs_size=fs_size.split()[8]
        fs_bytes_used=fs_bytes_used.split()[9]
        image_dirsize = image_dirsize.split()[10]

        if(int(image_dirsize) < int(fs_bytes_used)):
            raise MountError("df ", "ERROR: Not enough space on filesystem. \n" +
                             "Check the path to your image ("+imagepath+") "+
                             "in ~/.repoman-client and retry")
        if(int(image_dirsize) < int(fs_size)):
            print ("WARNING: the directory you have specified for your image copy"+
                   "is smaller in size than the root directory.  Your new image"+
                   "will have less free space.")
            fs_size = fs_bytes_used

        print "creating image "+imagepath
        ret4, dd = getstatusoutput("dd if=/dev/zero of="+imagepath+" count=0 bs=1k seek="+str(fs_size))
        if ret4:
            raise MountError("dd", "ERROR: problem creating image "+imagepath+": "+dd)

        print "creating ext3 filesystem on "+imagepath
        ret5, mkfs = getstatusoutput("/sbin/mkfs -t ext3 -F "+imagepath)
        if ret5:
            raise MountError("mkfs.ext3: ", "ERROR: problem with mkfs: "+mkfs)
            
    def label_image(self, imagepath, label='/'):
    	print "Labeling image as: '%s'" % label
        ret, tune2fs = getstatusoutput("/sbin/tune2fs -L %s %s" % (label, imagepath))
    	if ret:
    		raise MountError("tune2fs: ", "ERROR: problem with tune2fs: "+tune2fs)

    def mount_image(self, imagepath, mountpoint):
        if not path.exists(mountpoint):
            makedirs(mountpoint)
        print "mounting image "+imagepath+" on "+mountpoint
        ret, mnt = getstatusoutput("mount -o loop "+imagepath+" "+mountpoint)
        if ret:
            raise MountError("mount -o loop", "ERROR: Mounting of image failed: "+mnt)

    def check_mounted(self, imagepath, mountpoint):
        for line in open("/etc/mtab"):
            if imagepath in line:
                return True
        return False

    def sync_filesystem(self, mountpoint, excl_dirs):
        create_dirs = ['/dev', '/mnt', '/proc', '/sys', '/tmp', '/root', '/root/.ssh']
        for i in create_dirs:
            if not path.exists(mountpoint+i):
            	if i == '/root/.ssh':
            		mkdir(mountpoint+i, 0700)
            	else:
                	mkdir(mountpoint+i)
        excludes = str.rsplit(excl_dirs)
        cmd = "rsync -ax --delete"
        for excl in excludes:
            cmd += " --exclude "+excl
        cmd += " / "+mountpoint
        print "creating local copy of filesystem... this could take some time.  Please be patient."
        p = Popen(cmd, shell=True, stdout=PIPE)
        ret = p.wait()
        if ret:
            raise MountError("rsync ", p.stdout.read())
        #ret, sync = getstatusoutput(cmd)
        #if ret:
        #    raise MountError("rsync ","ERROR: rsync returned errors: "+ sync)
        #print "local copy of VM created."



class MountError(Exception):
    """Exception raised when the system cannot mount the specified file.

    Attributes:
    expr -- input expression in which the error occurred
    msg -- system error from mount command
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

