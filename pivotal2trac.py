#!/usr/bin/env python

import csv
import sys
import getpass
import mechanize
from optparse import OptionParser

protocol = 'http://'

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c', '--component', dest='component', help='trac component')
    parser.add_option('-u', '--username', dest='user', help='trac username')
    parser.add_option('-s', '--host', dest='host', help='trac server host')
    parser.add_option('-f', '--file', dest='file', help='Pivotal csv export file')
    parser.add_option('-m', '--milestone', dest='milestone', help='trac milestone')
    parser.add_option('-v', '--version', dest='version', help='trac version')
    (options, args) = parser.parse_args()

    if not options.file or not options.host or not options.component or not options.milestone or not options.version:
        parser.print_help()
        sys.exit(1)

    csv_file = open(options.file, 'rb')
    csv_reader = csv.DictReader(csv_file)

    br = mechanize.Browser()

    if options.user:
        username = options.user
    else:
        username = raw_input('Username: ')

    password = getpass.getpass('Password: ')

    login_url = protocol + options.host + '/login'
    ticket_url = protocol + options.host + '/newticket'

    br.add_password(login_url, username, password)
    br.open(login_url)

    for row in csv_reader:
        br.open(ticket_url)
        br.select_form(nr=1)

        br['field_summary'] = row['Story']
        br['field_description'] = row['Description']
        
        story_type = row['Story Type']
        if story_type == 'feature':
            br['field_type'] = ['Feature']
        elif story_type == 'bug':
            br['field_type'] = ['Bug']
        elif story_type == 'chore':
            br['field_type'] = ['Chore']
        elif story_type == 'release':
            continue

        br['field_owner'] = row['Owned By']
        br['field_component'] = [options.component]
        br['field_milestone'] = [options.milestone]
        br['field_version'] = [options.version]

        submit_resposne = br.submit(name='submit')

        print "Added story %s" % row['Id']
