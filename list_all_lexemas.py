# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import requests
import pywikibot

from pywikibot import pagegenerators
from pywikibot.xmlreader import XmlDump
import hewiktionary

DUMP_FILE = 'hewiktionary-latest-pages-articles.xml.bz2'

def get_dump():
    """
    This function downloads teh latest wiktionary dump
    """
    r = requests.get('http://dumps.wikimedia.org/hewiktionary/latest/hewiktionary-latest-pages-articles.xml.bz2',
                     stream=True)
    if r.status_code == 200:
        try:
            with open(DUMP_FILE, 'wb') as dump_fd:
                for chunk in r.iter_content(chunk_size=1024):
                    dump_fd.write(chunk)
        except Exception as e:
            print("could not save dump file")
            os._exit(-1)
    else:
        print(f"could not get dump, status: %d" % r.status_code)
        os._exit(-1)


def file_age_by_days(file):
    file_sec_since_epoch = os.path.getmtime(file)
    sec_since_epoch = time.time()
    sec_age = sec_since_epoch - file_sec_since_epoch
    return sec_age / (60*60*24)


def main(args):

    letter = None
    force_dump = False
    bot_args = []


    for arg in args:

        print('\u05D0'.encode('utf-8'))
        #print(arg.decode('utf-8'))
        l = re.compile(r'^-letter:(.+)$').match(arg)
        print(l)
        if l:
            letter = l.group(1)
        elif arg == '--get-dump':
            force_dump = True  # download the latest dump if it doesnt exist
        else:
            bot_args.append(arg)
    print(bot_args)
    pywikibot.handle_args(bot_args)
    site = pywikibot.Site('he', 'wiktionary')

    if force_dump \
            or not os.path.exists(DUMP_FILE) \
            or file_age_by_days(DUMP_FILE) > 30:
        get_dump()

    all_wiktionary = XmlDump(DUMP_FILE).parse()

    all_wiktionary = filter(lambda page: page.ns == '0' \
                                         and not page.title.endswith('(שורש)') \
                                         and not re.compile(r'[a-zA-Z]').search(page.title) \
                                         and (not letter or page.title.startswith(letter))
                                         and not page.isredirect,
                            all_wiktionary)
    gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
    gen = pagegenerators.PreloadingGenerator(gen)

    words = []
    for page in gen:

        if not page.exists() or page.isRedirectPage():
            continue

        for lex in hewiktionary.lexeme_title_regex_grouped.findall(page.get()):
            words.append("* [[%s#%s|%s]]" % (page.title(),lex,lex))

    report_content = 'סך הכל %s ערכים\n' % str(len(words))
    report_content +=  '\n'.join(['%s' % p for p in words])
    report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"

    if letter:
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s/%s' % ('רשימת_כל_המילים',letter))
    else:
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % ('רשימת_כל_המילים'))
    report_page.text = report_content
    report_page.save("סריקה עם בוט ")

if __name__ == "__main__":
    main(sys.argv)
