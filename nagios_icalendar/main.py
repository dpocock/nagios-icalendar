#!/usr/bin/env python

"""
.. module:: main
   :synopsis: Render Nagios issues as iCalendar feed
.. moduleauthor:: Daniel Pocock http://danielpocock.com

"""

# Copyright (C) 2015, Daniel Pocock http://danielpocock.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import datetime
import flask
import github
import icalendar
import logging
import md5
import mk_livestatus
import os
import uuid
import yaml

conf = None

log = logging.getLogger(__name__)
def setup_logging():
    log.setLevel(logging.DEBUG)
    console_out = logging.StreamHandler()
    console_out.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    console_out.setFormatter(formatter)
    log.addHandler(console_out)

def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()

def make_uid(row):
    m = md5.new()
    if 'host_alias' in row:
        # for services
        m.update(row['host_alias'])
        m.update('\0')
        m.update(row['description'])
    else:
        # for hosts
        m.update(row['alias'])
    m.update('\0')
    m.update(row['last_state_change'])
    return m.hexdigest()

host_state_names = ['Up', 'Down', 'Unreachable' ]
def get_host_state_name(state_code):
    return host_state_names[int(state_code)]

service_state_names = ['OK', 'Warning', 'Critical', 'Unknown']
def get_service_state_name(state_code):
    return service_state_names[int(state_code)]

def make_title(row):
    if 'host_alias' in row:
        return "Nagios %s: (%s) %s" % (row['host_alias'], get_service_state_name(row['state']), row['description'])
    else:
        return "Nagios host %s %s" % (row['alias'], get_host_state_name(row['state']))

def parse_nagios_ts(ts):
    return datetime.datetime.fromtimestamp(float(ts))

def get_todo_status(row):
    if row['acknowledged'] == '0':
        return 'NEEDS-ACTION'
    else:
        return 'IN-PROCESS'

def make_contact(row):
    if 'task_contact' in conf:
        return conf['task_contact']
    else:
        return 'nagios@nagios.invalid'

def make_priority(row):
    if row['state'] == '1':
        # Warning status
        return 2
    else:
        # Critical and Unknown status
        return 1

app = flask.Flask(__name__)

@app.route("/")
def ics_feed():
    log.debug('handling a query')
    if conf is None:
        log.error("No configuration available")
        return flask.Response(status_code=500, status='Missing configuration')

    q_contact = flask.request.args.get('contact')

    cal = icalendar.Calendar()
    cal.add('prodid', '-//danielpocock.com//NagiosIssueFeed//')
    cal.add('version', '1.0')

    s = mk_livestatus.Socket(conf['livestatus_sock'])
    q = s.services.columns('state', 'host_alias', 'description', 'long_plugin_output', 'last_state_change', 'last_check', 'action_url_expanded', 'acknowledged').filter('state > 0')
    q_contact = flask.request.args.get('contact')
    if q_contact is not None:
       log.debug("Contact: %s" % q_contact)
       q = q.filter('contacts >= %s' % q_contact)
    result = q.call()
    log.debug("services query got %d row(s)" % (len(result)))
    for row in result:
        try:
            todo = icalendar.Todo()
            todo['uid'] = make_uid(row)
            todo['summary'] = make_title(row)
            todo['description'] = row['long_plugin_output']
            if row['action_url_expanded']:
                todo['url'] = row['action_url_expanded']
            todo.add('created', parse_nagios_ts(row['last_state_change']))
            todo['last-modified'] = parse_nagios_ts(row['last_check'])
            todo['status'] = get_todo_status(row)
            todo['organizer'] = make_contact(row)
            todo['priority'] = make_priority(row)
            cal.add_component(todo)
        except Exception:
            log.error("Failed to parse %r", row, exc_info=True)
            return flask.Response(status_code=500,
                status='Error parsing Nagios data')

    q = s.hosts.columns('state', 'alias', 'plugin_output', 'long_plugin_output', 'last_state_change', 'last_check', 'action_url_expanded', 'acknowledged').filter('state > 0')
    if q_contact is not None:
       log.debug("Contact: %s" % q_contact)
       q = q.filter('contacts >= %s' % q_contact)
    result = q.call()
    log.debug("hosts query got %d row(s)" % (len(result)))
    for row in result:
        try:
            todo = icalendar.Todo()
            todo['uid'] = make_uid(row)
            todo['summary'] = make_title(row)
            todo['description'] = row['long_plugin_output']
            if row['action_url_expanded']:
                todo['url'] = row['action_url_expanded']
            todo.add('created', parse_nagios_ts(row['last_state_change']))
            todo['last-modified'] = parse_nagios_ts(row['last_check'])
            todo['status'] = get_todo_status(row)
            todo['organizer'] = make_contact(row)
            todo['priority'] = make_priority(row)
            cal.add_component(todo)
        except Exception:
            log.error("Failed to parse %r", row, exc_info=True)
            return flask.Response(status_code=500,
                status='Error parsing Nagios data')

    log.debug("done, writing response to stream")
    return flask.Response("%s" % display(cal),
        mimetype='text/calendar')

if __name__ == '__main__':
    setup_logging()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('config_filename')
    args = arg_parser.parse_args()
    with open(args.config_filename) as f:
        conf = yaml.load(f)
        log.info("Config loaded")
    app.run(host=conf['bind_address'], port=conf['bind_port'])
    #app.run(host=conf['bind_address'], port=conf['bind_port'], debug=True)

