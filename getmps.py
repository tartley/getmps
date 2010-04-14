#!/usr/bin/python

import json
import sys

from twfy import TWFY


VERSION = '0.1.3'

USAGE = '''
USAGE: getmps <inputfile >outputfile

Reads lines from stdin, of the form:

    memberid, postcode

Outputs lines on stdout, of the form:

    memberid, postcode, mp, constituency
'''

API_KEY = 'AQKQirGqLeMgFYEp3QDXjzte'
twfy = TWFY.TWFY(API_KEY)

class Options(object):

    def __init__(self):
        self.quiet = False

    def parse(self, args):
        if '-q' in args or '--quiet' in args:
            self.quiet = True


class Member(object):

    def __init__(self, uid, postcode):
        self.uid = uid
        self.postcode = postcode
        self.mp = ''
        self.constituency = ''

    def __str__(self):
        return '%s, %s, %s, %s' % (
            self.uid, self.postcode, self.mp, self.constituency)


def gen_postcodes():
    for line in sys.stdin.readlines():
        line = line.strip()
        if len(line) > 0:
            memberid, postcode = (x.strip() for x in line.split(','))
            yield Member(memberid, postcode)


BAD_POSTCODES = [
    '',
    '""',
    '"postcode"',
]

def populate_member(member):
    if member.postcode not in BAD_POSTCODES:
        mp_info_js = twfy.api.getMP(
            postcode=member.postcode, always_return=1, output='js')
        mp_info_js = mp_info_js.replace(b'\xf4', 'o')
        mp_info = json.loads(mp_info_js)
        member.mp = mp_info.get('full_name', '')
        member.constituency = mp_info.get('constituency', '').replace(',', ';')

def gen_mps(members):
    for member in members:
        try:
            populate_member(member)
        except StandardError, e:
            sys.stderr.write('\n' + str(e) + '\n')
        yield member


def display_progress(members):
    count = 0
    for count, member in enumerate(members):
        sys.stderr.write('.')
        if count % 50 == 0 and count > 0:
            sys.stderr.write('%d\n' % (count,))
        yield member


def pretty_print(members):
    for member in members:
        print member


def main():
    if sys.stdin.isatty():
        print USAGE
        sys.exit(1)

    options = Options()
    options.parse(sys.argv)

    members = gen_postcodes()
    members = gen_mps(members)
    if not options.quiet:
        members = display_progress(members)
    pretty_print(members)
    if not options.quiet:
        sys.stderr.write('done\n')


if __name__ == '__main__':
    main()

