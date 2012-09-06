import sys, os, time, errno, re
from repoman_client.logger import log
from repoman_client.config import config
from repoman_client import imageutils
from repoman_client.exceptions import RepomanError, FormattingError, ProxyExpiredError, ProxyNotFoundError
import pprint
if sys.version_info < (2, 6):
    try:
        import simplejson as json
    except:
        raise "Please install the simplejson lib for python 2.4 or 2.5"
else:
    import json

import httplib
import urllib
import socket
import subprocess

# Note: the following module is not available in python 2.4
#import ssl


HEADERS = {"Content-type":"application/x-www-form-urlencoded", "Accept": "*"}




class RepomanResponse(object):
    def __init__(self, code, data=None):
        self.data = data
        self.code = code


class RepomanClient(object):
    def __init__(self, host, port, proxy):
        self.HOST = host
        self.PORT = port
        self.PROXY = proxy
        self._conn = httplib.HTTPSConnection(host, port, cert_file=proxy, key_file=proxy)
        log.debug('Created Httpsconnection with... HOST:%s PORT:%s PROXY:%s' % 
                  (self.HOST, self.PORT, self.PROXY))

    def _request(self, method, url, kwargs={}, headers=HEADERS):
        log.debug("%s %s" % (method, url))
        log.debug("kwargs: %s" % kwargs)
        log.debug("headers: %s" % headers)
        try:
            if method == 'GET':
                self._conn.request(method, url)
            elif method == 'DELETE':
                self._conn.request(method, url)
            elif method == 'POST':
                params = urllib.urlencode(kwargs)
                self._conn.request(method, url, params, headers)
            resp =  self._conn.getresponse()
            log.debug("Server response code: %s" % resp.status)
            return self._check_response(resp)
        except RepomanError, e:
            raise(e)
        except httplib.InvalidURL, e:
            log.error("%s" % e)
            raise RepomanError("Invalid port number")
        except httplib.HTTPException, e:
            log.error("%s" % e)
            print 'httpexception'
        except socket.gaierror, e:
            log.error("%s", e)
            raise RepomanError('Unable to connect to server.  Check Host and port \n\t\t %s' % e)
