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

            mqtt = MqttNode(self._mqtt,
                            binding_blob['mqtt']['state'], partial(self._on_state, binding_blob),
                            binding_blob['mqtt']['mode'], partial(self._on_mode, binding_blob),
                            binding_blob['mqtt']['disable'], partial(self._on_disable, binding_blob))

            self._binding_map[self._blob_id(binding_blob)] = {'ical': ical, 'mqtt': mqtt}
        else:
            logging.warning('Unsupported binding type "%s"', binding_blob['type'])

    def _on_ical_change(self, binding_blob, state):
        logging.debug('Set state: %s', state)
        self._binding_map[self._blob_id(binding_blob)]['mqtt'].set_state(state)

    def _on_state(self, binding_blob, state):
        ical = self._binding_map[self._blob_id(binding_blob)]['ical']
        ical.state(state)

    def _on_mode(self, binding_blob, auto):
        ical = self._binding_map[self._blob_id(binding_blob)]['ical']
        ical.auto(auto)

    def _on_disable(self, binding_blob, disable):
        ical = self._binding_map[self._blob_id(binding_blob)]['ical']
        ical.disable(disable)
