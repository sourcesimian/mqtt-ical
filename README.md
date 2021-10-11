MQTT iCal <!-- omit in toc -->
===

***iCal Calendar to MQTT connector service***

A service which controls the values on selected MQTT topics via events in an iCal Calendar, configurable by YAML.

# Containerization
Example `Dockerfile`:

```
FROM python:3.9-slim

COPY mqtt-gpio/python3-requirements.txt /
RUN pip3 install -r python3-requirements.txt

COPY mqtt-ical/setup.py /
COPY mqtt-ical/mqtt_ical /mqtt_ical
RUN python3 /setup.py develop

COPY my-config.yaml /config.yaml

ENTRYPOINT ["/usr/local/bin/mqtt-ical", "/config.yaml"]
```

# Development
Setup the virtualenv:

```
python3 -m venv virtualenv
. ./virtualenv/bin/activate
python3 ./setup.py develop
```

Run the server:

```
mqtt-ical ./config-demo.yaml
```

# License

In the spirit of the Hackers of the [Tech Model Railroad Club](https://en.wikipedia.org/wiki/Tech_Model_Railroad_Club) from the [Massachusetts Institute of Technology](https://en.wikipedia.org/wiki/Massachusetts_Institute_of_Technology), who gave us all so very much to play with. The license is [MIT](LICENSE).
