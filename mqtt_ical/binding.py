import logging

from functools import partial

from mqtt_ical.mqttnode import MqttNode


class Binding:
    def __init__(self, mqtt, ical):
        self._mqtt = mqtt
        self._ical = ical
        self._binding_map = {}

    def open(self):
        if self._ical.reload_topic:
            self._mqtt.subscribe(self._ical.reload_topic, self._on_mqtt_reload)
        logging.info("Open")

    def _on_mqtt_reload(self, payload, _timestamp):
        if payload == self._ical.reload_payload:
            self._ical.update_now()

    def _blob_id(self, blob):
        ret = []
        ret.append(blob['ical']['match'])
        ret.append(blob['mqtt']['state']['topic'])
        return '-'.join(ret)

    def add_binding(self, binding_blob):
        if binding_blob['type'] == 'event':
            on_ical_change = partial(self._on_ical_change, binding_blob)
            ical = self._ical.register(binding_blob['ical']['url'], binding_blob['ical']['match'], on_ical_change)

            on_mqtt_change = partial(self._on_mqtt, binding_blob)

            mqtt = MqttNode(self._mqtt,
                            binding_blob['mqtt']['state']['topic'],
                            binding_blob['mqtt']['state']['retain'],
                            binding_blob['mqtt']['state']['qos'],
                            binding_blob['mqtt']['mode']['topic'],
                            on_mqtt_change)

            self._binding_map[self._blob_id(binding_blob)] = {'ical': ical, 'mqtt': mqtt}
        else:
            logging.warning('Unsupported binding type "%s"', binding_blob['type'])

    def _on_ical_change(self, binding_blob, state):
        if state:
            payload = binding_blob['mqtt']['state']['active']
        else:
            payload = binding_blob['mqtt']['state']['default']

        logging.debug('Set state: %s', payload)
        self._binding_map[self._blob_id(binding_blob)]['mqtt'].set_state(payload)

    def _on_mqtt(self, binding_blob, value, _timestamp):
        ical = self._binding_map[self._blob_id(binding_blob)]['ical']
        if value == binding_blob['mqtt']['mode']['enable']:
            ical.enable(True)
        elif value == binding_blob['mqtt']['mode']['disable']:
            ical.enable(False)
        else:
            logging.warning('Unrecognised mode: %s', value)
