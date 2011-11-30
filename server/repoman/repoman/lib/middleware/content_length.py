from webob import Request

class ContentLengthMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = req.get_response(self.app)

        content_length = resp.headers.get('x-content-length')
        if content_length: 
            resp.headers['Content-Length'] = content_length

        return resp(environ, start_response)
