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


REOGAM = "ראו גם"

def split_parts(page_text):
    
    parts = re.compile("(^==[^=]+==\s*\n)",re.MULTILINE).split(page_text)
    return parts



    
    
class KtzarmarBot(pywikibot.CurrentPageBot):
    def __init__(self, **kwargs):
        super(KtzarmarBot,self).__init__(**kwargs)
        self._pages_without_def = []
        self._ktzarmarim = []
        

    def check_ktzarmar(self,page_text,page_title):
        sections = re.compile("(^===[^=]+===\s*\n)",re.MULTILINE).split(page_text)

        
        hagdarot = sections.pop(0)
        hagdara = re.compile("^#[^:]",re.MULTILINE).search(hagdarot)
        
        if not hagdara:
            self._pages_without_def.append('* [[%s]]' % page_title)
            return True

        is_sec_title = 1
        sec_num = 0
        for section in sections:
            if is_sec_title and not re.compile(REOGAM).search(section):
                sec_num = sec_num + 1
            if(sec_num >= 2):
               return False
            is_sec_title = 1 - is_sec_title

        self._ktzarmarim.append('* [[%s]]' % page_title)
        return True 
                
            
            

    def treat_page(self):

        s = re.compile(u'.*(שורש).*',re.MULTILINE).search(self.current_page.title())
        if s is not None:
            return 

        s = re.compile(u'.*#הפניה.*',re.MULTILINE).search(self.current_page.text)
        if s is not None:
            return 
        
        s = re.compile(u'.*{{קצרמר}}.*',re.MULTILINE).search(self.current_page.text)
        if s is not None:
            return
           
        def_list = split_parts(self.current_page.text)
           
        

        # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
        def_list.pop(0)
    
        defs_num = len(def_list) #sum(1 for i in page_parts)
    
        if defs_num == 0:
           print('page ' + self.current_page.title() +' has no defenitions')
           return
        
        elif defs_num % 2 != 0:
            print('page' + self.current_page.title() +' is mal formed ')
            return
    
        tit = 1
        for part in def_list:
            if tit == 0:
                if self.check_ktzarmar(part,self.current_page.title()):
                    #new_text = self.current_page.text + "\n{{קצרמר}}"
                    #self.put_current(new_text, summary = u'בוט זיהוי קצרמרים')
                    return
            tit = 1 - tit
            
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

    bot = KtzarmarBot(generator = gen,site = site)
    bot.run()

    if article == '':
        report_content = 'סך הכל %s ערכים\n' % str(len(bot._pages_without_def))
        pages = sorted(bot._pages_without_def)
        report_content +=  '\n'.join(['%s' % p for p in bot._pages_without_def])
        report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
        
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/דפים_ללא_הגדרה_או_הגדרה_שאינה_מתחילה_בסולמית')
        report_page.text = report_content
        report_page.save("בוט קצרמרים");


        report_content = 'סך הכל %s ערכים\n' % str(len(bot._ktzarmarim))
        pages = sorted(bot._ktzarmarim)
        report_content +=  '\n'.join(['%s' % p for p in bot._ktzarmarim])
        report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"

        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/קצרמרים_שזוהו_על_ידי_בוט')
        report_page.text = report_content
        report_page.save("בוט קצרמרים");

if __name__ == "__main__":
    main(sys.argv)
