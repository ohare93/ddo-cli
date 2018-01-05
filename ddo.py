#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import docopt
import itertools
import logging
import os
import re
import requests
import sys
import time
import urllib

version = '0.1'

__doc__ = """
ddo.py {version} --- look up words in Den Danske Ordbog

A command-line interface for looking up words in the Danish online dictionary
Den Danske Ordbog which can be found at http://ordnet.dk/ddo

Usage:
  {filename} [-S] [-s ...] [-v ...] [-i] <word>
  {filename} (-h | --help)
  {filename} --version

Options:
  -S                  Very short output (same as -ssss)
  -s                  Short output (add up to four s'es for shorter output).
  -i                  Print word and its inflections only.
  -h, --help          Show this screen.
  --version           Show version.
  -v                  Print info (-vv for printing lots of info (debug)).

Examples:
  {filename} behændig

Copyright (C) 2016 Thomas Boevith

License: GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO
WARRANTY, to the extent permitted by law.
""".format(filename=os.path.basename(__file__), version=version)


class Word:
    """A word class."""
    def __init__(self, word, senses=[], numsenses=0):
        self.word = word
        self.senses = senses
        self.numsenses = numsenses
        self.download()

    def download(self):
        """Retrieves dictionary word entry from a word page."""
        page = get_page(word=args['<word>'])
        if page is None:
            log.debug('Page is empty')
            sys.exit(1)
        else:
            log.debug('Got page for word: %s' % args['<word>'])

        # Get all senses of headword from wordpage
        senseurls = getsenseurls(page)
        self.numsenses = len(senseurls)
        for senseurl in senseurls:
            log.debug('senseurl: %s' % (senseurl))
            sensepage = get_page(url=senseurl)
            sense = get_sense(sensepage, headword=self)
            if sense is not None:
                sense.prettyprint()
                self.senses.append(sense)


class Sense:
    """A word sense class."""
    newid = itertools.count().next

    def __init__(self, headword=None, sense=None, sensenum=None,
                 sensenumstring=None, senseurl=None, comment=None,
                 pronounciation=None, inflection=None, part_of_speech=None,
                 meanings=None, etymology=None, synonyms=None,
                 examples=None, wordformations=None):
        self.headword = headword
        self.id = Sense.newid()
        self.sense = sense
        self.sensenum = sensenum
        self.sensenumstring = sensenumstring
        self.senseurl = senseurl
        self.comment = comment
        self.pronounciation = pronounciation
        self.inflection = inflection
        self.part_of_speech = part_of_speech
        self.meanings = meanings
        self.etymology = etymology
        self.wordformations = wordformations

    def prettyprint(self):
        """Prints word sense to standard out."""
        if self.sense is None:
            return

        if args['-i']:
            print("%s" % self.sense)
            for i in self.inflection.split(','):
                if i[0] == '-':
                    print("%s%s" % (self.sense, i.strip().strip('-')))
                else:
                    print(i.strip())
            return

        print(self.sense),
        if self.sensenumstring is not None:
            print(self.sensenumstring),
        elif self.sensenum is not None:
            print(self.sensenum),
        if self.pronounciation is not None:
            print(self.pronounciation),
        if self.part_of_speech is not None:
            print(self.part_of_speech),
        print
        if args['-s'] > 3:
            return
        if self.comment is not None:
            print(self.comment)
        if self.inflection is not None:
            print('Bøjning:'),
            print(self.inflection)
        if args['-s'] > 2:
            print
            return
        if self.etymology is not None:
            print('Oprindelse:'),
            print(self.etymology)
        if args['-s'] > 1:
            print
            return
        if self.meanings != []:
            print
            print('Betydninger:')
            for i, meaning in enumerate(self.meanings):
                if meaning['id'] is not None:
                    if len(meaning['id']) == 1:
                        print(str(meaning['id'][0]) + '.'),
                    elif len(meaning['id']) == 2:
                        print(str(meaning['id'][0]) + '.'
                              + chr(int(meaning['id'][1]) + ord('a'))),
                    else:
                        print('.'.join(meaning['id'])),

                if meaning['topic'] is not None:
                    print(meaning['topic'].upper()),
                print(meaning['meaning'])
                if meaning['onyms'] is not None:
                    for j, onym in enumerate(meaning['onyms']):
                        print(onym)

                    if i < len(self.meanings) - 1:
                            print

        if self.wordformations != []:
            print
            print('Orddannelser:')
            for i, formation in enumerate(self.wordformations):
                print(formation)

        if self.id < self.headword.numsenses - 1:
            print('-' * 79)


