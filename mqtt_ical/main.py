import importlib.metadata
import logging
import sys

from functools import partial

import gevent
import gevent.monkey

import mqtt_ical.binding            # noqa: E402 pylint: disable=C0413
import mqtt_ical.config             # noqa: E402 pylint: disable=C0413
import mqtt_ical.ical               # noqa: E402 pylint: disable=C0413
import mqtt_ical.mqtt               # noqa: E402 pylint: disable=C0413
import mqtt_ical.server             # noqa: E402 pylint: disable=C0413

gevent.monkey.patch_all()
gevent.get_hub().SYSTEM_ERROR = BaseException

FORMAT = '%(asctime)-15s %(levelname)s [%(module)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


def cli():
    meta = dict(importlib.metadata.metadata('mqtt_ical'))
    logging.info('Running mqtt-ical v%s', meta['Version'])

    config_file = 'config.yaml' if len(sys.argv) < 2 else sys.argv[1]
    config = mqtt_ical.config.Config(config_file)

    logging.getLogger().setLevel(level=config.log_level)

    ical = mqtt_ical.ical.ICal(config.ical)
    mqtt = mqtt_ical.mqtt.Mqtt(config.mqtt)
    on_update = partial(ical.update_now)
    server = mqtt_ical.server.Server(config.http, on_update)

    binding = mqtt_ical.binding.Binding(mqtt, ical)

    for binding_blob in config.bindings:
        binding.add_binding(binding_blob)

    binding.open()
    ical.open()
    server.open()
    mqtt_loop = mqtt.run()
    ical_loop = ical.run()

    try:
        gevent.joinall((mqtt_loop, ical_loop,))
    except KeyboardInterrupt:
        server.close()
        ical.close()
        mqtt.close()
