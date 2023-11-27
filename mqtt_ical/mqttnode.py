import json
import logging


class MqttNode:
    def __init__(
        self, mqtt, state_path, events_path, retain, qos, mode_path, on_mode=None
    ):
        self._mqtt = mqtt
        self._state_path = state_path
        self._events_path = events_path
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
        self._mqtt.publish(
            self._state_path, payload=value, qos=self._qos, retain=self._retain
        )

    def set_events(self, events):
        if not self._events_path:
            return

        logging.info("Update events %s", self._events_path)
        payload = json.dumps([self._jsonify_event(event) for event in events])
        print(payload)
        self._mqtt.publish(
            self._events_path, payload=payload, qos=self._qos, retain=self._retain
        )

    def _jsonify_event(self, event):
        result = {}
        for key, value in event.property_items():
            str_value = value
            if hasattr(value, "dt") and hasattr(value.dt, "isoformat"):
                str_value = value.dt.isoformat()
            elif hasattr(value, "to_ical"):
                str_value = value.to_ical().decode("utf-8")
            elif value is None or value is True or value is False:
                pass
            else:
                str_value = str(value, "utf-8")

            params = {}
            if hasattr(value, "params"):
                params = dict(value.params)

            if key not in result:
                result[key] = []
            result[key].append({"value": str_value, "params": params})
        return result

    # def status(self, payload):
    #     if not self._status_path:
    #         return
    #     if not isinstance(payload, str):
    #         payload = json.dumps(payload, sort_keys=True)

    #     self._mqtt.publish(self._status_path, payload=payload, qos=0, retain=True)
