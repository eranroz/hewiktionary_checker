#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
According to Ariel1024 :

החלפה של "[[קטגוריה:פעל (שורש)]]" > "{{שורש|פעל}}" ("פעל" לדוגמה)

see:

https://he.wiktionary.org/w/index.php?title=%D7%A9%D7%99%D7%97%D7%AA_%D7%9E%D7%A9%D7%AA%D7%9E%D7%A9:Ariel1024&oldid=255275#.D7.94.D7.99

"""
import sys
import os
import pywikibot
from pywikibot import pagegenerators
import pywikibot.textlib
from pywikibot.xmlreader import XmlDump


class LinkShoreshToTemplateShoresh(pywikibot.CurrentPageBot):
    def __init__(self, **kwargs):
        super(LinkShoreshToTemplateShoresh,self).__init__(**kwargs)
        self._shoresh = u'שורש'
        self._kategoria = u'קטגוריה'
        
    def treat_page(self):
        if not self.current_page.title().endswith('(שורש)'):
            return 
        site = pywikibot.Site('he', 'wiktionary')
        for b in self.current_page.revisions():
            if b['user'] == 'Dafna3.bot' and b['comment'] == 'בוט המחליף לינק לשורשר בתבנית שורש':
                print(self.current_page.title())
                try:
                    site.editpage(self.current_page,summary=u'ביטול העריכה "בוט המחליף לינק שורש בתבנתי שורש"',bot=True,undo=b['revid'])
                except Exception as e:
                     print("exsception while site.editpage" + str(e))

def main(args):

    pywikibot.handle_args(args)
    site = pywikibot.Site('he', 'wiktionary')

    print(__file__+" סריקה עם בוט")


    if os.path.exists('pages-articles.xml.bz2'):
        print('parsing dump')
        all_wiktionary = XmlDump('pages-articles.xml.bz2').parse()  # open the dump and parse it.
        print('end parsing dump')        
        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect and page.title.endswith('(שורש)'), all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
        gen = pagegenerators.PreloadingGenerator(gen)

    else:
        #TODO - make sure this case works
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        gen =  pagegenerators.AllpagesPageGenerator(site = site)

    bot = LinkShoreshToTemplateShoresh(generator = gen,site = site)
    bot.run()

if __name__ == "__main__":
    main(sys.argv)
