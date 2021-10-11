import hashlib
import json
import logging
import os.path
import random

import yaml

# Prevent YAML loader from interpreting 'on', 'off', 'yes', 'no' as bool
from yaml.resolver import Resolver

for ch in "OoYyNn":
    Resolver.yaml_implicit_resolvers[ch] = [x for x in
            Resolver.yaml_implicit_resolvers[ch]
            if x[0] != 'tag:yaml.org,2002:bool']
def default(item, key, value):
    if key not in item:
        item[key] = value


class Config(object):
    def __init__(self, config_file):
        logging.debug('Config file: %s', config_file)
        with open(config_file, 'rt') as fh:
            self._d = yaml.load(fh, Loader=yaml.Loader)

        for channel in self._d['channel']:
            default(channel['mqtt']['state'], 'default', 'OFF')
            default(channel['mqtt']['state'], 'active', 'ON')
            default(channel['mqtt']['state'], 'retain', False)
            default(channel['mqtt']['state'], 'qos', 0)
            default(channel['mqtt'], 'mode', {})
            default(channel['mqtt']['mode'], 'topic', None)
            default(channel['mqtt']['mode'], 'enable', 'AUTO')
            default(channel['mqtt']['mode'], 'disable', 'MANUAL')

        logging.debug('Config: %s', json.dumps(self._d, sort_keys=True))
        self._hash = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()

        self._d['mqtt']['client-id'] += '-%s' % self._hash[8:]

    @property
    def ical(self):
        return self._d['ical']

    @property
    def http_server_bind(self):
        return ('0.0.0.0', int(self._d['http']['port']))

    @property
    def mqtt(self):
        return self._d['mqtt']

    @property
    def channels(self):
        for item in self._d['channel']:
            yield item


