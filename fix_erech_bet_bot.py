#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
bla
"""


import pywikibot
from pywikibot import pagegenerators
import re
import pywikibot.textlib
import os
from pywikibot.xmlreader import XmlDump
#import requests
import sys




class ErechBetBot(pywikibot.CurrentPageBot):
    def __init__(self, **kwargs):
        super(ErechBetBot,self).__init__(**kwargs)
        self._pages = []
        
    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        parts = re.compile(u'(^==[^=]+ [\u05d0-\u05d6][\'`"״\u0027]?\s*==\s*\n)',re.MULTILINE).findall(self.current_page.text)
        if(len(parts)>0):
            print("----1---------")
            self._pages.append( ('* [[%s]] ' % self.current_page.title()))
            print(self._pages)

        parts = re.compile("(^==[^=]+ </?[Ss]>[\u05d0-\u05d4]</?[Ss]>==\s*\n)",re.MULTILINE).findall(self.current_page.text)
        if(len(parts)>0):
            print("----2---------")
            self._pages.append( ('* [[%s]] ' % self.current_page.title()))

    
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
        gen = pagegenerators.PreloadingGenerator(gen,total = limit)

    else:
        #TODO - make sure this case works
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        #gen_factory = pagegenerators.GeneratorFactory(site,'-ns:1')
        #gen_factory.getCombinedGenerator()
        gen =  pagegenerators.AllpagesPageGenerator(site = site,total = limit)

    bot = ErechBetBot(generator = gen,site = site)
    bot.run()
    issue =  'כותרת ערך משני לא תקינה'
    
    report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % issue)

    print(bot._pages)
    report_content = 'סך הכל %s ערכים\n' % str(len(bot._pages))
    pages = sorted(bot._pages)
    report_content +=  '\n'.join(['%s' % p for p in bot._pages])
    report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"                    
    report_page.text = report_content
    report_page.save(__file__+" סריקה עם בוט")
    print('_____________________DONE____________________')
    

if __name__ == "__main__":
    main(sys.argv)
