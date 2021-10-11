import logging

import gevent.pool
import gevent.server
import gevent.socket
import gevent.pywsgi

class Server(object):
    def __init__(self, config, on_update):
        self._server = None
        self._config = config
        self._on_update = on_update

    def open(self):
        logging.info('Open')
        pool = gevent.pool.Pool(10) # limit to 10 connections
        self._server = gevent.pywsgi.WSGIServer(
            self._config.http_server_bind,
            self._handle_request,
            spawn=pool)
        self._server.start()

    def close(self):
        logging.info('Close')
        self._server.stop()
        self._server = None

    def _handle_request(self, env, start_response):
        if env['PATH_INFO'] == '/health':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b"<b>Healthy</b>"]

        if env['PATH_INFO'] == '/update':
            self._on_update()
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b"<b>Updated ICAL</b>"]

        if env['PATH_INFO'] == '/':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [b"<b>hello world</b>"]

        start_response('404 Not Found', [('Content-Type', 'text/html')])
        return [b'<h1>Not Found</h1>']
