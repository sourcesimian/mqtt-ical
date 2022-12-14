import logging


class ICalSchedule:
    def __init__(self, match, on_state_change, on_update_now):
        self._match = match
        self._on_state_change = on_state_change
        self._on_update_now = on_update_now
        self._state = None
        self._auto = True
        self._disable = False

    def is_match(self, summary):
        return summary == self._match

    def set_state(self, state):
        if self._state == state:
            return
        self._state = state
        if not self._auto or self._disable:
            logging.info('{%s} Skipped switch: %s', self._match, state)
        else:
            logging.info("{%s} Switch: %s", self._match, state)
            self._on_state_change(state)

    def _update(self):
        self._on_update_now()
        if self._disable:
            self._state = False
        self.set_state(self._state)

    def state(self, state):
        self._state = state

    def auto(self, enable):
        if enable != self._auto:
            self._auto = enable
            if enable:
                logging.info('{%s} Auto', self._match)
                self._update()
            else:
                logging.info('{%s} Manual', self._match)

    def disable(self, disable):
        if self._disable != disable:
            self._disable = disable
            if self._auto:
                if disable:
                    logging.info('{%s} Disable', self._match)
                    self.set_state(False)
                else:
                    logging.info('{%s} Enable', self._match)
                    self._update()
