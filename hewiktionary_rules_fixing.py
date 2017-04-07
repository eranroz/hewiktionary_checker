#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
iterate all Hebrew wiktionary fixing bots
"""

import pywikibot
from pywikibot import pagegenerators
import re
import os
from pywikibot.xmlreader import XmlDump
import sys
import fixers

fix_bad_order_fields = "fix fields (sections) in wrong order (sort according to the right order)"
replace_link_shoresh_to_template_shoresh = "replace a link to a shoresh (root) page to the teplate {שורש|XXX}"
replace_template_shin_to_makaf = "replace templare {ש} to template {-}"
section_title_replace = "replace section titles - for example דעת פרשנים -> פרנשים מפרשים"
section_title_to_third = "move section title from 2nd level (==) to 3rd (===)"

    
#fixers_to_code = {
#    fix_bad_order_fields : "fbof"
#    replace_link_shoresh_to_template_shoresh : "rlsts"
#    replace_template_shin_to_makaf : "rtsm"
#    section_title_replace : "str"
#    section_tite_to_third : "stt"
#}

fixers_to_code = {
    "fbof" : fix_bad_order_fields,
    "rlsts" : replace_link_shoresh_to_template_shoresh,
    "rtsm" : replace_template_shin_to_makaf,
    "str" : section_title_replace,
    "stt" : section_title_to_third
}

fixers_to_tahzuka_file = {
    "fbof" : "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_בסדר_הנכון",
    "str" : "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה",
    "stt" : "ויקימילון:תחזוקה/דפים_עם_כותרת_סעיף_מסדר_2"
}


def fill_all_pages_fixers(issues):
    f = {}    
    if len(issues) == 0:
        f["rlsts"] = fixers.LinkShoreshToTemplateShoresh()
        f["rtsm"] = fixers.ShinToMakafBot()
    else:
        if "rlsts" in issues:
            f["rlsts"] =  fixers.LinkShoreshToTemplateShoresh()
        if "rtsm" in isuess:
            f["rtsm"] = fixers.ShinToMakafBot()

    return f


def fill_listed_pages_fixers(issues,article = ''):
    f = {}    
    if len(issues) == 0:
        f["stt"] = fixers.SectionTitleLvl2ndTo3rdFixer(article)
    else:
        if "stt" in issues:
            f["stt"] = fixers.SectionTitleLvl2ndTo3rdFixer(article)
    return f


class AllPagesFixersBot(pywikibot.CurrentPageBot):
    def __init__(self,f, **kwargs):
        super(AllPagesFixersBot,self).__init__(**kwargs)
        self._l = f
        print(self._l)
    def treat_page(self):
        for key,val in self._l.items():
            new_text = val.fix(self.current_page.title(), self.current_page.text)
            self.put_current(new_text,summey = val._comment)
    

def main(args):

    site = pywikibot.Site('he', 'wiktionary')
    global_args  = []

    limit = 0
    article = ''

    all_pages_fixers = []
    listed_pages_fixers = []

    print(args)
    for arg in args:
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        l = re.compile('^-list-issues$').match(arg)
        for key,val in fixers_to_code.items():
            if re.compile('^'+key+'$').match(arg):
                if not fixers_to_tahzuka_file[key]:
                    all_pages_fixers += [key]
                else:
                    listed_pages_fixers += [key]
    

        if arg == '--get-dump':
            get_dump()  # download the latest dump if it doesnt exist
        elif m:
            limit = int(m.group(1))
        elif a:
            article = a.group(1)
        elif l:
            l = []

            for key,val in fixers_to_code.items():
                l+=[val,key]
            sys.exit("List of issues that bots can fix, you can run the command with the issue code(s) in order to run fixes only these issue(s):\n"+"%s (code: %s)\n"*len(fixers_to_code) % tuple(l))

        else:
            global_args.append(arg)

    local_args = pywikibot.handle_args(global_args)

    if not listed_pages_fixers or all_pages_fixers:
        f = fill_all_pages_fixers(all_pages_fixers)
        if article != '':
            print(article[::-1])
            gen = [pywikibot.Page(site, article)]
            gen = pagegenerators.PreloadingGenerator(gen)

        elif os.path.exists('pages-articles.xml.bz2'):
            print("1")
            all_wiktionary = XmlDump('pages-articles.xml.bz2').parse()  # open the dump and parse it.
            all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect, all_wiktionary)
            gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
            gen = pagegenerators.PreloadingGenerator(gen)

        else:
            print("2")
            gen =  pagegenerators.AllpagesPageGenerator(site = site,total = limit)

        bot = AllPagesFixersBot(f,generator = gen,site = site)
        bot.run()
    if not all_pages_fixers or listed_pages_fixers:

        fixers = fill_listed_pages_fixers(listed_pages_fixers,article)        
        for key,bot in fixers.items():
            bot.run()


        
if __name__ == "__main__":
    main(sys.argv)
