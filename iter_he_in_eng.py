# -*- coding: utf-8 -*-
"""
Iterate the English wiktionary and search for Hebrew words
that are not in the Hebrew dictionary
"""

import sys
import os
import re
import argparse
import pywikibot
from pywikibot import pagegenerators
from pywikibot.xmlreader import XmlDump
import hewiktionary
import requests

def get_some_wiki_dump(lang_code):
    """
    This function downloads teh latest wiktionary dump
    """
    url = 'http://dumps.wikimedia.org/%swiktionary/latest/%swiktionary-latest-pages-articles.xml.bz2' % (
        lang_code, lang_code)
    file = '%swiktionary-latest-pages-articles.xml.bz2' % (lang_code)
    try:
        req = requests.get(url, stream=True)
    except requests.exceptions.RequestException as exc:
        print("exception getting the dump file %s" % file)
        print(exc)
        return False
    if req.status_code != 200:
        print("status code is not 200 but %d" % req.status_code)
        return False

    with open(file, 'wb') as dump_fd:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                dump_fd.write(chunk)
    return True


def get_dump():
    """
    This function downloads teh latest wiktionary dump
    """
    try:
        req = requests.get('http://dumps.wikimedia.org/hewiktionary/latest/hewiktionary-latest-pages-articles.xml.bz2',
                           stream=True)
    except requests.exceptions.RequestException as e:
        print("exception getting the dump file")
        print(e)
        return False
    if req.status_code != 200:
        print("status code is not 200 but %d" % req.status_code)
        return False

    with open('pages-articles.xml.bz2', 'wb') as dump_fd:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                dump_fd.write(chunk)
    return True


def main(args):
    site = pywikibot.Site('en', 'wiktionary')

    parser = argparse.ArgumentParser(
        description="Iterate the English Wiktionary and search for Hebrew pages there that are not"
                    "in the Hebrew wiktionary",
        epilog="Options include also global pywikibot options and all generators options")
    parser.add_argument("--article", required=False)
    parser.add_argument("--from-article", required=False)
    parser.add_argument("--limit", required=False, type=int, default=-1)
    parser.add_argument("--force-get-dump", required=False, action='store_true')
    parser.add_argument("-always", action='store_false', required=False)
    args, factory_args = parser.parse_known_args(args)

    pywikibot.handle_args(factory_args)

    if args.force_get_dump:
        if not get_dump():
            print("could not get dump of hewiktionary")
            sys.exit(-1)
        if not get_some_wiki_dump("en"):
            print("could not get dump of enwiktionary")
            sys.exit(-1)

    if args.article:
        gen = (pywikibot.Page(site, args.article))
        gen = pagegenerators.PreloadingGenerator(gen)
    elif os.path.exists('enwiktionary-latest-pages-articles.xml.bz2'):
        print('parsing dump')
        all_wiktionary = XmlDump('enwiktionary-latest-pages-articles.xml.bz2').parse()
        print('end parsing dump')

        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect and
                                             hewiktionary.HEBREW_WORD_REGEX.search(page.title), all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        # TODO - make sure this case works
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        # gen_factory = pagegenerators.GeneratorFactory(site,'-ns:1')
        # gen_factory.getCombinedGenerator()
        if args.from_article:
            gen = pagegenerators.AllpagesPageGenerator(start=args.from_article, site=site)
        else:
            gen = pagegenerators.AllpagesPageGenerator(start='א', site=site)

    hesite = pywikibot.Site('he', 'wiktionary')
    list = []
    # f = open('workfile', 'w')
    for idx, page in enumerate(gen):
        if idx % 100 == 0:
            print(page.title())
        if page.title() == 'תתרנית':
            break

        if page.isRedirectPage():
            continue
        if not hewiktionary.HEBREW_WORD_REGEX.search(page.title()):
            continue
        if not re.compile(r"==\s*Hebrew\s*==", re.MULTILINE).search(page.text):
            # print("yidish "+page.title())
            continue
        hepage = pywikibot.Page(hesite, page.title())
        if not hepage.exists():
            list.append("* {{ת|אנגלית|%s}} [[%s]]" % (page.title(), page.title()))
            if len(list) == args.limit:
                break

            # print("* {{ת|אנגלית|%s}}\n"%(page.title()))
            # f.write("* {{ת|אנגלית|%s}}\n"%(page.title()))

    report_page = pywikibot.Page(hesite, 'ויקימילון:תחזוקה/%s' % ('מילים בויקימילון האנגלי שאינם בעברית'))

    report_content = 'סך הכל %s ערכים\n' % str(len(list))

    report_content += '\n'.join(['%s' % p for p in list])
    report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
    report_page.text = report_content
    report_page.save("סריקה עם בוט ")


if __name__ == "__main__":
    main(sys.argv)
