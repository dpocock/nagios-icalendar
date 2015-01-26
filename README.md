Nagios iCalendar issue feed
===========================

Obtain list of Nagios alerts as iCalendar feed of VTODO items.

[Official repository](https://github.com/dpocock/nagios-icalendar/)

Usage
-----

This script must be installed on the same server as Nagios.

Install the dependencies on your system, on a Debian or Ubuntu system you
may execute a command like this to get everything you need:

    sudo apt-get install python-yaml python-icalendar python-flask \
        python-mk-livestatus check-mk-livestatus

Note that some of the packages may not be in the current stable repository,
you can fetch them from http://packages.debian.org

Add MK Livestatus to /etc/nagios3/nagios.cfg, typically you need
to ensure the following two lines are present:

    event_broker_options=-1

    broker_module=/usr/lib/check_mk/livestatus.o /var/lib/nagios3/rw/live

Reload Nagios:

    systemctl reload nagios3

Create a configuration file for this script, for example:

    livestatus_sock: /var/lib/nagios3/rw/live
    bind_address: ::0
    bind_port: 5001
    task_contact: support@example.org

Start the process (must run as a user having access to the
livestatus_sock socket):

    $ ./nagios_icalendar/main.py nagios-ics.cfg

In your iCalendar client (such as Mozilla Thunderbird with the
Mozilla Lightning plugin) you just have to add a new remote calendar
using the http://host:port URL where your nagios-icalendar instance
is running.

Copyright notice
----------------

Copyright (C) 2015, Daniel Pocock http://danielpocock.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

