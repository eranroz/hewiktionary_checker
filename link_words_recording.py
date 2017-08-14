
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

class HebrewWordsRecordsLinkerBot(pywikibot.CurrentPageBot):

    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        print(self.current_page.title())
        s = re.compile(u'^File:He-([\u0590-\u05f4\u200f]+)\.ogg$').match(self.current_page.title())
        if s:
            word = s.group(1) 
            site = pywikibot.Site('he','wiktionary')
            word_wiithout_nikud  = re.sub('[\u0590-\u05c7\u200f]','',word)
            #print("WITHOUT")
            #print(word_wiithout_nikud)
            p = pywikibot.Page(site,title = word_wiithout_nikud)
            #print(word)
            #
            if p.exists():
                print("EXIST:")   
            

    
        #if new_page_text != self.current_page.text:
        #    print('saving %s' % self.current_page.title())
        #    self.put_current(new_page_text, summary = u'בוט המחליף כותרות סעיפים מסדר 2 לסדר 3')

def main(args):
    
    site = pywikibot.Site('commons', 'commons')    
    cat = pywikibot.Category(site,'Category:Hebrew_pronunciation')
    gen = pagegenerators.CategorizedPageGenerator(cat)
    #maintain_page = pywikibot.Page(site, title = "Category:Hebrew_pronunciation",ns = 14)
    #print(maintain_page)
    #print("EXIST:")
    #print(maintain_page.exists())
    
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
#    if article:
#        gen = [pywikibot.Page(site, article)]
#        gen = pagegenerators.PreloadingGenerator(gen)
#    else:
#        print("sdfsdf")
#        gen = pagegenerators.LinkedPageGenerator(maintain_page, content = True)
        #gen = pagegenerators.RegexFilter.titlefilter(gen, '.+\.ogg$')

    #for page in maintain_page.linkedPages():
    #for page in gen:
#   #     print('sdfsdfsdfsdff')
    #    print(page)
        
    bot = HebrewWordsRecordsLinkerBot(generator = gen)
    bot.run()  

    print('_____________________DONE____________________')
    

if __name__ == "__main__":
    main(sys.argv)
