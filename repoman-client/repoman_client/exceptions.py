
class RepomanError(Exception):
    def __init__(self, message, resp=None):
        self.resp = resp            # Original response
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


class InvalidArgumentError(RepomanError):
    def __init__(self, message):
        RepomanError.__init__(self, message)

    def __str__(self):
        return 'Error: Invalid argument.\n%s' % (self.message)

    def __repr__(self):
        return str(self)

class ClientConfigurationError(RepomanError):
    def __init__(self, message):
        RepomanError.__init__(self, message)

    def __str__(self):
        return 'Client configuration error:\n%s' % (self.message)

    def __repr__(self):
        return str(self)

class LoggingError(RepomanError):
    def __init__(self, message):
        RepomanError.__init__(self, message)

    def __str__(self):
        return 'Logging error:\n%s' % (self.message)

    def __repr__(self):
        return str(self)

class ProxyExpiredError(RepomanError):
    def __init__(self, message):
        RepomanError.__init__(self, message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return str(self)

class ProxyNotFoundError(RepomanError):
    def __init__(self, message):
        RepomanError.__init__(self, message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return str(self)

class ImageUtilError(RepomanError):
    def __init__(self, message):
        RepomanError.__init__(self, message)

    def __str__(self):
        return 'ImageUtils error:\n%s' % (self.message)

    def __repr__(self):
        return str(self)

class SubcommandFailure(RepomanError):
    def __init__(self, subcommand, message = None, e = None):
        RepomanError.__init__(self, message)
        self.subcommand = subcommand
        self.exception = e

    def __str__(self):
        m = "[FAILED] %s" % (self.subcommand.command)
        if self.message:
            m += "\n\t%s" % (self.message)
        if self.exception:
            m += "\n\t%s" % (self.exception)
        return m

    def __repr__(self):
        return str(self)

