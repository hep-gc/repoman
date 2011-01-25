
# Project imports
from repoman.model import meta
from repoman.model.certificate import Certificate

# Standard imports
from time import strptime, gmtime

# Other imports
from webob import Request

def demo_app(environ,start_response):
    """Borrowed from python wsgiref.simple_server
    Useful for debugging middleware. just return demo_app anywhere in your
    middleware to see the current environ
    """
    from StringIO import StringIO
    stdout = StringIO()
    print >>stdout, "Hello world!"
    print >>stdout
    h = environ.items(); h.sort()
    for k,v in h:
        print >>stdout, k,'=', repr(v)
    start_response("200 OK", [('Content-Type','text/plain')])
    return [stdout.getvalue()]



class UserAuthentication(object):

    def __init__(self, app, deploy_type):
        self.deploy_type = deploy_type
        self.app = app

    def forbidden(self, message):
        self.start_response('403 Forbidden', [('Content-type', 'text/html')])
        return [message]

    def server_error(self):
        start_response('500 Internal Server Error', [('Content-type', 'text/html')])
        return ['The server has experienced an internal error.']

    def cert_expired(self, start, end):
        # Check validity of certificate time.  can prob get rid of this
        try:
            start_time = strptime(start, "%b %d %H:%M:%S %Y %Z")
            end_time = strptime(end, "%b %d %H:%M:%S %Y %Z")
            now = gmtime()
            if not (start_time < now < end_time):
                return True
            else:
                return False
        except:
            self.server_error()

    def get_ssl_from_headers(self, environ):
        req = Request(environ)
        ssl = {'client_dn':req.headers.get('X-Repoman-ssl-client-s-dn'),
               'client_verify':req.headers.get('X-Repoman-ssl-client-verify'),
               'client_v_start':req.headers.get('X-Repoman-ssl-client-v-start'),
               'client_v_end':req.headers.get('X-Repoman-ssl-client-v-end')}
        return ssl

    def get_ssl_from_environ(self, environ):
        ssl = {'client_verify':environ.get('SSL_CLIENT_VERIFY'),
               'client_dn':environ.get('SSL_CLIENT_S_DN'),
               'client_v_start':environ.get('SSL_CLIENT_V_START'),
               'client_v_end':environ.get('SSL_CLIENT_V_END')}
        return ssl

    def __call__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response

        if self.deploy_type == 'mod_wsgi':
            ssl = self.get_ssl_from_environ(environ)
        elif self.deploy_type == 'proxy':
            ssl = self.get_ssl_from_headers(environ)
        else:
            invalid_config_value('deploy_type', self.deploy_type)

        return self.authorize(ssl, environ, start_response)

    def authorize(self, ssl, environ, start_response):
        if ssl.get('client_verify') not in ['SUCCESS']:
            # Enter repoman as an unauthenticated user
            new_env = environ.copy()
            new_env.update({"AUTHENTICATED":False})
            return self.app(new_env, start_response)

        if self.cert_expired(ssl.get('client_v_start'), ssl.get('client_v_end')):
            self.forbidden('Certificate Expired')

        #HACK: will a clients DN always have a CN?
        client_dn = ssl.get('client_dn')
        if client_dn.count('/CN=') > 1:
            # Proxy cert.  need to remove the extra CNs' to get match in db
            while client_dn.count('/CN=') > 1:
                client_dn = client_dn[:client_dn.rindex('/CN=')]

        # Check if client is in the DB
        cert_q = meta.Session.query(Certificate)
        cert = cert_q.filter(Certificate.client_dn==client_dn).first()
        if cert:
            if cert.user.suspended:
                self.forbidden('Accout suspended.  Contact your administrator')
            elif not cert.user.suspended:
                # Update environ with user info
                new_env = environ.copy()
                new_env.update({"AUTHENTICATED":True})
                new_env.update({"REPOMAN_USER":cert.user})
                return self.app(new_env, start_response)
        else:
            new_env = environ.copy()
            new_env.update({"AUTHENTICATED":False})
            return self.app(new_env, start_response)

