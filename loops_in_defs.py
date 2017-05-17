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
import hewiktionary_constants
from hewiktionary_constants import PAGE_TEXT_PART

fsas = ''            
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



def split_parts(page_text):

    '''
    sparates the page text to parts according to second level title and also seperates each title to 
    from it's part.
    For example:
   
    "
    blabla
    == A1 ==
    text for defining A1

    == A2 ==
    text for defining A2
    "
    will create the generator: [('blabla','',unknown),
                               ('== A1 ==','text for defining A1',<type>)
                               ('== A2 ==','text for defining A2',<type>)]
    '''
    #for multile mode , the '^, $' will match both 
    #the start/end of the string and the start/end of a line.

    # the paranthess in the regex will add the delimiter 
    # see http://stackoverflow.com/questions/2136556/in-python-how-do-i-split-a-string-and-keep-the-separators

    #matches the level2 title, e.g '== ילד =='
    parts = re.compile("(^==[^=]+==\s*$)",re.MULTILINE).split(page_text)

    yield (parts.pop(0),'')
    
    for i in range(0,len(parts),2):        
        title = parts[i]
        part = parts[i+1]
        yield (title,part)
        



def check_loop(orig_page,dest_page,orig_parag):

    global fsas
    site = pywikibot.Site('he', 'wiktionary')
    dest_page_p = pywikibot.Page(site,dest_page)

    try:
        dest_page_text = dest_page_p.get()
    except pywikibot.IsRedirectPage:
        return 
            
    #print(dest_page)
    parts = re.compile("(^==[^=]+==\s*\n)",re.MULTILINE).split(dest_page_text)
    for part in parts:
        sections = re.compile("(^===[^=]+===\s*\n)",re.MULTILINE).split(part)
        hagdara_sec = sections.pop(0)
        for defi in re.compile("^#([^:].*)$",re.MULTILINE).findall(hagdara_sec):
            words = re.compile("[ ,\.]+").split(defi.strip())
            for word in words:
                word = word.strip();
                word_n = re.compile('[^\[\]]*[\[\]]{2}([^\[\]]*)[\[\]]{2}').match(word)
                if word_n:
                    word = word_n.group(1)
                    w = re.compile('^([^|]*)\|').search(word)
                    if w:
                        word = w.group(1)
                        
                if word == orig_page:
                    fsas.write("* found loop page1=[[%s]] page2=[[%s]]\n"%(orig_page,dest_page))
                    fsas.write("# page1 [[%s]]:\n%s\n"%(orig_page,re.sub(dest_page,'<b>'+dest_page+'</b>',orig_parag)))
                    fsas.write("# page2 [[%s]]:\n%s\n"%(dest_page,re.sub(orig_page,'<b>'+orig_page+'</b>',defi)))
                    
                    
def check_part(page_title,title,part_text):
    
    sections = re.compile("(^===[^=]+===\s*\n)",re.MULTILINE).split(part_text)
    
    site = pywikibot.Site('he', 'wiktionary')

    hibur_cat = u'קטגוריה:מילות חיבור'
    yahas_cat = u'קטגוריה:מילות יחס'
    hibur_cat_p = pywikibot.Page(site,hibur_cat)
    yahas_cat_p = pywikibot.Page(site,yahas_cat)

    hagdara_sec = sections.pop(0)
    
    for defi in re.compile("^#([^:].*)$",re.MULTILINE).findall(hagdara_sec):
        words = re.compile("[ ,\.]+").split(defi.strip())
        #print(words)
        for word in words:
            word = word.strip();
            word_n = re.compile('[^\[\]]*[\[\]]{2}([^\[\]]*)[\[\]]{2}').match(word)
            if word_n:
                #print(page_title)
                #print(word)
                word = word_n.group(1)
                #print(word)
                w = re.compile('^([^|]*)\|').search(word)
                if w:
                    word = w.group(1)
                #print(word)
            word = word.strip();
            #print(word)
            if re.compile('[\[\]\{\}><]').search(word) or len(word)==0 or word==page_title:
                #print("bad word:%s in page %s" % (word,page_title))
                continue
            try:
                page = pywikibot.Page(site,word)
            except UnicodeDecodeError:
                print("UnicodeDecodeError in page %s: %s"%(word, e.strerror))
                print(word)
                continue
                
            if page.exists():
                if hibur_cat_p not in page.categories() and yahas_cat_p not in page.categories():
                      #print(word)
                      check_loop(page_title,word,defi)
    
    
def check_page(site, page_title, page_text):
    """
    This function checks for violations of the common structure in wiktionary.
    It report the found issues as string
    """
    
    if page_title.endswith('(שורש)'):
        return 

    if re.compile(u'[a-zA-Z"\.]').search(page_title):
        return []
       
    parts_gen = split_parts(page_text)

    # the first part is either an empty string or a string before the first definition e.g. {{לשכתוב}}
    parts_gen.__next__()

    for part in parts_gen:
        w = check_part(page_title,re.compile("^==\s*([^=]+)\s*==\s*\n*").search(part[0]).group(1).strip() ,part[1])
        
        
        
        


def main(args):

    global fsas
    site = pywikibot.Site('he', 'wiktionary')
    global_args  = []

    limit = -1
    article = ''
    from_article = ''
    for arg in args:
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
    elif os.path.exists('pages-articles.xml.bz2'):
        print('parsing dump')
        all_wiktionary = XmlDump('pages-articles.xml.bz2').parse()  # open the dump and parse it.
        print('end parsing dump')
        
        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect, all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary)
        gen = pagegenerators.PreloadingGenerator(gen)
        if from_article != '':
            print(from_article)
            for p in gen:
                if p.title() == from_article:
                    break
                
    else:
        #TODO - make sure this case works
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        #gen_factory = pagegenerators.GeneratorFactory(site,'-ns:1')
        #gen_factory.getCombinedGenerator()
        if from_article != '':
            gen =  pagegenerators.AllpagesPageGenerator(start = from_article , site = site)
        else:
            gen =  pagegenerators.AllpagesPageGenerator(site = site)

    fsas = open('file.txt', 'w',500)

    for page in gen:
        #print(page.title())
        if limit == 0:
            break
        elif limit > 0:
            limit = limit -1
        
        check_page(site, page.title(), page.get())
    fsas.close()
if __name__ == "__main__":
    main(sys.argv)
