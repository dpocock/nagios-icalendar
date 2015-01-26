#!/usr/bin/env python

from setuptools import setup

__version__ = '1.0'

CLASSIFIERS = map(str.strip,
"""Framework :: Flask
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
Natural Language :: English
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2.7
""".splitlines())

entry_points = {
    'console_scripts': [
        'nagios_icalendar = nagios_icalendar.main:main',
    ]
}

setup(
    name="nagios_icalendar",
    version=__version__,
    author="Daniel Pocock",
    author_email="daniel@pocock.pro",
    description="Render Nagios issues as iCalendar feed",
    license="GPLv3+",
    url="https://nagios.com/dpocock/nagios-icalendar",
    long_description="",
    classifiers=CLASSIFIERS,
    keywords="",
    install_requires=[
        'setproctitle>=1.0.1',
    ],
    packages=['nagios_icalendar'],
    package_dir={'nagios_icalendar': 'nagios_icalendar'},
    platforms=['Linux'],
    zip_safe=False,
    entry_points=entry_points,
)

