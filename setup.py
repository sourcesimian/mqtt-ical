from setuptools import setup


setup(
    name="mqtt-ical",
    version="0.0.0",
    description="iCal Calendar to MQTT connector service",
    author="Source Simian",
    url="https://github.com/sourcesimian/mqtt-ical",
    license="MIT",
    packages=['mqtt_ical'],
    install_requires=open('python3-requirements.txt').readlines(),
    entry_points={
        "console_scripts": [
            "mqtt-ical=mqtt_ical.main:cli",
        ]
    },
)
