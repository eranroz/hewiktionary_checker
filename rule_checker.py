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

WARNING_PAGE_WITH_INVALID_FIELD = 'דפים עם סעיפים שאינם מהרשימה הסגורה'
WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER = 'דפים עם סעיפים שאינם בסדר הנכון'
WARNING_PAGE_WITH_COMMENT = 'דפים בהם לא נמחקה ההערה הדיפולטיבית'
WARNING_PAGE_WITH_TEXT_BEFORE_DEF = 'דפים עם טקסט לפני ההערה הראשונה'
WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM = 'דפים עם גרשיים שאינם ראשי תיבות'
WARNING_PAGE_ACRONYM_NO_GERSHAIM = 'דפים עם ראשי תיבות חסרי גרשיים'
WARNING_PAGE_WITHOUT_GREMMER_BOX = 'דפים חסרי ניתוח דקדוקי'
WARNING_PAGE_WITH_FIRST_LEVEL_TITLE =  'דפים עם כותרת מדרגה ראשונה'
WARNINGS_PAGE_WITHOUT_TITLE = 'דפים ללא כותרת'
WARNING_2nd_LEVEL_TITLE_FROM_LIST = 'דפים עם כותרת סעיף מסדר 2'
WARNING_TITLE_WITH_HTML_TAGS = 'דפים עם תגיות היפר-טקסט בכותרת'
WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE = 'דפים בהם כותרת מסדר 2 ללא ניקוד שונה משם הדף'
WARNING_NO_NIKUD_IN_SEC_TITLE  = 'דפים עם כותרת משנה לא מנוקדת'
WARNING_GERSHAIM_IN_MARE_MAKOM = 'דפים עם ציטוט מהתנך עם גרשיים במראי מקום'
WARNING_ERECH_BET_WRONG = 'ערך משני לא תיקני'
WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE = 'קצרמר בלי תבנית קצרמר'

warning_to_code = {

    WARNING_PAGE_WITH_INVALID_FIELD : "if",
    WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER : "fwo",
    WARNING_PAGE_WITH_COMMENT : "c",
    WARNING_PAGE_WITH_TEXT_BEFORE_DEF : "tbd", 
    WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM : "g",
    WARNING_PAGE_ACRONYM_NO_GERSHAIM : "ang",
    WARNING_PAGE_WITHOUT_GREMMER_BOX : "wgb",
    WARNING_PAGE_WITH_FIRST_LEVEL_TITLE : "flt",
    WARNINGS_PAGE_WITHOUT_TITLE  : "wt",
    WARNING_2nd_LEVEL_TITLE_FROM_LIST  : "2ltfl",
    WARNING_TITLE_WITH_HTML_TAGS  : "ht",
    WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE  : "stdpt",
    WARNING_NO_NIKUD_IN_SEC_TITLE  : "nnst",
    WARNING_GERSHAIM_IN_MARE_MAKOM : "gmm",
    WARNING_ERECH_BET_WRONG : "ebw",
    WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE : "kwkt"
}

warning_to_checker = {}

def fill_warning_to_checker(issues):

    if len(issues) == 0:
        warning_to_checker[WARNING_PAGE_WITH_TEXT_BEFORE_DEF] = checker.TextBeforeDefChecker()
        warning_to_checker[WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM] = checker.NonAcronymWithGereshChecker()
        warning_to_checker[WARNING_PAGE_ACRONYM_NO_GERSHAIM] = checker.AcronymWithoutGereshChecker()
        warning_to_checker[WARNING_PAGE_WITH_FIRST_LEVEL_TITLE] = checker.FirstLevelTitleChecker()
        warning_to_checker[WARNINGS_PAGE_WITHOUT_TITLE] = checker.NoTitleChecker()
        warning_to_checker[WARNING_GERSHAIM_IN_MARE_MAKOM] = checker.GershaimInMareMakom()
    else:
        if WARNING_PAGE_WITH_TEXT_BEFORE_DEF in issues:
            warning_to_checker[WARNING_PAGE_WITH_TEXT_BEFORE_DEF] = checker.TextBeforeDefChecker()
        if WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM in issues:
            warning_to_checker[WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM] = checker.NonAcronymWithGereshChecker()
        if WARNING_PAGE_ACRONYM_NO_GERSHAIM in issues:
            warning_to_checker[WARNING_PAGE_ACRONYM_NO_GERSHAIM] = checker.AcronymWithoutGereshChecker()
        if WARNING_PAGE_WITH_FIRST_LEVEL_TITLE in issues:
            warning_to_checker[WARNING_PAGE_WITH_FIRST_LEVEL_TITLE] = checker.FirstLevelTitleChecker()
        if WARNINGS_PAGE_WITHOUT_TITLE in issues:
            warning_to_checker[WARNINGS_PAGE_WITHOUT_TITLE] = checker.NoTitleChecker()
        if WARNING_GERSHAIM_IN_MARE_MAKOM in issues:
            warning_to_checker[WARNING_GERSHAIM_IN_MARE_MAKOM] = checker.GershaimInMareMakom()

