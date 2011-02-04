from repoman_client.config import config
from repoman_client import imageutils
import simplejson
import httplib
import urllib
import socket
import subprocess
#import ssl
import sys


HEADERS = {"Content-type":"application/x-www-form-urlencoded", "Accept": "*"}


class RepomanError(Exception):
    def __init__(self, message, resp):
        self.resp = resp            # Origonal response
        self.message = message      # User friendly message
        self.exit = True            # Should the client abort on this error?
        self.status = None
        if resp:
            try:
                self.status = resp.status
            except:
                pass

    def __str__(self):
        return self.message

    def __repr__(self):
        return str(self)


class FormattingError(RepomanError):
    def __init__(self, message, body=None, format='json', resp=None):
        self.format = format
        self.body = body
        self.resp = resp
        self.message = message
        self.status = None
        if resp:
            try:
                self.status = resp.status
            except:
                pass

    def __str__(self):
        return self.message

    def __repr__(self):
        return str(self)


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

    def _request(self, method, url, kwargs={}, headers=HEADERS):
        try:
            if method == 'GET':
                self._conn.request(method, url)
            elif method == 'DELETE':
                self._conn.request(method, url)
            elif method == 'POST':
                params = urllib.urlencode(kwargs)
                self._conn.request(method, url, params, headers)
            resp =  self._conn.getresponse()
            return self._check_response(resp)
        except httplib.InvalidURL:
            print "Invlaid port number"
            sys.exit(1)
        except httplib.HTTPException:
            print 'httpexception'
        except socket.gaierror, e:
            print 'Unable to connect to server.  Check Host and port'
            sys.exit(1)
#        except socket.error, e:
#            print 'Unable to connect to server.  Is the server running?\n\t%s' % e
#            sys.exit(1)
#        except ssl.SSLError, e:
#            print "An error has occured within open ssl."
#            print str(e)
#            sys.exit(1)
        except Exception, e:
            raise e


    def _check_response(self, resp):
        if resp.status in [httplib.OK, httplib.CREATED]:
            return resp
        elif resp.status == httplib.BAD_REQUEST:
            # 400
            message = "Invalid request."
            # parse body for reason and display to user.
        elif resp.status == httplib.FORBIDDEN:
            # 403
            message = "You lack the rights to access that object"
        elif resp.status == httplib.NOT_FOUND:
            # 404
            message = "Requested resource could not be found"
        elif resp.status == httplib.REQUEST_TIMEOUT:
            # 408
            message = "Request has timed out.  Please retry or seek asistance."
        elif resp.status == httplib.CONFLICT:
            # 409
            message = "Conflict in request"
            # parse body for reason and display to user.
        elif resp.status == httplib.INTERNAL_SERVER_ERROR:
            # 500
            message = ("The server has encountered an error and was unable to "
                       "process your request.  If problem persists, seek asistance.")
        elif resp.status == httplib.NOT_IMPLEMENTED:
            # 501
            message = ("The requested functionality has yet to be implimented by the server")
        else:
            # Generic error message
            message = ("Response from server cannot be handled by this client.\n\n"
                       "status: %s\nreason: %s\n"
                       "-------- body ---------\n"
                       "%s\n-----------------------\n"
                       ) % (resp.status, resp.reason, resp.read())
        raise RepomanError(message, resp)

    def _get(self, url):
        return self._request('GET', url)

    def _post(self, url, kwargs={}):
        return self._request('POST', url, kwargs)

    def _delete(self, url):
        return self._request('DELETE', url)

    def _json(self, resp):
        body = resp.read()
        try:
            return simplejson.loads(body)
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

    def describe_image(self, image):
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

    def upload_image(self, image, image_file):
        resp = self._get('/api/images/%s' % image)
        if resp.status != 200:
            raise RepomanError('Image does not yet exist.  Create an image before uploading to it', resp)

        url = 'https://' + config.host + '/api/images/raw/%s' % image
        try:
            args = ['curl',
                    '--cert', config.proxy,
                    '--insecure',
                    '-T', image_file, url]
            cmd = " ".join(args)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            for line in p.stdout.readlines():
                print line
        except Exception, e:
            print e

    def download_image(self, image, dest=None):
        if not dest:
            dest = './%s' % image
        url = 'https://' + config.host + '/api/images/raw/%s' % image
        try:
            args = ['curl',
                    '--cert', config.proxy,
                    '--insecure',
                    url, '>', dest]
            cmd = " ".join(args)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            for line in p.stdout.readlines():
                print line
        except Exception, e:
            print e

