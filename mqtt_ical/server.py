import logging
import json

import gevent.pool
import gevent.server
import gevent.socket
import gevent.pywsgi

from gevent.pywsgi import WSGIHandler


class Server:
    def __init__(self, config, on_update):
        self._server = None
        self._c = config
        self._on_update = on_update

    def open(self):
        logging.info('Open')
        pool = gevent.pool.Pool(self._c.get('max-connections', 100))
        bind = (
            self._c.get('bind', '0.0.0.0'),
            int(self._c.get('port', 8080))
        )
        logging.info('Server listening on: %s:%s', *bind)
        self._server = gevent.pywsgi.WSGIServer(
            bind,
            self._handle_request,
            handler_class=Handler,
            spawn=pool)
        try:
            self._server.start()
            return True
        except OSError as ex:
            logging.error('%s: %s', ex.__class__.__name__, ex)
        return False

    def close(self):
        logging.info('Close')
        self._server.stop()
        self._server = None

    def _handle_request(self, env, start_response):
        if env['PATH_INFO'] == '/api/health':
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({'health': 'okay'}).encode()]

        if env['PATH_INFO'] == '/api/update':
            self._on_update()
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({'update': True}).encode()]

        if env['PATH_INFO'] == '/':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b"<p>Hello from mqtt-ical</p>"]

        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']


class Handler(WSGIHandler):
    def log_request(self):
        if '101' not in str(self.status):
            logging.debug(self.format_request())
