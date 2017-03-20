#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

import re
import os
import sys
import hewiktionary_constants

class SectionTitleLvl2ndTo3rdBot(pywikibot.CurrentPageBot):

    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        new_page_text = self.current_page.text

        part_titles = re.findall("^ *\t*== *\t*[^=]+ *\t*== *\t*$",self.current_page.text,re.MULTILINE)
        for part_title in part_titles:


            title = re.compile("==\s*([^=]+)\s*==").search(part_title).group(1).strip()
            if title in hewiktionary_constants.titles_list:
                new_page_text = re.sub('\s==\s*'+title+'\s*==\s','\n==='+title+'===\n',new_page_text,re.MULTILINE)

            if new_page_text != self.current_page.text:
                print('saving %s' % self.current_page.title())
                self.put_current(new_page_text, summary = u'בוט המחליף כותרות סעיפים מסדר 2 לסדר 3')

def main(args):
    
    site = pywikibot.Site('he', 'wiktionary')    
    maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_כותרת_סעיף_מסדר_2")

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
        gen = [pywikibot.Page(site, article.decode('utf-8'))]
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        gen = pagegenerators.LinkedPageGenerator(maintain_page,total = limit, content = True)


    bot = SectionTitleLvl2ndTo3rdBot(generator = gen,site = site)
    bot.run()  

    print('_____________________DONE____________________')
    

if __name__ == "__main__":
    main(sys.argv)
