import os

from win_tornado_terminals import TermManager
from tornado.log import app_log
from notebook.utils import url_path_join as ujoin
from .handlers import TerminalHandler, TermSocket
from . import api_handlers


def initialize(webapp, notebook_dir, connection_url, settings):
    default = 'cmd' if os.name == 'nt' else 'sh'
    shell = settings.get('shell_command', [os.environ.get('SHELL') or default])
    terminal_manager = webapp.settings['terminal_manager'] = TermManager(
        shell_command=shell,
        extra_env={'JUPYTER_SERVER_ROOT': notebook_dir,
                   'JUPYTER_SERVER_URL': connection_url,
                   },
    )
    terminal_manager.log = app_log
    base_url = webapp.settings['base_url']
    handlers = [
        (ujoin(base_url, r"/terminals/(\w+)"), TerminalHandler),
        (ujoin(base_url, r"/terminals/websocket/(\w+)"), TermSocket,
             {'term_manager': terminal_manager}),
        (ujoin(base_url, r"/api/terminals"), api_handlers.TerminalRootHandler),
        (ujoin(base_url, r"/api/terminals/(\w+)"), api_handlers.TerminalHandler),
    ]
    webapp.add_handlers(".*$", handlers)
