import logging


class MqttNode:
    def __init__(self, mqtt, state_blob, on_state, mode_blob, on_mode, disable_blob, on_disable):
        self._mqtt = mqtt
        self._state_blob = state_blob
        self._on_state = on_state
        self._mode_blob = mode_blob
        self._disable_blob = disable_blob
        self._on_mode = on_mode
        self._on_disable = on_disable

        self._mqtt.subscribe(state_blob['topic'], self.on_payload_state)

        if mode_blob['topic'] and on_mode:
            self._mqtt.subscribe(mode_blob['topic'], self.on_payload_mode)

        if disable_blob['topic'] and on_disable:
            self._mqtt.subscribe(disable_blob['topic'], self.on_payload_disable)

    def on_payload_state(self, payload, timestamp):
        if payload == self._state_blob['active']:
            self._on_state(True)
        elif payload == self._state_blob['default']:
            self._on_state(False)
        else:
            logging.warning('Unrecognised state: %s', payload)

    def on_payload_mode(self, payload, timestamp):
        if payload == self._mode_blob['enable']:
            self._on_mode(True)
        elif payload == self._mode_blob['disable']:
            self._on_mode(False)
        else:
            logging.warning('Unrecognised mode: %s', payload)

    def on_payload_disable(self, payload, timestamp):
        if payload == self._disable_blob['active']:
            self._on_disable(True)
        elif payload == self._disable_blob['inactive']:
            self._on_disable(False)
        else:
            logging.warning('Unrecognised disable: %s', payload)

    def set_state(self, state):
        assert isinstance(state, bool)

        if state:
            payload = self._state_blob['active']
        else:
            payload = self._state_blob['default']

        logging.info("Publish %s: %s", self._state_blob['topic'], payload)
        self._mqtt.publish(self._state_blob['topic'], payload=payload, qos=self._state_blob['qos'], retain=self._state_blob['retain'])

    # def status(self, payload):
    #     if not self._status_path:
    #         return
    #     if not isinstance(payload, str):
    #         payload = json.dumps(payload, sort_keys=True)

    #     self._mqtt.publish(self._status_path, payload=payload, qos=0, retain=True)
