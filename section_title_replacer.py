#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pywikibot
from pywikibot import pagegenerators
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
    "ראה גם" : REOGAM,
    "הערת שוליים" : SHULAIM,
    "הערות שוליים" : SHULAIM,
    "קשורים חיצוניים" : KISHURIM,
    "מקורות" : SIMUCHIN

}

def fix_page(page_title, page_text):

    for key, value in titles_replacer.iteritems():
        page_text = re.sub("===\s*%s\s*===" % (key), "=== %s ===" % (value), page_text, re.MULTILINE )
    
    return page_text

def main(args):
    
    gen_factory = pagegenerators.GeneratorFactory()
    site = pywikibot.Site('he', 'wiktionary')    
    maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה")

    global_args  = []

    limit = -1
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


    changed = ''


    if article:
        page = pywikibot.Page(site,article.decode('utf-8'))
        print page.title()[::-1]
        page_text = page.get()
        new_text = fix_page(page.title(),page_text)
            
        if(new_text != page_text):
            print 'CHANGED'
            changed += '\n\n* [[%s]]' % page.title()
            page.text = new_text
            page.save("סריקה עם בוט ")


    else:
        n = 1
        for page in maintain_page.linkedPages():
            if limit == 0:
                break
            elif limit > 0:
                limit -= 1
            print str(n)+" "+page.title()[::-1]
            n += 1
            page_text = page.get()
            new_text = fix_page(page.title(),page_text)
            
            if(new_text != page_text):
                print 'CHANGED'
                changed += '\n\n* [[%s]]' % page.title()
                page.text = new_text
                page.save("סריקה עם בוט ")

                
    f = open('changed.txt' ,'w')
    f.write(changed.encode('utf-8'))
    f.close()

    
    print '_____________________DONE____________________'
    

if __name__ == "__main__":
    main(sys.argv)
