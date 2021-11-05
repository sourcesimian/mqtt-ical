import logging
import os.path

from mqtt_ical.mqttnode import MqttNode

from functools import partial

class Binding(object):
    def __init__(self, mqtt, ical):
        self._mqtt = mqtt
        self._ical = ical
        self._channel_map = {}

    def _blob_id(self, blob):
        ret = []
        ret.append(blob['ical']['match'])
        ret.append(blob['mqtt']['state']['topic'])
        return '-'.join(ret)

    def add_channel(self, blob):
        if blob['type'] == 'event':
            on_ical_change = partial(self._on_ical_change, blob)
            ical = self._ical.register(blob['ical']['url'], blob['ical']['match'], on_ical_change)

            on_mqtt_change = partial(self._on_mqtt, blob)

            mqtt = MqttNode(self._mqtt,
                            blob['mqtt']['state']['topic'],
                            blob['mqtt']['state']['retain'],
                            blob['mqtt']['state']['qos'],
                            blob['mqtt']['mode']['topic'],
                            on_mqtt_change)

            self._channel_map[self._blob_id(blob)] = {'ical': ical, 'mqtt': mqtt}
        else:
            logging.warning('Unsupported channel type "%s"', blob['type'])

    def _on_ical_change(self, blob, state):
        if state:
            payload = blob['mqtt']['state']['active']
        else:
            payload = blob['mqtt']['state']['default']

        logging.debug('Set state: %s', payload)
        self._channel_map[self._blob_id(blob)]['mqtt'].set_state(payload)

    def _on_mqtt(self, blob, value, timestamp):
        ical = self._channel_map[self._blob_id(blob)]['ical']
        if value == blob['mqtt']['mode']['enable']:
            ical.enable(True)
        elif value == blob['mqtt']['mode']['disable']:
            ical.enable(False)
        else:
            logging.warning('Unrecognised mode: %s', value)

        
        