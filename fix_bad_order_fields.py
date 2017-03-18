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

GIZRON = "גיזרון"
MAKOR = "מקור"
PARSHANIM = "פרשנים מפרשים"
TSERUFIM = "צירופים"
NIGZAROT = "נגזרות"
NIRDAFOT = "מילים נרדפות"
KROVIM = "ביטויים קרובים"
NIGUDIM = "ניגודים"
TERGUM = "תרגום"
MEIDA = "מידע נוסף"
REOGAM = "ראו גם"
KISHURIM = "קישורים חיצוניים"
SIMUCHIN = "סימוכין"
SHULAIM = "הערות שוליים"


titles_to_order = {

    GIZRON : 0,
    MAKOR  : 0,
    PARSHANIM : 1,  
    TSERUFIM :  2,
    NIGZAROT : 3,
    NIRDAFOT : 4,
    KROVIM  : 4,
    NIGUDIM : 5,
    TERGUM : 6,
    MEIDA : 7,
    REOGAM : 8,
    KISHURIM : 9,
    SIMUCHIN : 10,
    SHULAIM : 11,
}

def split_parts(page_text):
    
    #ascii =  "".join((c if ord(c) < 128 else '_' for c in page_text))

    #for multile mode , the '^' in the begginnig of the regex will match both the start of the string and the start of a new line.
    # the paranthess in the regex will add the delimiter 
    # see http://stackoverflow.com/questions/2136556/in-python-how-do-i-split-a-string-and-keep-the-separators

    parts = re.compile("(^==[^=]+==\s*\n)",re.MULTILINE).split(page_text)

    for part in parts:
        yield part


def cmp(m1,m2):
    return titles_to_order[m1[2]]-titles_to_order[m2[2]]

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0  
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
    

def fix_part2(part_text):
    
    original = part_text
    if re.compile('[^\n]===[^=\n\r\v\f]+===',re.MULTILINE).search(part_text):
        print('ERROR: a 3rd level title that do not start with new line')
        print(re.compile('[^\n]===[^=\n]+===',re.MULTILINE).findall(part_text))
        return original

    if re.compile('\n===[^=\n\r\v\f]+===[ \t]*[^\n]',re.MULTILINE).search(part_text):
        print('ERROR: a 3rd level title that do not end')
        return original

    categories = re.findall("\[\[קטגוריה:[^\]]+\]\]",part_text,re.MULTILINE)

    part_text = re.sub("\[\[קטגוריה:[^\]]+\]\]",'',part_text)
    part_text = re.sub("\n{3,}",'\n\n',part_text)

    fields_from_known_list_to_sort = []
    fields_not_from_known_list  = {}
    fields = re.compile("(===[^=\n\r\v\f]+===\s*\n)",re.MULTILINE).split(part_text)

    if len(fields) < 2:
        print('PROBLEM 1: seems like the are no sections in this part: num of parts: '+str(len(fields)))
        return original 

    if fields[0].startswith('='):
        print('PROBLEM 2: '+fields[0])
        return None
 
   # print('================== PART BEFORE FIX =================')
    #print part_text
    
    tit = 1
    i = 1
    j = 0
    while i < len(fields)-1:
        # tit is one for the section title
        if tit == 1: 
            section_title =  re.compile("===\s*([^=]+)\s*===\s*\n").search(fields[i]).group(1)
            section_title = section_title.strip()

            if section_title in titles_to_order:
                fields_from_known_list_to_sort += [[fields[i],fields[i+1],section_title]]#add the section title, the section text and the the title itsel (for sorting) 
            else:
                fields_not_from_known_list[j]  = [fields[i],fields[i+1]]
            j += 1
        tit = 1 - tit
        i += 1
        
    fields_from_known_list_to_sort.sort(key=cmp_to_key(cmp))# It modifies the list in-place (and returns None to avoid confusion)
    
    final = [None] * (len(fields)-1)
    
    for key in list(fields_not_from_known_list.keys()):
        f = fields_not_from_known_list[key] 
        final[2*key] = f[0]
        final[2*key+1] = f[1]

    i = 0
    for f in fields_from_known_list_to_sort:
        while final[i] != None:
            i += 1;
        final[i] = f[0]
        final[i+1] = f[1]
   
    final = [fields[0]]+final

    final = ''.join(final)
    if not final.endswith('\n'):
        print('add newline to final')
        final += '\n'
    for cat in categories:
        final += cat+'\n'
    
    return final
    
    

def fix_page(page_title, page_text):

    final = []

    # page_parts is a list like[ 'text before first', '== title nikud1 ==','def1', '== title nikud2 == ', 'def2']
    page_parts = split_parts(page_text)
    
    def_list = list(page_parts)
    # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
    final += [def_list.pop(0)]
    
    defs_num = len(def_list) #sum(1 for i in page_parts)
    
    if defs_num == 0:
        print('page' + page_title +'has no defenitions')
        return
        
    elif defs_num % 2 != 0:
         print('page' + page_title +' is mal formed ')
         return
    
    tit = 1
    
    for part in def_list:
        
        #print part
        if tit == 0: #tit 0 : definition
            #if verbose:
            p = fix_part2(part)
            if not p:
                print('problem with this page')
                return None
    
            final += [p]
        else:
            print('=== PART ==='+part)
            if not part.startswith('\n') and not final[-1].endswith('\n') and not len(final) == 1:
                final += ['\n'+part]
            else:
                final += [part]
        tit = 1 - tit


    return ''.join(final)

def main(args):

    site = pywikibot.Site('he', 'wiktionary')
    global_args  = []

    limit = -1
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
        page = pywikibot.Page(site, article)
        t= page.text
        page.text = fix_page(page.title(),page.text)

        if page.text:
            if (t == page.text):
                print('ARE EQUAL!')
            page.save("בוט שמסדר סעיפים מדרגה 3 בסדר הנכון")

    else:
        gen_factory = pagegenerators.GeneratorFactory()
        site = pywikibot.Site('he', 'wiktionary')    
        maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_בסדר_הנכון")

        l = 0
        for page in maintain_page.linkedPages():
            if(l == limit):
                break
            print(page.title()[::-1])
            page.text = fix_page(page.title(),page.text)
            if page.text:
                page.save("בוט שמסדר סעיפים מדרגה 3 בסדר הנכון")
            else:
                print('problem with page - skipping')
            l += 1
            
    
    print('_____________________DONE____________________')
    

if __name__ == "__main__":
    main(sys.argv)
