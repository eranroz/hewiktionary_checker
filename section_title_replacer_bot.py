#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

import re
import pywikibot.textlib
import os
import requests
import sys
import rule_checker

GIZRON = "גיזרון"
MAKOR = "מקור"
PARSHANIM = "פרשנים מפרשים"
TSERUFIM = "צירופים"
NIGZAROT = "נגזרות"
NIRDAFOT = "מילים נרדפות"
KROVIM = "ביטויים קרובים"
NIGUDIM = "ניגודים"
TERGUM = "תרגום"
MEIDA = "מידע נוסף"
REOGAM = "ראו גם"
KISHURIM = "קישורים חיצוניים"
SIMUCHIN = "סימוכין"
SHULAIM = "הערות שוליים"


titles_replacer = {

    "דעת פרשנים" : PARSHANIM,
    "צרופים" :  TSERUFIM,
    "ביטויים וצרופים" :  TSERUFIM,
    "צירופים וביטויים" :  TSERUFIM,
    "מילים קרובות" : NIRDAFOT,
    "מלים נרדפות" : NIRDAFOT,
    "נרדפות" : NIRDAFOT,
    "מילים מנוגדות" : NIGUDIM,
    "נגודים" : NIGUDIM,
    "תרגומים" : TERGUM,
    "תירגום" : TERGUM,
    "תירגומים" : TERGUM,
    "ראה גם" : REOGAM,
    "הערת שוליים" : SHULAIM,
    "הערות שוליים" : SHULAIM,
    "קשורים חיצוניים" : KISHURIM,
    "מקורות" : SIMUCHIN,
    "גזרון" : GIZRON

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

        print(arg)
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        if m:
            limit = int(m.group(1))
        elif a:
            print('a')
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
