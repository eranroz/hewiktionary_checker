#!/usr/bin/python3
# -*- coding: utf-8 -*-
r"""
This bot sorts the fields (sections) of a definition according to the predetermined order decided by the hebrew wiktionary community
The order is represeted by the constant titles_to_order defined in hewiktionary_constants.py
It goes over the list of links in  "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_בסדר_הנכון"

"""

import pywikibot
from pywikibot import pagegenerators
import re
import sys
import hewiktionary
from hewiktionary import titles_to_order
import argparse

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

    for idx,field in enumerate(fields):
        section_title =  re.compile("===\s*([^=]+)\s*===\s*\n").search(field)
        if section_title:
            section_title = section_title.group(1).strip()

            if section_title in titles_to_order:
                fields_from_known_list_to_sort += [[fields[idx],fields[idx+1],section_title]]#add the section title, the section text and the the title itsel (for sorting)
            else:
                fields_not_from_known_list[idx//2]  = [fields[idx],fields[idx+1]]

    fields_from_known_list_to_sort.sort(key=cmp_to_key(cmp))# It modifies the list in-place (and returns None to avoid confusion)
    final = []

    fiter = iter(fields_from_known_list_to_sort)
    #print(fields_not_from_known_list)
    for idx in range(len(fields)//2):
        #print("======= %d ==========" % idx)
        if idx in fields_not_from_known_list:
            #print("======= DCIT ==========")
            #print(fields_not_from_known_list[idx])
            final.append(fields_not_from_known_list[idx][0])
            final.append(fields_not_from_known_list[idx][1])
        else:
            #print("======= triple ==========")
            triple = next(fiter)

            #print(triple)
            final.append(triple[0])
            final.append(triple[1])
        if(not final[-1].endswith("\n")):
            final[-1] +=  "\n"

    final = [fields[0]]+final

    print(final)
    final = ''.join(final)
    for cat in categories:
        final += cat+'\n'
    return final

def fix_page(page_title, page_text):

    # page_parts is a list like[ 'text before first', '== title nikud1 ==','def1', '== title nikud2 == ', 'def2']
    page_parts = split_parts(page_text)

    # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
    final = [page_parts.__next__()]

    for part in page_parts:
        if not re.compile("(^==[^=]+==\s*\n)",re.MULTILINE).match(part):
            final.append(fix_part2(part))
        else:
            final.append(part)

    return ''.join(final)

def main(args):

    local_args = pywikibot.handle_args(args)

    site = pywikibot.Site('he', 'wiktionary')

    parser = argparse.ArgumentParser(description="reorder subsection titles according to predefined order")
    parser.add_argument("--article",nargs=1, required=False)
    parser.add_argument("-always",action='store_false', required=False)
    #parser.add_argument("-limit",nargs=1, required=False)

    args, factory_args = parser.parse_known_args(local_args)


    print(args)

    if args.article:
        article = args.article[0]
        page = pywikibot.Page(site, article)
        page.text = fix_page(page.title(),page.text)

        if page.text:
            page.save("בוט שמסדר סעיפים מדרגה 3 בסדר הנכון")

    else:
        maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_בסדר_הנכון")

        for page in maintain_page.linkedPages():
            print(page.title()[::-1])
            page.text = fix_page(page.title(),page.text)
            if page.text:
                page.save("בוט שמסדר סעיפים מדרגה 3 בסדר הנכון")
            else:
                print('problem with page - skipping')

    print('_____________________DONE____________________')

if __name__ == "__main__":
    main(sys.argv)
