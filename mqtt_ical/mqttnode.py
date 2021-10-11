import logging

class MqttNode(object):
    def __init__(self, mqtt, state_path, retain, qos, mode_path, on_mode=None):
        self._mqtt = mqtt
        self._state_path = state_path
        self._mode_path = mode_path
        self._retain = retain
        self._qos = qos
        self._on_mode = on_mode

        if mode_path and on_mode:
            self._mqtt.subscribe(mode_path, self.on_payload)

    def on_payload(self, payload, timestamp):
        self._on_mode(payload, timestamp - self._mqtt.connect_timestamp)

    def set_state(self, value):
        assert isinstance(value, str)

        logging.info("Publish %s: %s", self._state_path, value)
        self._mqtt.publish(self._state_path, payload=value, qos=self._qos, retain=self._retain)

    def status(self, payload):
        if not self._status_path:
            return
        if not isinstance(payload, str):
            payload = json.dumps(payload, sort_keys=True)

        self._mqtt.publish(self._status_path, payload=payload, qos=0, retain=True)
