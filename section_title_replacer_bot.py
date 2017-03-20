#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
In the Hebrew Wiktionary , the titles of sections of defintions must be from a determined list, the list is listed in hewiktionary_constants.py .
This script replace the titles of the sctions to the right title name required
"""

from __future__ import unicode_literals
import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

import re
import sys
import rule_checker
import hewiktionary_constants

titles_replacer = {

    "דעת פרשנים" : hewiktionary_constants.PARSHANIM,
    "צרופים" :  hewiktionary_constants.TSERUFIM,
    "ביטויים וצרופים" :  hewiktionary_constants.TSERUFIM,
    "צירופים וביטויים" :  hewiktionary_constants.TSERUFIM,
    "מילים קרובות" : hewiktionary_constants.NIRDAFOT,
    "מלים נרדפות" : hewiktionary_constants.NIRDAFOT,
    "נרדפות" : hewiktionary_constants.NIRDAFOT,
    "מילים מנוגדות" : hewiktionary_constants.NIGUDIM,
    "נגודים" : hewiktionary_constants.NIGUDIM,
    "תרגומים" : hewiktionary_constants.TERGUM,
    "תירגום" : hewiktionary_constants.TERGUM,
    "תירגומים" : hewiktionary_constants.TERGUM,
    "ראה גם" : hewiktionary_constants.REOGAM,
    "הערת שוליים" : hewiktionary_constants.SHULAIM,
    "הערות שוליים" : hewiktionary_constants.SHULAIM,
    "קשורים חיצוניים" : hewiktionary_constants.KISHURIM,
    "מקורות" : hewiktionary_constants.SIMUCHIN,
    "גזרון" : hewiktionary_constants.GIZRON
}

class SectionTitleReplacerBot(pywikibot.CurrentPageBot):

    def treat_page(self):
        """Load the given page, do some changes, and save it."""

        print(self.current_page.title())
        old_page_text = self.current_page.text
        new_page_text = old_page_text

        page_title = self.current_page.title()

        for key, value in titles_replacer.items():
            new_page_text = re.sub("===\s*%s\s*===" % (key), "=== %s ===" % (value), new_page_text, re.MULTILINE )
    
        if(new_page_text != old_page_text):
            print('CHANGED')
            self.put_current(new_page_text, summary = u'בוט המחליף כותרות סעיפים')

def main(args):
    
    site = pywikibot.Site('he', 'wiktionary')    
    maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה")

    global_args  = []

    limit = 0
    article = None

    for arg in args:
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        if m:
            limit = int(m.group(1))
        elif a:
            article = a.group(1)
        else:
            global_args.append(arg)

    local_args = pywikibot.handle_args(global_args)

    if article:
        print(article[::-1])
        gen = [pywikibot.Page(site, article.decode('utf-8'))]
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        gen = pagegenerators.LinkedPageGenerator(maintain_page,total = limit, content = True)


    bot = SectionTitleReplacerBot(generator = gen,site = site)
    bot.run()  

    print('_____________________DONE____________________')
    

if __name__ == "__main__":
    main(sys.argv)
