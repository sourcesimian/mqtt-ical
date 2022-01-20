MQTT iCal <!-- omit in toc -->
===

***iCal Calendar to MQTT bridge service***

A service which publishes values to MQTT topics based on events in an iCal Calendar, configurable by YAML. For example this allows you to hookup events in your Google Calendars to topics on your MQTT broker.

- [Installation](#installation)
  - [Docker](#docker)
  - [MQTT Infrastructure](#mqtt-infrastructure)
- [Configuration](#configuration)
  - [Conventions](#conventions)
  - [iCal](#ical)
  - [MQTT](#mqtt)
    - [MQTT - Basic Auth](#mqtt---basic-auth)
    - [MQTT - mTLS Auth](#mqtt---mtls-auth)
  - [Web Server](#web-server)
  - [Logging](#logging)
  - [Bindings](#bindings)
- [Contribution](#contribution)
  - [Development](#development)
- [Alternatives](#alternatives)
- [License](#license)

# Installation
Prebuilt container images are available on [Docker Hub](https://hub.docker.com/r/sourcesimian/mqtt-ical).
## Docker
Run
```
docker run -n mqtt-ical -d -it --rm -p 8080:8080 \
    --volume my-config.yaml:/config.yaml:ro \
    sourcesimian/mqtt-ical:latest
```
## MQTT Infrastructure
An installation of **mqtt-ical** will need a MQTT broker to connect to. There are many possibilities available. [Eclipse Mosquitto](https://github.com/eclipse/mosquitto/blob/master/README.md) is a great self-hosted option with many ways of installation including pre-built containers on [Docker Hub](https://hub.docker.com/_/eclipse-mosquitto).

To compliment your MQTT infrastructure you may consider the following other microservices:
| Service | Description |
|---|---|
| [mqtt-gpio](https://github.com/sourcesimian/mqtt-gpio/blob/main/README.md) | Connects MQTT topics to GPIO pins. |
| [mqtt-panel](https://github.com/sourcesimian/mqtt-panel/blob/main/README.md) | A self hostable service that connects to a MQTT broker and serves a progressive web app panel. |

# Configuration
**mqtt-ical** consumes a single [YAML](https://yaml.org/) file. To start off you can copy [config-basic.yaml](./config-basic.yaml)

## Conventions
The following are conventions that are used in the YAML configuration:
| Item | Description |
|---|---|
| `<string>` | Any string of characters, preferably "quoted" to avoid YAML from interpreting in a different way. |
| `<topic>` | A MQTT topic, e.g. `fizz/buzz/status`. Subscriptions can also accept the `*` and `#` wildcards. Use "quotes" to ensure that the `#` is not interpreted as a comment.

## iCal

```
ical:
  poll-period: <seconds>        # optional: Interval at which iCal calendars are polled. Default: 3600
  reload-topic: <topic>         # optional: MQTT topic to listen for forced updates
  reload-payload: <string>      #           MQTT payload which will trigger an update. Default: RELOAD
  cache-duration: <seconds>     # optional: Duration to cache iCal events when updates are failing. Default: 86400
  fetch-window: <seconds>       # optional: Duration ahead of time to fetch. Default 86400
```

## MQTT
```
mqtt:
  host: <host>                  # optional: MQTT broker host, default: 127.0.0.1
  port: <port>                  # optional: MQTT broker port, default 1883
  client-id: mqtt-gpio          # MQTT client identifier, often brokers require this to be unique
  topic-prefix: <topic prefix>  # optional: Scopes the MQTT topic prefix
  auth:                         # optional: Defines the authentication used to connect to the MQTT broker
    type: <type>                # Auth type: none|basic|mtls, default: none
    ... (<type> specific options)
```

### MQTT - Basic Auth
```
    type: basic
    username: <string>          # MQTT broker username
    password: <string>          # MQTT broker password
```

### MQTT - mTLS Auth
```
    type: mtls
    cafile: <file>              # CA file used to verify the server
    certfile: <file>            # Certificate presented by this client
    keyfile: <file>             # Private key presented by this client
    keyfile_password: <string>  # optional: Password used to decrypt the `keyfile`
    protocols:
      - <string>                # optional: list of ALPN protocols to add to the SSL connection
```

## Web Server
```
http:
  bind: <bind>                  # optional: Interface on which web server will listen, default 0.0.0.0
  port: <port>                  # optional: Port on which web server will listen, default 8080
  max-connections: <integer>    # optional: Limit the number of concurrent connections, default 100
```

The web server exposes the following API:
* `/api/health` - Responds with 200 if service is healthy
* `/api/update` - Force the the service to reload the calendar cache

## Logging
```
logging:
  level: INFO                   # optional: Logging level, default DEBUG
```

## Bindings
A binding is a functional element, which is used to connect events in an iCal calendar to MQTT topics and payloads.

Bindings are defined under the `bindings` key:
```
bindings:
- ...
```

All bindings have the following form:
```
  - type: event                 # Binding type: event
    ical:
      match: <string>           # Event summary text to match
      url: <iCal URL>           # URL to iCal Calendar
    mqtt:
      state:
        topic: <topic>          # MQTT topic to publish to
        default: <string>       # Default payload
        active: <string>        # Payload published when event is active
        qos: [0 | 1 | 2]        # optional: MQTT QoS to use, default: 1
        retain: [False | True]  # optional: Publish with MQTT retain flag, default: False
      mode:
        topic: <topic>          # optional: MQTT topic to control mode
        enable: <string>        #           Payload to enable binding. Default: AUTO
        disable: <string>       #           Payload to disable binding. Default: MANUAL

```
The `mqtt/mode/topic` can be used to disable the binding from publishing to `mqtt/state/topic` by setting the disable payload. When set to enable payload, the calendar will be reloaded, and `mqtt/state/topic` will be updated.

# Contribution
Yes sure! And please. I built **mqtt-ical** to act as a microservice in a MQTT ecosystem. The cababilities can most likely be replicated using one of the home automation soltutions. However, I like the componentised way of connecting iCal events to a MQTT topic.

Before pushing a PR please ensure that `make check` and `make test` are clean and please consider adding unit tests.

## Development
Setup the virtualenv:

```
python3 -m venv virtualenv
. ./virtualenv/bin/activate
python3 ./setup.py develop
```

You will want to provide your own iCAL URLs in the config file.

Run the service:
```
mqtt-ical ./config-demo.yaml
```

# Alternatives
I like **mqtt-ical** because it can be orchestrated as a single, source controlled and managed micro-service in a MQTT centric architecture which makes for a clean and reliable deployment. There are however alternatives that may be more suitable to your needs:

| Alternative | Description |
|---|---|
| NodeRED::[ical-events](https://flows.nodered.org/node/node-red-contrib-ical-events) | [NodeRED](https://nodered.org/) is a flow-based visual programming tool for wiring together devices, with built in MQTT integration. The ical-events module gets the events from an ical-URL, a caldav-server or from iCloud. |


# License
In the spirit of the Hackers of the [Tech Model Railroad Club](https://en.wikipedia.org/wiki/Tech_Model_Railroad_Club) from the [Massachusetts Institute of Technology](https://en.wikipedia.org/wiki/Massachusetts_Institute_of_Technology), who gave us all so very much to play with. The license is [MIT](LICENSE).
