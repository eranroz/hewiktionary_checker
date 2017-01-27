#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators
import re
import pywikibot.textlib
import os
from pywikibot.xmlreader import XmlDump
#import requests
import sys

GERSHAIM_REGEX = re.compile('["״\'\׳]')


class TsatBot(pywikibot.CurrentPageBot):
    def __init__(self, **kwargs):
        super(TsatBot,self).__init__(**kwargs)
        self._tsat = u'צט'
        self._tanah = u'תנ"ך'
        self._pages_with_merchaot_in_tsitut = []
        
    def treat_page(self):
        tsitutim = re.findall(u'\{\{'+self._tsat+u'/'+self._tanah+u'([^{}]*)\}\}',self.current_page.text,re.MULTILINE)
        if tsitutim:
            for tsitut in tsitutim:
                parts = tsitut.split('|')
                
                if GERSHAIM_REGEX.findall(parts[-1]) or GERSHAIM_REGEX.findall(parts[-2]) or GERSHAIM_REGEX.findall(parts[-3]):
                    self._pages_with_merchaot_in_tsitut.append('* [[%s]]' % self.current_page.title())
                    return
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

    bot = TsatBot(generator = gen,site = site)
    bot.run()

    if article == '':
        report_content = 'סך הכל %s ערכים\n' % str(len(bot._pages_with_merchaot_in_tsitut))
        pages = sorted(bot._pages_with_merchaot_in_tsitut)
        report_content +=  '\n'.join(['%s' % p for p in bot._pages_with_merchaot_in_tsitut])
        report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
        
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/דפים_עם_ציטוט_מהתנך_עם_גרשיים_במראי_מקום')
        report_page.text = report_content
        report_page.save( "בוט ציטוטים");

if __name__ == "__main__":
    main(sys.argv)
