#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
This bot will validate page against list of rules in he-wiktionary

Use get_dump to get the full dump (for developing we are analyzing the full dump)

&params;

Please type "rule_checker.py -help | more" if you can't read the top of the help.
"""

from __future__ import unicode_literals
import pywikibot
from pywikibot import pagegenerators
import re
import pywikibot.textlib
import os
from pywikibot.xmlreader import XmlDump
import requests

GERSHAIM_REGEX = re.compile('["״]')


def get_dump():
    """
    This function downloads teh latest wiktionary dump
    """
    # we already have a dump
    if os.path.exists('pages-articles.xml.bz2'):
        return
    # get a new dump
    print('Dump doesnt exist locally - downloading...')
    r = requests.get('http://dumps.wikimedia.org/hewiktionary/latest/hewiktionary-latest-pages-articles.xml.bz2',
                     stream=True)
    with open('pages-articles.xml.bz2', 'wb') as dump_fd:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                dump_fd.write(chunk)
    print('New dump downloaded successfully')


def split_parts(page_text):
    print('WARNING - not implemented- should break page to sub defintions')
    return [page_text]


class PAGE_PART_TYPE:
    NOUN = 1
    VERB = 2
    PHRASE = 3
    UNKOWN = 4


def check_noun(page_text):
    warnings = []
    print('NOT IMPLEMENTED')
    return warnings


def check_verb(part_type):
    warnings = []
    print('NOT IMPLEMENTED')
    return warnings


def check_phrase(part_type):
    warnings = []
    print('NOT IMPLEMENTED')
    return warnings


def common_checks(part_type):
    warnings = []
    print('NOT IMPLEMENTED')
    return warnings


def check_part(part_text, part_type):
    warnings = []
    if part_type == PAGE_PART_TYPE.NOUN:
        warnings += check_noun(part_type)
    elif part_type == PAGE_PART_TYPE.VERB:
        warnings += check_verb(part_type)
    elif part_type == PAGE_PART_TYPE.PHRASE:
        warnings += check_phrase(part_type)

    warnings += common_checks(part_text)

    return warnings


def check_page(site, page_title, page_text):
    """
    This function checks for violations of the common structure in wiktionary.
    It report the found issues as string
    """
    pywikibot.output('Analyzing page %s' % page_title)
    page_parts = split_parts(page_text)
    text_categories = [cat.title(withNamespace=False) for cat in pywikibot.textlib.getCategoryLinks(page_text, site)]
    warnings = []
    for part in page_parts:
        part_type = PAGE_PART_TYPE.UNKOWN
        warnings += check_part(part, part_type)

    # common checks
    parsed_page_templates = pywikibot.textlib.extract_templates_and_params(page_text)
    nituch_dikduki = [template_params for template_name, template_params in parsed_page_templates
                      if template_name == 'ניתוח דקדוקי']
    has_nituch_dikduki = len(nituch_dikduki) > 0

    if GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' not in text_categories):
        warnings += ['דפים עם גרשיים שאינם ראשי תיבות']  # FIX: warning for gershaim which aren't in category
    elif not GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' in text_categories):
        warnings += ['דפים עם ראשי תיבות חסרי גרשיים']  # FIX: warning for rashi taivut without gershaim
    elif not has_nituch_dikduki:
        warnings += ['דפים חסרי ניתוח דקדוקי']  # FIX: warning of missing nituh dikduki

    return warnings


def main(*args):
    local_args = pywikibot.handle_args(args)
    gen_factory = pagegenerators.GeneratorFactory()

    for arg in local_args:
        if gen_factory.handleArg(arg):
            continue
        elif arg == 'get_dump':
            get_dump()  # download the latest dump if it doesnt exist

    site = pywikibot.Site('he', 'wiktionary')
    if os.path.exists('pages-articles.xml.bz2'):
        print('Using dump')
        all_wiktionary = XmlDump('pages-articles.xml.bz2').parse()  # open the dump and parse it.

        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect, all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary if check_page(site, p.title, p.text))
    else:
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        gen = gen_factory.getCombinedGenerator()

    gen = pagegenerators.PreloadingGenerator(gen)

    # a dictionary where the key is the issue and the value is list of pages violates it
    pages_by_issues = dict()
    for page in gen:
        try:
            issues = check_page(site, page.title(), page.get())
            for issue in issues:
                if issue not in pages_by_issues:
                    pages_by_issues[issue] = []
                else:
                    pages_by_issues[issue].append(page.title())
        except pywikibot.IsRedirectPage:
            continue
        except pywikibot.NoPage:
            continue

    # after going over all pages, report it to a maintenance page so human go over it
    for issue, pages in pages_by_issues.items():
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % issue)
        report_content = '\n'.join(['* [[%s]]' % p for p in pages])
        report_page.put(report_content)

    for page in gen:
        check_page(page.title(), page.text)


if __name__ == "__main__":
    main()