warning_to_item_checker = {}

def fill_warning_to_item_checker(issues):
    if len(issues) == 0:
        warning_to_item_checker[WARNING_2nd_LEVEL_TITLE_FROM_LIST] = checker.SecondLevelTitleField()
        warning_to_item_checker[WARNING_TITLE_WITH_HTML_TAGS] = checker.HtmlTagsInTitle()
        warning_to_item_checker[WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE] = checker.ItemTitleDiffPageTitle()
        warning_to_item_checker[WARNING_NO_NIKUD_IN_SEC_TITLE] = checker.NoNikudInSecTitle()
        warning_to_item_checker[WARNING_PAGE_WITHOUT_GREMMER_BOX] = checker.NoGremmerBoxChecker()
        warning_to_item_checker[WARNING_ERECH_BET_WRONG] = checker.ErechBetWrong()
        warning_to_item_checker[WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER] = checker.InvalidFieldOrderItemChecker()
        warning_to_item_checker[WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE] = checker.KtzarmarWithoutKtzarmarTemplate()
    else:
        if WARNING_2nd_LEVEL_TITLE_FROM_LIST in issues:
            warning_to_item_checker[WARNING_2nd_LEVEL_TITLE_FROM_LIST] = checker.SecondLevelTitleField()
        if WARNING_TITLE_WITH_HTML_TAGS in issues:    
            warning_to_item_checker[WARNING_TITLE_WITH_HTML_TAGS] = checker.HtmlTagsInTitle()
        if WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE in issues:
            warning_to_item_checker[WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE] = checker.ItemTitleDiffPageTitle()
        if WARNING_NO_NIKUD_IN_SEC_TITLE in issues:
            warning_to_item_checker[WARNING_NO_NIKUD_IN_SEC_TITLE] = checker.NoNikudInSecTitle()
        if WARNING_PAGE_WITHOUT_GREMMER_BOX in issues:
            warning_to_item_checker[WARNING_PAGE_WITHOUT_GREMMER_BOX] = checker.NoGremmerBoxChecker()
        if WARNING_ERECH_BET_WRONG in issues:
            warning_to_item_checker[WARNING_ERECH_BET_WRONG] = checker.ErechBetWrong()
        if WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER in issues:
            warning_to_item_checker[WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER] = checker.InvalidFieldOrderItemChecker()
        if WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE in issues:
            warning_to_item_checker[WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE] = checker.KtzarmarWithoutKtzarmarTemplate()
                    
warning_to_field_checker = {}

def fill_warning_to_field_checker(issues):
    if len(issues) == 0:
        warning_to_field_checker[WARNING_PAGE_WITH_INVALID_FIELD] = checker.InvalidFieldItemChecker()
        warning_to_field_checker[WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER] = checker.InvalidFieldOrderItemChecker()
    else:
        if WARNING_PAGE_WITH_INVALID_FIELD in issues:
            warning_to_field_checker[WARNING_PAGE_WITH_INVALID_FIELD] = checker.InvalidFieldItemChecker()
        if WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER in issues:
            warning_to_field_checker[WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER] = checker.InvalidFieldOrderItemChecker()
            
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
        

def check_part(page_title,title,part_text):

    warnings = {}
    
    for key, value in warning_to_item_checker.items():
        v = value.rule_break_found(page_title,title,part_text,PAGE_TEXT_PART.WHOLE_ITEM)
        if v:
            if key not in warnings:
                warnings[key] = []
            warnings[key] += v
            
    fields = re.compile("(^===[^=]+===\s*\n)",re.MULTILINE).findall(part_text)
        
    for f in fields:
        field_title =  re.compile("^===\s*([^=]+)\s*===\s*\n").search(f).group(1).strip()
        
        for key, value in warning_to_field_checker.items():
            v = value.rule_break_found(page_title,'',field_title,PAGE_TEXT_PART.SECTION_TITLE)
            if v:
                if key not in warnings:
                    warnings[key] = []
                warnings[key] += v
                
    return warnings


