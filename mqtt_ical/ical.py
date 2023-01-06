import logging
import urllib.request
import urllib.error

from datetime import datetime, timezone, timedelta

import icalendar
import recurring_ical_events

import gevent

from mqtt_ical.icalschedule import ICalSchedule


class ICal:
    def __init__(self, config):
        self._c = config
        self._calendars = {}
        self._events = {}
        self._next_update = None
        self._last_update = None

    def open(self):
        logging.info("Open")

    def close(self):
        logging.info("Close")

    def run(self):
        def loop():
            while True:
                now = self._now()
                if not self._next_update or self._next_update <= now:
                    self._update(now)
                else:
                    logging.debug('Skipping update')
                sleep = (self._next_update - self._now()).total_seconds()
                gevent.sleep(sleep)
        return gevent.spawn(loop)

    def register(self, url, match, on_state_change):
        sched = ICalSchedule(match, on_state_change, self._on_update_now)
        if url not in self._calendars:
            self._calendars[url] = []
        self._calendars[url].append(sched)
        return sched

    def force_update(self):
        logging.info('Force update')
        for url, schedules in self._calendars.items():
            for schedule in schedules:
                schedule.clear_last_active()
        self._update_now()

    def _update_now(self):
        now = self._now()
        self._update(now)

    def _on_update_now(self):
        if self._last_update and (self._now() - self._last_update) < timedelta(seconds=3):
            return
        self._update_now()
        self._last_update = self._now()

    def _update(self, now):
        self._update_events(now)
        self._update_states(now)

    def _update_events(self, now):
        for url, _ in self._calendars.items():
            calendar = self._get_ical(url)
            if calendar:
                fetch_window = self._c.get('fetch-window', 86400)
                self._events[url] = {
                    'timestamp': now,
                    'events': list(recurring_ical_events.of(calendar).between(now, now + timedelta(seconds=fetch_window)))
                }

    def _update_states(self, now):
        poll_period = self._c.get('poll-period', 3600)
        next_update = now + timedelta(seconds=poll_period)

        off = set()
        for url, schedules in self._calendars.items():
            off.update(schedules)
            if url in self._events:
                events = self._events[url]
                timestamp = events['timestamp']
                cache_duration = self._c.get('cache-duration', 86400)
                if timestamp < (now - timedelta(seconds=cache_duration)):
                    continue
                for event in events['events']:
                    start = event["DTSTART"].dt
                    end = event["DTEND"].dt
                    summary = str(event['SUMMARY'])

                    schedule = None
                    for schedule in schedules:
                        if schedule.is_match(summary):
                            break
                    else:
                        continue

                    if schedule and start <= now < end:
                        logging.debug("Current event: %s->%s %s", start, end, summary)
                        next_update = min(next_update, end)
                        schedule.set_active(True)
                        off.remove(schedule)
                    else:
                        if start > now:
                            next_update = min(next_update, start)

        for schedule in off:
            schedule.set_active(False)

        self._next_update = next_update
        logging.debug("Next update: %s", self._next_update)

    def _now(self):
        return datetime.utcnow().replace(tzinfo=timezone.utc)

    def _get_ical(self, ical_url):
        try:
            with urllib.request.urlopen(ical_url) as req:
                ical_string = req.read()
                calendar = icalendar.Calendar.from_ical(ical_string)
                return calendar
        except (urllib.error.HTTPError, urllib.error.URLError) as ex:
            logging.error('Fetching ICAL URL: %s: %s', ex, ical_url)
        return None

    @property
    def reload_topic(self):
        return self._c.get('reload-topic', None)

    @property
    def reload_payload(self):
        return self._c.get('reload-payload', 'RELOAD')
