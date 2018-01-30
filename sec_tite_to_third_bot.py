#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators

import re
import sys
import hewiktionary
import argparse

class SectionTitleLvl2ndTo3rdBot(pywikibot.CurrentPageBot):

    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        new_page_text = self.current_page.text

        part_titles = hewiktionary.lexeme_title_regex.findall(self.current_page.text)

        for part_title in part_titles:
            title = hewiktionary.lexeme_title_regex_grouped.search(part_title).group(1).strip()
            if title in hewiktionary.titles_list:
                new_page_text = re.sub('==\s*'+title+'\s*==','==='+title+'===',new_page_text,re.MULTILINE)

        if new_page_text != self.current_page.text:
            print('saving %s' % self.current_page.title())
            self.put_current(new_page_text, summary = u'בוט המחליף כותרות סעיפים מסדר 2 לסדר 3')

def main(args):

    local_args = pywikibot.handle_args(args)
    site = pywikibot.Site('he', 'wiktionary')
    maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_כותרת_סעיף_מסדר_2")

    genFactory = pagegenerators.GeneratorFactory()
    options = {}

    parser = argparse.ArgumentParser(description="move subsections titles from headin level 2 to heading level 3",epilog="Options include also global pywikibot options and all generators options")
    parser.add_argument("--article",nargs=1, required=False)
    parser.add_argument("-always",action='store_false', required=False)
    args, factory_args = parser.parse_known_args(local_args)

    options['always'] = args.always

    for arg in factory_args:
        genFactory.handleArg(arg)

    genFactory.handleArg('-intersect')

    if args.article:
        article = args.article[0]
        print(article[::-1])#the terminal shows hebrew left to write :(
        gen = [pywikibot.Page(site, article)]
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        gen = pagegenerators.LinkedPageGenerator(maintain_page, content = True)

    gen = genFactory.getCombinedGenerator(gen)

    bot = SectionTitleLvl2ndTo3rdBot(generator = gen,site = site)
    bot.run()

    print('_____________________DONE____________________')


if __name__ == "__main__":
    main(sys.argv)
