#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
In the Hebrew Wiktionary, the titles of sections of defintions must be from a determined list, the list is listed in hewiktionary.py.
This script replaces the titles of the sctions to the right title name required
"""

import pywikibot
from pywikibot import pagegenerators
from pywikibot.tools import issue_deprecation_warning

import re
import sys
import hewiktionary
import argparse

titles_replacer = {

    "דעת פרשנים" : hewiktionary.PARSHANIM,
    "צרופים" :  hewiktionary.TSERUFIM,
    "ביטויים וצרופים" :  hewiktionary.TSERUFIM,
    "צירופים וביטויים" :  hewiktionary.TSERUFIM,
    "מילים קרובות" : hewiktionary.NIRDAFOT,
    "מלים נרדפות" : hewiktionary.NIRDAFOT,
    "נרדפות" : hewiktionary.NIRDAFOT,
    "מילים מנוגדות" : hewiktionary.NIGUDIM,
    "נגודים" : hewiktionary.NIGUDIM,
    "תרגומים" : hewiktionary.TERGUM,
    "תירגום" : hewiktionary.TERGUM,
    "תירגומים" : hewiktionary.TERGUM,
    "ראה גם" : hewiktionary.REOGAM,
    "הערת שוליים" : hewiktionary.SHULAIM,
    "קשורים חיצוניים" : hewiktionary.KISHURIM,
    "מקורות" : hewiktionary.SIMUCHIN,
    "גזרון" : hewiktionary.GIZRON
}

class SectionTitleReplacerBot(pywikibot.CurrentPageBot):

    def treat_page(self):
        """Load the given page, do some changes, and save it."""

        print(self.current_page.title())
        old_page_text = self.current_page.text
        new_page_text = old_page_text

        for key, value in titles_replacer.items():
            if re.compile("===\s*%s\s*===" % (key)).search(new_page_text):
                new_page_text = re.sub("===\s*%s\s*===" % (key), "=== %s ===" % (value), new_page_text, re.MULTILINE )

        if(new_page_text != old_page_text):
            print('CHANGED')
            self.put_current(new_page_text, summary = u'בוט המחליף כותרות סעיפים')


def main(args):

    site = pywikibot.Site('he', 'wiktionary')
    maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה")

    local_args = pywikibot.handle_args(args)
    genFactory = pagegenerators.GeneratorFactory()
    article = None
    options = {}

    for arg in local_args:
        if arg.startswith("-article"):
            article = re.compile('^-article:(.+)$').match(arg).group(1)
        elif arg  == '-always':
            options['always'] = True
        else:
            genFactory.handleArg(arg)

    genFactory.handleArg('-intersect')

    if article:
        print(article[::-1])#the terminal shows hebrew left to write :(
        gen = [pywikibot.Page(site, article)]
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        gen = pagegenerators.LinkedPageGenerator(maintain_page, content = True)

    gen = genFactory.getCombinedGenerator(gen)

    bot = SectionTitleReplacerBot(generator = gen,site = site, **options)
    bot.run()

    print('_____________________DONE____________________')

if __name__ == "__main__":
    main(sys.argv)
