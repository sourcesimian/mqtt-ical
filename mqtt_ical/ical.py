import logging
import json
import time
import urllib.request
import urllib.error
import os

from datetime import datetime, timezone, timedelta

import icalendar
import recurring_ical_events

import gevent


class ICal(object):
    def __init__(self, config):
        self._config = config
        self._calendars = {}
        self._events = {}
        self._next_update = None

    def open(self):
        logging.info("Open")

    def close(self):
        logging.info("Close")

    def run(self):
        def loop():
            while True:
                now = self._now()
                if not self._next_update or self._next_update < now:
                    self._update(now)
                else:
                    logging.debug('Skipping update')
                sleep = (self._next_update - self._now()).total_seconds()
                gevent.sleep(sleep)
        return gevent.spawn(loop)

    def register(self, url, match, on_state_change):
        sched = ICalSchedule(match, on_state_change)
        if url not in self._calendars:
            self._calendars[url] = []
        self._calendars[url].append(sched)
        return sched

    def update_now(self):
        logging.debug('Update now')
        now = self._now()
        self._update(now)
    
    def _update(self, now):
        self._update_events(now)
        self._update_states(now)

    def _update_events(self, now):
        for url, _ in self._calendars.items():
            calendar = self._get_ical(url)
            if calendar:
                self._events[url] = {
                    'timestamp': now,
                    'events': list(recurring_ical_events.of(calendar).between(now, now + timedelta(seconds=self._config.ical['fetch-window'])))
                }

    def _update_states(self, now):
        next_update = now + timedelta(seconds=self._config.ical['poll-period'])

        off = set()
        for url, schedules in self._calendars.items():
            off.update(schedules)
            if url in self._events:
                events = self._events[url]
                timestamp = events['timestamp']
                if timestamp < (now - timedelta(seconds=self._config.ical['cache-duration'])):
                    continue
                for event in events['events']:
                    start = event["DTSTART"].dt
                    end = event["DTEND"].dt
                    summary = str(event['SUMMARY'])

                    for schedule in schedules:
                        if schedule._is_match(summary):
                            break
                    else:
                        continue

                    if now >= start and now < end:
                        logging.debug("Current event: %s->%s %s", start, end, summary)
                        next_update = min(next_update, end)
                        schedule._set_state(True)
                        off.remove(schedule)
                    else:
                        if start > now:
                            next_update = min(next_update, start)

        for schedule in off:
            schedule._set_state(False)

        self._next_update = next_update
        logging.debug("Next update: %s", self._next_update)

    def _now(self):
        return datetime.utcnow().replace(tzinfo=timezone.utc)

    def _get_ical(self, ical_url):
        try:
            ical_string = urllib.request.urlopen(ical_url).read()
        except (urllib.error.HTTPError, urllib.error.URLError) as ex:
            logging.error('Fetching ICAL URL: %s: %s', ex, ical_url)
            return None

        calendar = icalendar.Calendar.from_ical(ical_string)
        return calendar

class ICalSchedule(object):
    def __init__(self, match, on_state_change):
        self._match = match
        self._on_state_change = on_state_change
        self._state = None
        self._enable = True

    def _is_match(self, summary):
        return summary == self._match

    def _set_state(self, state):
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
            logging.info('%s and Switching: %s', 'Enabled' if enable else 'Disabled', self._state)
            self._on_state_change(self._state)
        
        self._enable = enable
        