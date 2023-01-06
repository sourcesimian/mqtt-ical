import logging


class ICalSchedule:
    def __init__(self, match, on_ical_active, on_update_now):
        self._match = match
        self._on_ical_active = on_ical_active
        self._on_update_now = on_update_now
        self._state = None
        self._last_active = None
        self._auto = True
        self._disable = False

    def is_match(self, summary):
        return summary == self._match

    def clear_last_active(self):
        self._last_active = None

    def set_active(self, active):
        if self._last_active is not None and self._last_active == active:
            return
        self._last_active = active
        self._set_state(active)

    def _set_state(self, state):
        if self._state == state:
            return
        self._state = state
        if not self._auto or (self._disable and state is True):
            logging.info('{%s} Skipped switch: %s', self._match, state)
        else:
            logging.info("{%s} Switch: %s", self._match, state)
            self._on_ical_active(state)

    def _update(self):
        self._on_update_now()
        if self._disable:
            self._state = False
        self._set_state(self._state)

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
                    self._set_state(False)
                else:
                    logging.info('{%s} Enable', self._match)
                    self._update()
