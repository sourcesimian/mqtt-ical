import logging


class ICalSchedule:
    def __init__(self, match, on_state_change, on_update_now):
        self._match = match
        self._on_state_change = on_state_change
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
            logging.debug('Skipped switch: %s', state)
        else:
            logging.debug("Switch: %s", state)
            self._on_state_change(state)

    def enable(self, enable):
        if enable and enable != self._enable:
            self._on_update_now()
            logging.info('%s and Switching: %s', 'Enabled' if enable else 'Disabled', self._state)
            self._on_state_change(self._state)

        self._enable = enable
