from paste.cascade import Cascade
from paste import httpexceptions
from paste.util import converters
import tempfile
from cStringIO import StringIO


class BypassCascade(Cascade):
    """
    Subclasses paste.cascade.Cascade

    if `BYPASS_CASCADE` exists in the environ, then skip calling the Cascade
    if `BYPASS_CASCADE` is not found, then proceed as normal
    """
    def __init__(self, app, applications, catch=(404,)):
        self.app = app
        Cascade.__init__(self, applications, catch)

    def __call__(self, environ, start_response):
        if environ.get('BYPASS_CASCADE'):
            return self.app(environ, start_response)
        else:
            return Cascade.__call__(self, environ, start_response)

