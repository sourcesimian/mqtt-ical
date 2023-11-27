import logging


class ICalSchedule:
    def __init__(self, match, on_state_change, on_events_change, on_update_now):
        self._match = match
        self._on_state_change = on_state_change
        self._on_events_change = on_events_change
        self._on_update_now = on_update_now
        self._state = None
        self._enable = True

    def is_match(self, summary):
        return summary == self._match

    def set_state(self, state):
        if self._state == state:
            return
        self._state = state
        if not self._enable:
            logging.debug('{%s} Skipped switch: %s', self._match, state)
        else:
            logging.debug("{%s} Switch: %s", self._match, state)
            self._on_state_change(state)

    def update_events(self, events):
        self._on_events_change(events)

    def enable(self, enable):
        if enable != self._enable:
            if enable:
                self._on_update_now()
                logging.info('{%s} Enabled and setting: %s', self._match, 'active' if self._state else 'default')
                self._on_state_change(self._state)
            else:
                logging.info('{%s} Disabled', self._match)

        self._enable = enable