def gettext(soupfind):
    """Get the text of an element, stripping off white space."""
    if soupfind is not None:
        try:
            return soupfind.get_text().strip()
        except:
            return None


def supernumeral(num, encoding='utf-8'):
    """Convert integer to superscript integer."""
    if encoding == 'utf-8':
        superscripts = ['⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']
        superdigit = ''
        for digit in str(int(num)):
            superdigit += superscripts[int(digit)]
        return superdigit
    else:
        return '(' + str(num) + ')'


def getsenseurls(page):
    """Retrieve all URLS for the senses of a word."""
    soup = BeautifulSoup(page, 'lxml')
    senseurls = []
    try:
        queryresult = soup.find('dl', {'id': 'search-panel'}).find('dd',
                                                        class_='portletResult')
    except:
        e = sys.exc_info()[0]
        log.error('Could not get query results (error: %s)' % e)
        sys.exit(1)

    for resultatbox in queryresult.find_all('div', class_='searchResultBox'):
        links = resultatbox.find_all('a')
        for link in links:
            # Convert URL to accepted ASCII encoding
            url = (link.get('href')).encode('latin-1')
            senseurls.append(url)
        return senseurls


def get_page(word=None, url=None):
    """Download page for a word using either the word or the complete url."""
    if url is not None:
        url = url
    else:
        url = 'http://ordnet.dk/ddo/ordbog?query=' + word

    url = urllib.quote(url, safe=',.:=&/?:')
    r = requests.get(url)
    status_code = r.status_code
    content = r.content
    if status_code == 200:
        log.debug('status code: %s OK' % status_code)
        return content
    if status_code == 404:
        if word is not None:
            print('Ingen resultater i Den Danske Ordbog for: %s' % word)
        log.debug('status code: %s Not Found' % status_code)
        soup = BeautifulSoup(content, 'lxml')
        subwarning = gettext(soup.find('div', class_="subWarning"))
        if subwarning is not None:
            print(subwarning),
        try:
            for tag in soup.find_all('li', class_='visFlere'):
                tag.replaceWith('')
            for suggestion in soup.find('div',
                                class_='nomatch').find('ul',
                                {'id': 'more-alike-list-long'}).find_all('a'):
                print(gettext(suggestion)),
        except:
            return None
        return None
    else:
        log.debug('request status_code: %s:' % status_code)
        return None


