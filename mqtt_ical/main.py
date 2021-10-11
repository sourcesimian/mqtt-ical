import sys
import logging

from functools import partial

import gevent
import gevent.monkey
gevent.monkey.patch_all()
gevent.get_hub().SYSTEM_ERROR = BaseException

import mqtt_ical.config
import mqtt_ical.binding
import mqtt_ical.ical
import mqtt_ical.mqtt
import mqtt_ical.server

FORMAT = '%(asctime)-15s %(levelname)s [%(module)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)


def cli():
    config_file = 'config.yaml' if len(sys.argv) < 2 else sys.argv[1]
    config = mqtt_ical.config.Config(config_file)

    ical = mqtt_ical.ical.ICal(config)
    mqtt = mqtt_ical.mqtt.Mqtt(**config.mqtt)
    on_update = partial(ical.update_now)
    server = mqtt_ical.server.Server(config, on_update)

    binding = mqtt_ical.binding.Binding(mqtt, ical)

    for channel in config.channels:
        binding.add_channel(channel)

    mqtt.open()
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

