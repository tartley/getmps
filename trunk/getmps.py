
import codecs
import json
import sys

from twfy import TWFY


VERSION = '0.1.2'
API_KEY = 'AQKQirGqLeMgFYEp3QDXjzte'

USAGE = '''
USAGE: getmps <inputfile >outputfile

Reads lines from stdin, of the form:

    memberid, postcode

Outputs lines on stdout, of the form:

    memberid, postcode, mp, constituency
'''

twfy = TWFY.TWFY(API_KEY)


class Member(object):

    def __init__(self, id, postcode):
        self.id = id
        self.postcode = postcode
        self.mp = ''
        self.constituency = ''

    def __str__(self):
        return '%s, %s, %s, %s' % (
            self.id, self.postcode, self.mp, self.constituency)


def gen_postcodes():
    for line in sys.stdin.readlines():
        line = line.strip()
        if len(line) > 0:
            memberid, postcode = (x.strip() for x in line.split(','))
            yield Member(memberid, postcode)


def populate_member(member):
    postcode_valid = (
        member.postcode != '"postcode"' and
        member.postcode != '' and
        member.postcode != '""')
    if postcode_valid:
        mp_info_js = twfy.api.getMP(postcode=member.postcode, output='js')
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

    members = gen_postcodes()
    members = gen_mps(members)
    members = display_progress(members)
    pretty_print(members)
    sys.stderr.write('done\n')


if __name__ == '__main__':
    main()

  