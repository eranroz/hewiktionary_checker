# -*- coding: utf-8 -*-


import sys
import os
import re
import requests
import argparse
import pywikibot
from pywikibot import pagegenerators
from pywikibot.xmlreader import XmlDump
import hewiktionary
from hewiktionary import PAGE_TEXT_PART

            
def get_dump():
    """
    This function downloads teh latest wiktionary dump
    """

    r = requests.get('http://dumps.wikimedia.org/hewiktionary/latest/hewiktionary-latest-pages-articles.xml.bz2',
                     stream=True)
    if r.status_code != 200:
        print("status code is not 200 but %d" % r.status_code)
        return False

    with open('pages-articles.xml.bz2', 'wb') as dump_fd:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                dump_fd.write(chunk)
    return True





def main(args):
    
    site = pywikibot.Site('en', 'wiktionary')
    global_args  = []

    parser = argparse.ArgumentParser(description="Iterate the English Wiktionary and search for Hebrew pages there that are not"
                                                 "in the Hebrew wiktionary",
                                     epilog="Options include also global pywikibot options and all generators options")
    parser.add_argument("--article", nargs=1, required=False)
    parser.add_argument("--limit", nargs=1, required=False, type=int)
    parser.add_argument("--force_get_dump", required=False, action='store_true')
    parser.add_argument("-always", action='store_false', required=False)
    args, factory_args = parser.parse_known_args(local_args)

    limit = -1
    article = ''
    from_article = ''
    for arg in args:
        print(arg)
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        f = re.compile('^-from-article:(.+)$').match(arg)

        if arg == '--get-dump':
            get_dump()  # download the latest dump if it doesnt exist
        elif m or f:
            if m:
                limit = int(m.group(1))
            if f:
                from_article = f.group(1)
        elif a:
            article = a.group(1)
        else:
            global_args.append(arg)

    local_args = pywikibot.handle_args(global_args)


    if article != u'':
        gen = (pywikibot.Page(site, article) for i in range(0,1))
        gen = pagegenerators.PreloadingGenerator(gen)
    #elif os.path.exists('pages-articles.xml.bz2') and from_article == '':
    #    print('parsing dump')
    #    all_wiktionary = XmlDump('pages-articles.xml.bz2').parse()  # open the dump and parse it.
    #    print('end parsing dump')
        
        # filter only main namespace
    #    all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect, all_wiktionary)
    #    gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
    #    gen = pagegenerators.PreloadingGenerator(gen)
    else:
        #TODO - make sure this case works
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        #gen_factory = pagegenerators.GeneratorFactory(site,'-ns:1')
        #gen_factory.getCombinedGenerator()
        if from_article != '':
            gen =  pagegenerators.AllpagesPageGenerator(start = from_article , site = site)
        else:
            gen =  pagegenerators.AllpagesPageGenerator(start = 'א',site = site)

    hesite = pywikibot.Site('he', 'wiktionary')
    list = []
    #f = open('workfile', 'w')
    for page in gen:
        loop = (loop+1)%100
        if len(page.title())==1 or loop == 0:
            print(page.title())
        if(page.title()=='תתרנית'):
            break
        
        if page.isRedirectPage():
            continue
        if not re.compile("==\s*Hebrew\s*==",re.MULTILINE).search(page.text):
            #print("yidish "+page.title())
            continue
        hepage = pywikibot.Page(hesite,page.title()) 
        if(not hepage.exists()):
            list.append("* {{ת|אנגלית|%s}} [[%s]]"%(page.title(),page.title()))
            #print("* {{ת|אנגלית|%s}}\n"%(page.title()))
            #f.write("* {{ת|אנגלית|%s}}\n"%(page.title()))

    report_page = pywikibot.Page(hesite, 'ויקימילון:תחזוקה/%s' % ('מילים בויקימילון האנגלי שאינם בעברית'))

    report_content = 'סך הכל %s ערכים\n' % str(len(list))

    report_content +=  '\n'.join(['%s' % p for p in list])
    report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
    report_page.text = report_content
    report_page.save("סריקה עם בוט ")

        
            
        
if __name__ == "__main__":
    main(sys.argv)
