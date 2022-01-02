from setuptools import setup


setup(
    name="mqtt-ical",
    version=open('version', 'rt', encoding="utf8").read().strip(),
    description="iCal Calendar to MQTT bridge service",
    author="Source Simian",
    url="https://github.com/sourcesimian/mqtt-ical",
    license="MIT",
    packages=['mqtt_ical'],
    install_requires=open('python3-requirements.txt', encoding="utf8").readlines(),
    entry_points={
        "console_scripts": [
            "mqtt-ical=mqtt_ical.main:cli",
        ]
    },
)