def check_page(site, page_title, page_text):
    """
    This function checks for violations of the common structure in wiktionary.
    It report the found issues as string
    """
    # pywikibot.output('Analyzing page %s' % page_title)
    #print 'Analyzing page '.encode('utf-8') + (page_title[::-1].encode('utf-8'))

    # warnings is a  dictionary, each key in the dictionary is a string describing the warning.
    # The list of warnings is in the head of this file , they all start with WARNING_
    # the value of each enty is a list of strings , each string is a detailed description of what is wrong
    # if there is no need for detailed description and it is enough to put link to the page, the list will be empty
    warnings = {}

    for key, value in warning_to_checker.items():
        value.reset_state()
    for key, value in warning_to_item_checker.items():
        value.reset_state()
    for key, value in warning_to_field_checker.items():
        value.reset_state()

    if page_title.endswith('(שורש)'):
        return warnings

    for key, value in warning_to_checker.items():
        if value.rule_break_found(page_title,'',page_text):
            warnings[key] = []
         
    parts_gen = split_parts(page_text)

    # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
    parts_gen.__next__()

    for part in parts_gen:
        w = check_part(page_title,re.compile("^==\s*([^=]+)\s*==\s*\n*").search(part[0]).group(1).strip() ,part[1])
        for key in w:
            if key in warnings:
                warnings[key] += w[key]
            else:
                warnings[key] = w[key]
    return warnings


def main(args):
    
    site = pywikibot.Site('he', 'wiktionary')
    global_args  = []

    limit = -1
    article = ''
    issues_to_search = []
    for arg in args:
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        l = re.compile('^-list-issues$').match(arg)
        for key,val in warning_to_code.items():
            if re.compile('^'+val+'$').match(arg):
                issues_to_search += [key]
        if arg == '--get-dump':
            get_dump()  # download the latest dump if it doesnt exist
        elif m:
            limit = int(m.group(1))
        elif a:
            article = a.group(1)
        elif l:
            l = []
            for key,val in warning_to_code.items():
                l+=[key[::-1],val]
                
            sys.exit("List of issues checked, you can run the command with the issue code in order to run only this issue:\n"+"%s (code: %s)\n"*len(warning_to_code) % tuple(l))
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
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary if check_page(site, p.title, p.text))
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        #TODO - make sure this case works
        print('Not using dump - use get_dump to download dump file or run with comment lise arguments')
        #gen_factory = pagegenerators.GeneratorFactory(site,'-ns:1')
        #gen_factory.getCombinedGenerator()
        gen =  pagegenerators.AllpagesPageGenerator(site = site)

    
    # a dictionary where the key is the issue and the value is list of pages violates it
    pages_by_issues = dict()

    fill_warning_to_checker(issues_to_search)
    fill_warning_to_item_checker(issues_to_search)
    fill_warning_to_field_checker(issues_to_search)

    for page in gen:
        if limit == 0:
            break
        elif limit > 0:
            limit = limit -1
        try:
            issues = check_page(site, page.title(), page.get())
            for issue in issues:
                if issue not in pages_by_issues:
                    pages_by_issues[issue] = []
                if issues[issue] == []:
                    pages_by_issues[issue].append('* [[%s]]' % page.title())
                else:
                    for detailed_issue in issues[issue]:
                        pages_by_issues[issue].append( ('* [[%s]] :' % page.title()) + detailed_issue)

        except pywikibot.IsRedirectPage:
            print (page.title().encode('utf-8') + "is redirect page".encode('utf-8'))
            continue
        except pywikibot.NoPage:
            print (page.title().encode('utf-8') + ": NoPage exception".encode('utf-8'))
            continue
    # after going over all pages, report it to a maintenance page so human go over it
    for issue, pages in pages_by_issues.items():
        print ('found issue %s' % issue)
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % issue)
         
        report_content = 'סך הכל %s ערכים\n' % str(len(pages))
        pages = sorted(pages)
        report_content +=  '\n'.join(['%s' % p for p in pages])
        report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"                    
        report_page.text = report_content
        report_page.save("סריקה עם בוט ")
        
    print ('_____________________DONE____________________')
    
print 
if __name__ == "__main__":
    main(sys.argv)
