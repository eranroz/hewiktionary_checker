#!/usr/bin/python3
# -*- coding: utf-8 -*-
r"""
According to Ariel1024 :

החלפה של: {{ש}}{{ש}}{{ש}}{{ש}} וכולי בסוף ערכים לתבנית {{-}}

see:

https://he.wiktionary.org/w/index.php?title=%D7%A9%D7%99%D7%97%D7%AA_%D7%9E%D7%A9%D7%AA%D7%9E%D7%A9:Ariel1024&oldid=255275#.D7.94.D7.99
"""
import sys
import argparse
import pywikibot
import re
import os
from pywikibot import pagegenerators
from pywikibot.xmlreader import XmlDump
import hewiktionary

class ShinToMakafBot(pywikibot.CurrentPageBot):

    def treat_page(self):

        s = re.compile(r'שורש',re.MULTILINE).search(self.current_page.title())
        if s is not None:
            return 

        s = re.compile(r'.*#הפניה.*',re.MULTILINE).search(self.current_page.text)
        if s is not None:
            return 

        new_page_text = re.sub(r'({{ש}}\n?){2,}','{{-}}\n',self.current_page.text,re.MULTILINE)
        if new_page_text != self.current_page.text:
            print('saving page %s' % self.current_page.title())
            self.put_current(new_page_text, summary = u'בוט המחליף תבניות {{ש}} לתבנית {{-}} \u200f')
        return

def main(args):

    local_args = pywikibot.handle_args(args)
    site = pywikibot.Site('he', 'wiktionary')
    genFactory = pagegenerators.GeneratorFactory()
    options = {}

    parser = argparse.ArgumentParser(description="a bot that replaces {{ש}} with {{-}}",
                                     epilog="Options include also global pywikibot options and all generators options",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--article", required=False)
    parser.add_argument("--limit", required=False,type=int,default=0)
    parser.add_argument("-always",action='store_false', required=False,default=True)

    args, factory_args = parser.parse_known_args(local_args)

    options['always'] = args.always

    for arg in factory_args:
        genFactory.handleArg(arg)

    genFactory.handleArg('-intersect')

    gen = None

    if args.article:
        print(args.article[::-1])
        gen = [pywikibot.Page(site, args.article)]
        gen = pagegenerators.PreloadingGenerator(gen)
    elif os.path.exists(hewiktionary.LATEST_DUMP):
        print('parsing dump')
        all_wiktionary = XmlDump(hewiktionary.LATEST_DUMP).parse()  # open the dump and parse it.
        print('end parsing dump')
        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect and page.title.endswith('(שורש)'), all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
        gen = pagegenerators.PreloadingGenerator(gen)

    else:
        if args.limit:
            gen = pagegenerators.AllpagesPageGenerator(site = site,includeredirects=False, total = args.limit)
        else:
            gen = pagegenerators.AllpagesPageGenerator(site = site)

    bot = ShinToMakafBot(generator = gen,site = site, always = args.always)
    bot.run()

if __name__ == "__main__":
    main(sys.argv)
