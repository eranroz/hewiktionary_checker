#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
In the Hebrew Wiktionary, the titles of sections of defintions must be from a determined list, the list is listed in hewiktionary.py.
This script replaces the titles of the sctions to the right title name required
"""

import pywikibot
from pywikibot import pagegenerators

import re
import sys
import hewiktionary
import argparse

#GIZRON = "גיזרון"
#MAKOR = "מקור"
#PARSHANIM = "פרשנים מפרשים"
#TSERUFIM = "צירופים"
#NIGZAROT = "נגזרות"
#NIRDAFOT = "מילים נרדפות"
#KROVIM = "ביטויים קרובים"
#NIGUDIM = "ניגודים"
#TERGUM = "תרגום"
#MEIDA = "מידע נוסף"
#REOGAM = "ראו גם"
#KISHURIM = "קישורים חיצוניים"
#SIMUCHIN = "סימוכין"
#SHULAIM = "הערות שוליים"

titles_replacer = {

    "דעת פרשנים" : hewiktionary.PARSHANIM,
    "צרופים" :  hewiktionary.TSERUFIM,
    "ביטויים וצרופים" : hewiktionary.TSERUFIM,
    "צירופים וביטויים" : hewiktionary.TSERUFIM,
    "ביטויים וצירופים" : hewiktionary.TSERUFIM,
    "ביטויים נרדפים" : hewiktionary.KROVIM,
    "ביטויים דומים" : hewiktionary.KROVIM,
    "מילים קרובות" : hewiktionary.NIRDAFOT,
    "מלים נרדפות" : hewiktionary.NIRDAFOT,
    "נרדפות" : hewiktionary.NIRDAFOT,
    "מילים מנוגדות" : hewiktionary.NIGUDIM,
    "נגודים" : hewiktionary.NIGUDIM,
    "תרגומים" : hewiktionary.TERGUM,
    "תירגום" : hewiktionary.TERGUM,
    "תירגומים" : hewiktionary.TERGUM,
    "תרגומים" :  hewiktionary.TERGUM,
    "ראה גם" : hewiktionary.REOGAM,
    "הערת שוליים" : hewiktionary.SHULAIM,
    "קשורים חיצוניים" : hewiktionary.KISHURIM,
    "קישורים חיצונים" : hewiktionary.KISHURIM,
    "מקורות" : hewiktionary.SIMUCHIN,
    "גזרון" : hewiktionary.GIZRON,
    "אטימולוגיה" : hewiktionary.GIZRON
#    "הערה" : hewiktionary.MEIDA # this probably relates to הערות שלויים
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

    local_args = pywikibot.handle_args(args)
    site = pywikibot.Site('he', 'wiktionary')
    maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה")

    genFactory = pagegenerators.GeneratorFactory()
    options = {}

    parser = argparse.ArgumentParser(description="replace wrong subsection titles in the Hebrew Wiktionary",epilog="Options include also global pywikibot options and all generators options")
    parser.add_argument("--article",nargs=1, required=False)
    parser.add_argument("-always",action='store_false', required=False)
    args, factory_args = parser.parse_known_args(local_args)

    options['always'] = args.always

    for arg in factory_args:
        genFactory.handleArg(arg)

    genFactory.handleArg('-intersect')

    if args.article:
        article = args.article[0]
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
