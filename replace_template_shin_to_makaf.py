#!/usr/bin/python3
# -*- coding: utf-8 -*-
r"""
According to Ariel1024 :

החלפה של: {{ש}}{{ש}}{{ש}}{{ש}} וכולי בסוף ערכים לתבנית {{-}}

see:

https://he.wiktionary.org/w/index.php?title=%D7%A9%D7%99%D7%97%D7%AA_%D7%9E%D7%A9%D7%AA%D7%9E%D7%A9:Ariel1024&oldid=255275#.D7.94.D7.99
"""

import pywikibot
from pywikibot import pagegenerators
import re
import os
from pywikibot.xmlreader import XmlDump
import sys

class ShinToMakafBot(pywikibot.CurrentPageBot):

    def treat_page(self):

        s = re.compile(u'.*(שורש).*',re.MULTILINE).search(self.current_page.title())
        if s is not None:
            return 

        s = re.compile(u'.*#הפניה.*',re.MULTILINE).search(self.current_page.text)
        if s is not None:
            return 

        new_page_text = re.sub(u'(\{\{ש\}\}\n?){2,}','{{-}}\n',self.current_page.text,re.MULTILINE)
        if new_page_text != self.current_page.text:
            print('saving page %s' % self.current_page.title())
            self.put_current(new_page_text, summary = u'בוט המחליף תבניות {{ש}} לתבנית {{-}} \u200f')
        return

def main(args):

    site = pywikibot.Site('he', 'wiktionary')
    global_args  = []

    limit = 0
    article = ''

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