def get_sense(sensepage, headword):
    """Extract elements of a word sense by parsning the HTML page."""
    if sensepage is None:
        log.error('Page is empty: %s' % senseurl)
        return None

    soup = BeautifulSoup(sensepage, 'lxml')

    s = Sense(headword=headword)

    artikel = soup.find('div', class_='artikel')
    if artikel is None:
        log.error('Could not retrieve artikel for: %s' % senseurl)
        return None

    sense = artikel.find('div', class_='definitionBoxTop').find('span',
                                                                class_='match')
    s.sense = sense.find(text=True, recursive=False)
    s.sensenum = gettext(sense.find(text=False, recursive=False))

    s.part_of_speech = gettext(artikel.find('div',
                                        class_='definitionBoxTop').find('span',
                                        class_='tekstmedium allow-glossing'))

    inflection = artikel.find('div', {'id': 'id-boj'})
    if inflection is not None:
        inflection = inflection.find('span',
                                     class_='tekstmedium allow-glossing')
        dividerdouble = inflection.find_all('span',
                                            class_='dividerDouble')
        if dividerdouble is not None:
            for e in dividerdouble:
                e.string = '||'
        if inflection is not None:
            s.inflection = inflection.get_text()

    comment = artikel.find('div', class_='definitionBox').find('span',
                                                                class_='tekst')
    if comment is not None:
        s.comment = comment.get_text()

    pronounciation = artikel.find('div', {'id': 'id-udt'})
    if pronounciation is not None:
        pronounciation = pronounciation.find('span',
                                             class_='lydskrift')
        s.pronounciation = pronounciation.get_text().strip()

    etymology = artikel.find('div', {'id': 'id-ety'})
    if etymology is not None:
        for link in etymology.find_all('a'):
            link.insert_before('_')
            link.insert_after('_')
        etymology = etymology.find('span',
                                   class_='tekstmedium allow-glossing')
        ordform = etymology.find_all('span', class_='ordform')
        if ordform is not None:
            for e in ordform:
                e.string = '/' + e.string + '/'
        dividerdot = etymology.find_all('span', class_='dividerDot')
        if dividerdot is not None:
            for e in dividerdot:
                e.string = ' * '
        if etymology is not None:
            s.etymology = etymology.get_text().strip()

    s.meanings = []
    meanings = artikel.find('div', {'id': 'content-betydninger'})

    if meanings is not None:
        for i, b in enumerate(meanings.find_all('div',
                          class_='definitionIndent', recursive=False)):
            meaningdict = {}
            onyms = []
            meaningdict['topic'] = None
            for c in b.find_all('div', class_='definitionBox'):
                dividerstroke = c.find_all('span', class_='dividerStroke')
                if dividerstroke is not None:
                    for e in dividerstroke:
                        e.string = ' * '

                if c.find('span', class_='stempelNoBorder') is not None:
                    meaningdict['topic'] = gettext(c.find('span',
                                             class_='stempelNoBorder'))

                if ('id' in c.attrs and
                      re.compile(r'^betydning-[-0-9]+$').match(c.attrs['id'])):
                    meaningdict['id'] = c.attrs['id'][10:].split('-')
                    meaningdict['meaning'] = c.find('span',
                                        class_='definition').get_text().strip()

                if 'onym' in c.attrs['class']:
                    for link in c.find_all('a'):
                        link.insert_before('_')
                        link.insert_after('_')

                    onymname = gettext(c.find('span', class_='stempel'))
                    onymwords = c.find('span', class_='inlineList')
                    dividersmall = onymwords.find_all('span',
                                                      class_='dividerSmall')
                    if dividersmall is not None:
                        for e in dividersmall:
                            e.string = '|'

                    onyms.append(onymname.upper() + ': ' + gettext(onymwords))

                if 'details' in c.attrs['class']:
                    detailsname = gettext(c.find('span', class_='stempel'))
                    detailswords = c.find('span', class_='inlineList')
                    dividersmall = detailswords.find_all('span',
                                                         class_='dividerSmall')
                    if dividersmall is not None:
                        for e in dividersmall:
                            e.string = '|'

                    onyms.append(detailsname.upper() + ': '
                                 + gettext(detailswords))

                citater = c.find_all('div', class_='rc-box-citater-body')
                for citat in citater:
                    for link in citat.find_all('span', class_='kilde'):
                        link.insert_after('-- ')
                        link.extract()

                    onyms.append(citat.get_text().strip())

            meaningdict['onyms'] = onyms
            s.meanings.append(meaningdict)

    s.wordformations = []
    wordformations = artikel.find('div', {'id': 'content-orddannelser'})
    if wordformations is not None:
        for c in wordformations.find_all('div', class_='definitionBox'):
            for link in c.find_all('a'):
                link.insert_before('_')
                # Ensure white space after links if necessary
                if str(link.next.next) == ' ':
                    link.insert_after('_')
                else:
                    link.insert_after('_ ')

            wordformationname = gettext(c.find('span', class_='stempel'))
            formation = c.find('span', class_='inlineList')
            dividersmall = formation.find_all('span', class_='dividerSmall')
            if dividersmall is not None:
                for e in dividersmall:
                    e.string = '|'

            dividerdouble = formation.find_all('span', class_='dividerDouble')
            if dividerdouble is not None:
                for e in dividerdouble:
                    e.string = '||'

            s.wordformations.append(wordformationname.upper() + ': '
                                    + gettext(formation))

    return s

if __name__ == '__main__':
    start_time = time.time()
    args = docopt.docopt(__doc__, version=str(version))

    log = logging.getLogger(os.path.basename(__file__))
    formatstr = '%(asctime)-15s %(name)-17s %(levelname)-5s %(message)s'
    if args['-v'] >= 2:
        logging.basicConfig(level=logging.DEBUG, format=formatstr)
    elif args['-v'] == 1:
        logging.basicConfig(level=logging.INFO, format=formatstr)
    else:
        logging.basicConfig(level=logging.WARNING, format=formatstr)

    if args['-S']:
        args['-s'] = 4

    log.debug('%s started' % os.path.basename(__file__))
    log.debug('docopt args=%s' % str(args).replace('\n', ''))

    log.info('Looking up: %s' % args['<word>'])

    word = Word('<word>')

    log.debug('Processing time={0:.2f} s'.format(time.time() - start_time))
    log.debug('%s ended' % os.path.basename(__file__))