#        except socket.error, e:
#            raise RepomanError('Unable to connect to server.  Is the server running?\n\t%s' % e)
#        except ssl.SSLError, e:
#            pass
        except Exception, e:
            log.error("%s", e)
            if str(e).find('SSL_CTX_use_PrivateKey_file') and not os.path.exists(self.PROXY):
                raise ProxyNotFoundError('Certificate proxy not found: %s\nPlease create a certificate proxy and try again.' % (self.PROXY))
            elif str(e).find('certificate expired') != -1:
                raise ProxyExpiredError('Your certificate proxy has expired.\nPlease generate a new one and try again.')
            else:
                raise RepomanError("Unknown error has occurred. \n\t\t %s" % e)


    def _check_response(self, resp):
        if resp.status in [httplib.OK, httplib.CREATED]:
            return resp
        elif resp.status == httplib.BAD_REQUEST:
            # 400
            message = resp.read()
            # parse body for reason and display to user.
        elif resp.status == httplib.FORBIDDEN:
            # 403
            message = "You lack the rights to access that object"
        elif resp.status == httplib.NOT_FOUND:
            # 404
            message = "Requested resource could not be found"
        elif resp.status == httplib.REQUEST_TIMEOUT:
            # 408
            message = "Request has timed out.  Please retry or seek assistance."
        elif resp.status == httplib.CONFLICT:
            # 409
            message = "Conflict in request"
            # parse body for reason and display to user.
        elif resp.status == httplib.INTERNAL_SERVER_ERROR:
            # 500
            message = ("The server has encountered an error and was unable to "
                       "process your request.  If problem persists, seek assistance.")
        elif resp.status == httplib.NOT_IMPLEMENTED:
            # 501
            message = ("The requested functionality has yet to be implemented by the server")
        else:
            # Generic error message
            message = ("Response from server cannot be handled by this client.\n\n"
                       "status: %s\nreason: %s\n"
                       "-------- body ---------\n"
                       "%s\n-----------------------\n"
                       ) % (resp.status, resp.reason, resp.read())
        log.error(message)
        raise RepomanError(message, resp)

    def _get(self, url):
        return self._request('GET', url)

    def _post(self, url, kwargs={}):
        return self._request('POST', url, kwargs)

    def _delete(self, url):
        return self._request('DELETE', url)

    def _json(self, resp):
        body = resp.read()
        log.debug("Message body from server: '%s'" % body)
        try:
            return json.loads(body)
        except:
            message = "Unable to parse response."
            raise FormattingError(message, body)

    def _parse_response(self, resp):
        content_type = resp.getheader('content-type')
        if 'json' in content_type:
            return self._json(resp)
        else:
            raise FormattingError("Unable to parse the response body.  Unknown content_type: '%s'" % content_type)

    def whoami(self):
        resp = self._get('/api/whoami')
        return self._parse_response(resp)

    def list_users(self, group=None):
        if group is None:
            # List all users
            resp = self._get('/api/users')
        else:
            # List users who are members of `group`
            resp = self._get('/api/groups/%s/users' % group)
        return self._parse_response(resp)

    def list_groups(self, user=None, list_all=False):
        if list_all:
            resp = self._get('/api/groups')
        elif user is None:
            # List my group membership
            resp = self.whoami()
            return resp.get('groups')
        else:
            # list the group membership of `user`
            resp = self._get('/api/users/%s/groups' % user)
        return self._parse_response(resp)

    def list_all_images(self):
        resp = self._get('/api/images')
        return self._parse_response(resp)

    def list_current_user_images(self):
        resp = self.whoami()
        return resp.get('images')

    def list_user_images(self, user):
        resp = self._get('/api/users/%s/images' % user)
        return self._parse_response(resp)

    def list_images_shared_with_group(self, group):
        resp = self._get('/api/groups/%s/shared' % group)
        return self._parse_response(resp)

    def list_images_shared_with_user(self, user=None):
        if user:
            resp = self._get('/api/users/%s/shared' % user)
            return self._parse_response(resp)
        else:
            # Two calls, grrr...
            user = self.whoami().get('user_name')
            resp = self._get('/api/users/%s/shared' % user)
            return self._parse_response(resp)

    def describe_user(self, user):
        resp = self._get('/api/users/%s' % user)
        return self._parse_response(resp)

    def describe_image(self, image, owner = None):
        if owner:
            resp = self._get('/api/images/%s/%s' % (owner, image))
        else:
            resp = self._get('/api/images/%s' % image)
        return self._parse_response(resp)

    def describe_group(self, group):
        resp = self._get('/api/groups/%s' % group)
        return self._parse_response(resp)

    def create_user(self, **kwargs):
        resp = self._post('/api/users', kwargs)
        return True

    def create_group(self, **kwargs):
        resp = self._post('/api/groups', kwargs)
        return True

    def create_image_metadata(self, **kwargs):
        resp = self._post('/api/images', kwargs)
        return self._parse_response(resp)

    def remove_user(self, user):
        resp = self._delete('/api/users/%s' % user)
        return True

    def remove_group(self, group):
        resp = self._delete('/api/groups/%s' % group)
        return True

    def remove_image(self, image):
        resp = self._delete('/api/images/%s' % image)
        return True

    def modify_user(self, user, **kwargs):
        resp = self._post('/api/users/%s' % user, kwargs)
        return True

    def modify_image(self, image, **kwargs):
        resp = self._post('/api/images/%s' % image, kwargs)
        return True

    def modify_group(self, group, **kwargs):
        resp = self._post('/api/groups/%s' % group, kwargs)
        return True

    def add_user_to_group(self, user, group):
        resp = self._post('/api/groups/%s/users/%s' % (group, user))
        return True

    def remove_user_from_group(self, user, group):
        resp = self._delete('/api/groups/%s/users/%s' % (group, user))
        return True

    def add_permission(self, group, permission):
        resp = self._post('/api/groups/%s/permissions/%s' % (group, permission))
        return True

    def remove_permission(self, group, permission):
        resp = self._delete('/api/groups/%s/permissions/%s' % (group, permission))
        return True

    def share_with_user(self, image, user):
        resp = self._post('/api/images/%s/share/user/%s' % (image, user))
        return True

    def unshare_with_user(self, image, user):
        resp = self._delete('/api/images/%s/share/user/%s' % (image, user))
        return True

    def share_with_group(self, image, group):
        resp = self._post('/api/images/%s/share/group/%s' % (image, group))
        return True

    def unshare_with_group(self, image, group):
        resp = self._delete('/api/images/%s/share/group/%s' % (image, group))
        return True

    def uploaded_image_exist(self, image, owner, hypervisor='xen'):
        """
        This method will test if an image has an uploaded file for a given hypervisor.
        """
        log.info("Checking to see if image %s, owner %s, has an uploaded file for hypervisor %s" % (image, owner, hypervisor))
        if owner:
            resp = self._get('/api/images/%s/%s' % (owner, image))
        else:
            resp = self._get('/api/images/%s' % (image))
        if resp.status != 200:
            log.info("Image slot does not yet exist.")
            raise RepomanError('Image does not yet exist.', resp)

        if owner:
            url = 'https://' + config.host + '/api/images/raw/%s/%s/%s' % (owner, hypervisor, image)
        else:
            url = 'https://' + config.host + '/api/images/raw/%s/%s' % (hypervisor, image)
        try:
            cmd = ['curl',
                    '--cert', config.proxy,
                    '--insecure',
                    '--head',
                    url]
            log.debug(" ".join(cmd))
            p = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=config.get_restricted_env())
            if not p:
                log.error("Error calling: %s" % (cmd))
                raise RepomanError("Error checking if image %s, owner %s, has an uploaded file for hypervisor %s" % (image, owner, hypervisor))
            log.info("Command complete")
            stdout = p.communicate()[0]
            log.debug(stdout)
            m = re.search('^HTTP/.+200 OK', stdout, flags=re.M)
            if m:
                log.info("Uploaded file exist for image %s, owner %s, hypervisor %s." % (image, owner, hypervisor))
                return True
            else:
                log.info("Uploaded file does not exist for image %s, owner %s, hypervisor %s." % (image, owner, hypervisor))
                return False
        except Exception, e:
            log.error("%s" % e)
            raise RepomanError(str(e))
           

    def upload_image(self, image, owner, image_file, gzip=False, hypervisor='xen'):
        log.info("Checking to see if image slot exists on repository")
        if owner:
            resp = self._get('/api/images/%s/%s' % (owner, image))
        else:
            resp = self._get('/api/images/%s' % (image))

        if resp.status != 200:
            log.info("Image slot does not yet exist.")
            raise RepomanError('Image does not yet exist.  Create an image before uploading to it', resp)

        # Check if the source is a directory.  If it is, then raise an
        # exception.
        if os.path.isdir(image_file):
            raise RepomanError('Specified source is a directory: %s\nSource must be a file.' % (image_file))
           
        # Check if the source file exists.
        if not os.path.exists(image_file):
            raise RepomanError('Specified source not found: %s' % (image_file))
            
        if owner:
            url = 'https://' + config.host + '/api/images/raw/%s/%s/%s' % (owner, hypervisor, image)
        else:
            url = 'https://' + config.host + '/api/images/raw/%s/%s' % (hypervisor, image)

        try:
            if gzip:
                log.info("Performing gzip on image prior to upload")
                print "Gzipping image before upload"
                gzip_image = os.path.join(os.path.dirname(image_file), image)
                gzip = subprocess.Popen("gzip --stdout %s > %s" % (image_file, gzip_image),
                                        shell=True, env=config.get_restricted_env())
                gzip.wait()
                image_file = gzip_image
                log.info('Gzip complete')

            args = ['curl',
                    '--cert', config.proxy,
                    '--insecure',
                    '-T', image_file, url]
            cmd = " ".join(args)
            log.info("Running command: '%s'" % cmd)
            curl = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=config.get_restricted_env())
            for line in curl.stdout.readlines():
                print line
            log.info("Command complete")
            # Cleanup gzip file if needed.
            if gzip:
                try:
                    log.info("Cleaning up %s" % (image_file))
                    os.remove(image_file)
                except Exception, e:
                    pass
 
        except Exception, e:
            log.error("%s" % e)
            raise RepomanError(str(e))

    def download_image(self, image, dest=None):
        if not dest:
            dest = './%s' % image

        # Check to see if requested image existing in the repo.
        # This will raise an exception if it does not.
        log.info("Checking to see if image slot exists on repository before download")
        resp = self._get('/api/images/%s' % image)

        # Check to make sure destination is not an existing directory.
        if os.path.isdir(dest):
            raise RepomanError('Cannot create %s.  Specified destination already exist and is a directory.' % (dest))

        # If the destination already exists, make sure we can overwrite it.
        if os.path.isfile(dest):
            try:
                fp = open(dest, 'w')
            except IOError, e:
                if e.errno == errno.EACCES:
                    raise RepomanError('Cannot overwrite %s.  Specified destination already exist and you don\'t have permissions to write to it.' % (dest))
            
        url = 'https://' + config.host + '/api/images/raw/%s' % image
        log.info("Downloading image From:'%s' To:'%s'" % (url, dest))
        try:
            args = ['curl',
                    '--cert', config.proxy,
                    '--insecure',
                    url, '>', dest]
            cmd = " ".join(args)
            log.info("Running Command: '%s'" % cmd)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, env=config.get_restricted_env())
            for line in p.stdout.readlines():
                print line
            log.info("Command complete")
        except Exception, e:
            log.error("%s" % e)
            print e

