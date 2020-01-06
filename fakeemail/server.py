from __future__ import absolute_import, print_function

try:
    from email import message_from_bytes
except ImportError:
    # Python < 3.2
    from email import message_from_string as message_from_bytes
import os
import tempfile

import six
from twisted.application import service
from twisted.python import usage

from fakeemail.smtp_server import WebMessageESMTPFactory, makeSMTPService
from fakeemail.web_server import WebMessageRouter, Site, makeWebService


_TEMPDIR = None


def get_tempdir():
    global _TEMPDIR
    if not _TEMPDIR:
        _TEMPDIR = tempfile.mkdtemp('fakeemail')
    return _TEMPDIR


class WebMessageStorage(object):

    messages = {}

    def addMessage(self, to, message):
        dest = six.text_type(to.dest)
        if dest in self.messages:
            self.messages[dest].append(
                self.process_message(message))
        else:
            self.messages[dest] = [self.process_message(message)]

        print("Message stored for: " + dest)

    def process_message(self, message):
        # Unpack each message and store the attachments to a temporary
        # directory, and retain the local path where we have stored
        # them. Return the message and the list of local paths.
        msg = message_from_bytes(message)
        attachments_paths = []
        for part in msg.walk():
            content_type = part.get_content_type()
            if (part.get_content_maintype() !=
                    'multipart') and not content_type.startswith('text/'):
                # Then we assume we have an attachment to store
                fpath = os.path.join(get_tempdir(), part.get_filename())
                with open(fpath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                attachments_paths.append(fpath)

        return msg, attachments_paths

    def get_for_name(self, name):
        if name in self.messages:
            return self.messages[name]
        return None

    def get_all_names(self):
        return self.messages.keys()

    def get_count(self, name):
        return len(self.messages[name])

    def clear_all(self):
        self.messages = {}


class Options(usage.Options):
    optParameters = [
        ["smtp_port", "s", 2025, "SMTP Server Port"],
        ["web_port", "w", 8000, "Web Server Port"],
        ["web_interface", "i", "127.0.0.1", "Web Server Interface"],
    ]


def makeService(config):

    storage = WebMessageStorage()

    s = service.MultiService()

    smtp_port = int(config.get('smtp_port'))
    web_port = int(config.get('web_port'))
    web_interface = config.get('web_interface')

    smtpService = makeSMTPService(smtp_port, storage)
    smtpService.setServiceParent(s)

    webService = makeWebService(web_interface, web_port, storage)
    webService.setServiceParent(s)

    return s


def start(config=None):

    if not config:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("smtp_port", help="SMTP Port", type=int)
        parser.add_argument("web_port", help="Web Port", type=int)
        parser.add_argument("web_interface",
                            help="Listening interface for web")
        args = parser.parse_args()

        config = {
            'smtp_port': args.smtp_port,
            'web_port': args.web_port,
            'web_interface': args.web_interface
        }

    from twisted.internet import reactor
    storage = WebMessageStorage()
    temp_dir = get_tempdir()
    smtp_factory = WebMessageESMTPFactory(storage)
    root = WebMessageRouter(storage, temp_dir)

    reactor.listenTCP(config['smtp_port'], smtp_factory)
    reactor.listenTCP(config['web_port'], Site(root),
                      interface=config['web_interface'])

    reactor.run()
