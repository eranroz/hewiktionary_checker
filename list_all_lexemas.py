#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""
This bot will validate page against list of rules in he-wiktionary

Use get_dump to get the full dump (for developing we are analyzing the full dump)

&params;

Please type "rule_checker.py -help | more" if you can't read the top of the help.

you  can run with 
python rule_checker.py -simulate -log:logrule.log -limit:5

"""

from __future__ import unicode_literals
from __future__ import division
import pywikibot
from pywikibot import pagegenerators
import re
import os
from pywikibot.xmlreader import XmlDump
import requests
import sys
import checker
import hewiktionary

def get_dump():
    """
    This function downloads teh latest wiktionary dump
    """
    # we already have a dump
    #if os.path.exists('pages-articles.xml.bz2'):
    #    return
    # get a new dump
    print('Dump doesnt exist locally - downloading...')
    r = requests.get('http://dumps.wikimedia.org/hewiktionary/latest/hewiktionary-latest-pages-articles.xml.bz2',
                     stream=True)
    with open('pages-articles.xml.bz2', 'wb') as dump_fd:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                dump_fd.write(chunk)
    print('New dump downloaded successfully')

    
def check_page(site, page_title, page_text):
    
    if page_title.endswith('(שורש)'):
        return []

    if re.compile(u'[a-zA-Z"\.]').search(page_title):
        return []

    titles = hewiktionary.lexeme_title_regex_grouped.findall(page_text)
    lexemas = []
    for t in titles:
        lexemas.append(t)


    return lexemas

def main(args):
    
    site = pywikibot.Site('he', 'wiktionary')
    global_args  = []

    limit = -1
    article = ''
    from_article = ''
    letter = None
    for arg in args:
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        f = re.compile('^-from-article:(.+)$').match(arg)
        l = re.compile('^-letter:(.{1})$').match(arg)

        if arg == '--get-dump':
            get_dump()  # download the latest dump if it doesnt exist
        elif m or f:
            if m:
                limit = int(m.group(1))
            if f:
                from_article = f.group(1)
        elif a:
            article = a.group(1)
        elif l:
            letter = l.group(1)
        else:
            global_args.append(arg)

    local_args = pywikibot.handle_args(global_args)

    if article != u'':
        gen = (pywikibot.Page(site, article) for i in range(0,1))
        gen = pagegenerators.PreloadingGenerator(gen)
    elif os.path.exists('pages-articles.xml.bz2') and from_article == '':
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
        if from_article != '':
            gen =  pagegenerators.AllpagesPageGenerator(start = from_article , site = site)
        elif letter:
            gen =  pagegenerators.AllpagesPageGenerator(start = letter , site = site)
        else:
            gen =  pagegenerators.AllpagesPageGenerator(site = site)

    num = 0

    n = 0
    words = []
    for page in gen:
        n = n + 1
        if n%100 == 0:
            print(n)
            print(page.title())
        if limit == 0:
            break
        elif limit > 0:
            limit = limit -1
        if not page.exists() or page.isRedirectPage():
            continue
        if not page.title().startswith(letter):
            break

        for lex in check_page(site, page.title(), page.get()):
            words.append("* [[%s#%s|%s]]" % (page.title(),lex,lex))



    report_content = 'סך הכל %s ערכים\n' % str(len(words))
    #pages = sorted(words)
    report_content +=  '\n'.join(['%s' % p for p in words])
    report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
    report_page = None
    if letter:
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s/%s' % ('רשימת_כל_המילים',letter))
    else:
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % ('רשימת_כל_המילים'))
    report_page.text = report_content
    report_page.save("סריקה עם בוט ")

    print("num is %d"%num)
if __name__ == "__main__":
    main(sys.argv)
