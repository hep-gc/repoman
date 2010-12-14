import os
import datetime
from webob import Request, Response, exc
import simplejson

# Python 2.4 compatability
try:
    from hashlib import md5
except:
    from md5 import new as md5

try:
    from hashlib import sha1
except:
    from sha import new as sha1

hash_type_map = {'md5':md5, 'sha1':sha1}


class MaxSizeExceeded(Exception):
    def __init__(self, length, max_size):
        self.length = length
        self.max_size = max_size
        self.description = 'The object that you attempted to upload exceeds the servers maximum allowable size.'
        self.error = {'component':'StorageMiddleware',
                      'error':'MaxSizeExceeded',
                      'max_size':self.max_size,
                      'upload_length':self.length,
                      'description':self.description}

    def __str__(self):
        return self.__json__()

    def __repr__(self):
        return self.__json__()

    def __json__(self):
        return simplejson.dumps({'errors':[self.error]})


class StorageMiddleware(object):
    """WSGI Middleware to stripout posted files and store them in a directory.

    Thanks to the gp.fileupload module for the ideas.
        url: http://pypi.python.org/pypi/gp.fileupload/
        File handling needed to be drastically changed which is why that
        module was not used.
    """

    #pass_through = ['POST', 'GET', 'HEAD', 'DELETE']
    capture = ['PUT']

    def __init__(self, app, temp='/tmp', paths=[], max_size=None, hash_type=None):
        """
        Args:
            app: The WSGI app you are wrapping
            temp: A writable path to temporarily store the uploaded file in
            dest: The final destination path where the file should end up.
            paths (list): The paths that this middleware will act upon
            max_size: What is the maximum file size in Bytes that you will allow
                to be uploaded.  A value of `None` will result in an uncapped
                file size.
        """
        self.temp = temp
        self.max_size = max_size
        self.app = app
        self.paths = paths
        if hash_type_map.get(hash_type):
            self.hash_type = hash_type
            self.hash_func = hash_type_map.get(hash_type)
        else:
            self.hash_type = None
            self.hash_func = None

        self._create_dirs()

    def _create_dirs(self):
        if not os.path.isdir(self.temp):
            os.mkdir(self.temp)

    def _500_error(self):
        e = {'component':'StorageMiddleware',
             'error':'Unknown error',
             'description':'An error has occured while processing your file upload.'}
        return e


    def __call__(self, environ, start_response):
        req = Request(environ)
        new_env = environ.copy()

        # Pass through everything except PUT
        if req.method in self.capture:
            try:
                temp_file, length, file_hash = self.store_files(req)
                new_env.update({'STORAGE_MIDDLEWARE_EXTRACTED_FILE':temp_file})
                new_env.update({'STORAGE_MIDDLEWARE_EXTRACTED_FILE_HASH':file_hash})
                new_env.update({'STORAGE_MIDDLEWARE_EXTRACTED_FILE_HASH_TYPE':self.hash_type})
                new_env.update({'STORAGE_MIDDLEWARE_EXTRACTED_FILE_LENGTH':length})
                new_env.update({'BYPASS_CASCADE':True})
            except MaxSizeExceeded, e:
                start_response('400 Bad Request', [('Content-Type','application/json')])
                return repr(e)
            except:
                try:
                    os.remove(temp_path)
                except:
                    pass
                start_response('500 Internal Server Error', [('Content-Type','application/json')])
                return simplejson.dumps({'errors':[self._500_error()]})

        # Next application
        return self.app(new_env, start_response)

    def read_chunks(self, f, size=1024):
        while True:
            chunk = f.read(size)
            if not chunk:
                break
            yield chunk

    def store_files(self, req):
        length = req.content_length
        if self.max_size and length > self.max_size:
            raise MaxSizeExceeded(length, self.max_size)

        if self.hash_type:
            file_hash = self.hash_func()
        else:
            file_hash = None

        inf = req.environ['wsgi.input']
        temp_name = md5(str(datetime.datetime.now())).hexdigest() + '_body'
        temp_path = os.path.join(self.temp, temp_name)
        temp_file = open(temp_path, 'w')
        for chunk in self.read_chunks(inf):
            if self.hash_type:
                file_hash.update(chunk)
            temp_file.write(chunk)
        temp_file.close()

        if self.hash_type:
            file_hash = file_hash.hexdigest()

        return temp_path, length, file_hash

