import hashlib
import logging
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


class Config:
    def __init__(self, config_file):
        logging.info('Config file: %s', config_file)
        with open(config_file, 'rt', encoding="utf8") as fh:
            self._d = yaml.load(fh, Loader=yaml.Loader)

        for binding in self._d['bindings']:
            default(binding['mqtt']['state'], 'default', 'OFF')
            default(binding['mqtt']['state'], 'active', 'ON')
            default(binding['mqtt']['state'], 'retain', False)
            default(binding['mqtt']['state'], 'qos', 0)
            default(binding['mqtt'], 'mode', {})
            default(binding['mqtt']['mode'], 'topic', None)
            default(binding['mqtt']['mode'], 'enable', 'AUTO')
            default(binding['mqtt']['mode'], 'disable', 'MANUAL')

        self._hash = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()

        self._d['mqtt']['client-id'] += f'-{self._hash[8:]}'

    @property
    def log_level(self):
        try:
            level = self._d['logging']['level'].upper()
            return {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'WARN': logging.WARNING,
                'ERROR': logging.ERROR,
            }[level]
        except KeyError:
            return logging.DEBUG

    @property
    def ical(self):
        return self._d.get('ical', {})

    @property
    def http(self):
        return self._d.get('http', {})

    @property
    def mqtt(self):
        return self._d['mqtt']

    @property
    def bindings(self):
        for item in self._d['bindings']:
            yield item
