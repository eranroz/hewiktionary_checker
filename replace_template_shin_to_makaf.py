#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
This bot will validate page against list of rules in he-wiktionary

Use get_dump to get the full dump (for developing we are analyzing the full dump)

&params;

Please type "rule_checker.py -help | more" if you can't read the top of the help.
"""


import pywikibot
from pywikibot import pagegenerators
import re
import pywikibot.textlib
import os
from pywikibot.xmlreader import XmlDump
#import requests
import sys


    
class ShinToMakafBot(pywikibot.CurrentPageBot):
    def __init__(self, **kwargs):
        super(ShinToMakafBot,self).__init__(**kwargs)
        self._pages_without_def = []
        self._ktzarmarim = []
        

    def treat_page(self):

        s = re.compile(u'.*(שורש).*',re.MULTILINE).search(self.current_page.title())
        if s is not None:
            return 

        s = re.compile(u'.*#הפניה.*',re.MULTILINE).search(self.current_page.text)
        if s is not None:
            return 

        new_page_text = re.sub(u'(\{\{ש\}\}\n?){2,}','{{-}}\n',self.current_page.text,re.MULTILINE)
        self.put_current(new_page_text, summary = u'בוט תבניות {{ש}} לתבנית {{-}} , יופי')           
        return

def main(args):

    site = pywikibot.Site('he', 'wiktionary')
    global_args  = []

    limit = 0
    article = ''
    print(__file__+" סריקה עם בוט")
    
    for arg in args:
    
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        if arg == '--get-dump':
            get_dump()  # download the latest dump if it doesnt exist
        elif m:
            limit = int(m.group(1))
        elif a:
            article = a.group(1)
        else:
            global_args.append(arg)

    local_args = pywikibot.handle_args(global_args)

    #sys.exit(1)

    if article != '':
        print(article[::-1])
        gen = [pywikibot.Page(site, article)]
        gen = pagegenerators.PreloadingGenerator(gen)
    elif os.path.exists('pages-articles.xml.bz2'):
        print('parsing dump')
        all_wiktionary = XmlDump('pages-articles.xml.bz2').parse()  # open the dump and parse it.
        print('end parsing dump')        
        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect, all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
        gen = pagegenerators.PreloadingGenerator(gen)

    else:
        #TODO - make sure this case works
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        #gen_factory = pagegenerators.GeneratorFactory(site,'-ns:1')
        #gen_factory.getCombinedGenerator()
        gen =  pagegenerators.AllpagesPageGenerator(site = site,total = limit)

    bot = ShinToMakafBot(generator = gen,site = site)
    bot.run()

if __name__ == "__main__":
    main(sys.argv)
