#!/usr/bin/python3
# -*- coding: utf-8 -*-
r"""
This bot will validate page against list of rules in he-wiktionary

Use get_dump to get the full dump (for developing we are analyzing the full dump)

&params;

Please type "rule_checker.py -help | more" if you can't read the top of the help.

you  can run with 
python rule_checker.py -simulate -log:logrule.log -limit:5

"""

import re
import os
import collections
import requests
import sys
import argparse
from argparse import RawTextHelpFormatter
import pywikibot
from pywikibot import pagegenerators
from pywikibot.xmlreader import XmlDump
import hewiktionary
from hewiktionary import PAGE_TEXT_PART
import checker


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
WARNING_SEPARATED_HOMONIMIM = 'הומונימים מופרדים'
WARNING_ = 'בעלי חיים וצמחים ללא תמונות'

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
    WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE : "kwkt",
    WARNING_SEPARATED_HOMONIMIM : "sh"
}

warnings_to_checker2 = {

    WARNING_PAGE_WITH_INVALID_FIELD : checker.InvalidFieldItemChecker(),
    WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER : checker.InvalidFieldOrderItemChecker(),
    WARNING_PAGE_WITH_TEXT_BEFORE_DEF : checker.TextBeforeDefChecker(),
    WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM : checker.NonAcronymWithGereshChecker(),
    WARNING_PAGE_ACRONYM_NO_GERSHAIM : checker.AcronymWithoutGereshChecker(),
    WARNING_PAGE_WITHOUT_GREMMER_BOX : checker.NoGremmerBoxChecker(),
    WARNING_PAGE_WITH_FIRST_LEVEL_TITLE : checker.FirstLevelTitleChecker(),
    WARNINGS_PAGE_WITHOUT_TITLE  : checker.NoTitleChecker(),
    WARNING_2nd_LEVEL_TITLE_FROM_LIST  : checker.SecondLevelTitleField(),
    WARNING_TITLE_WITH_HTML_TAGS  : checker.HtmlTagsInTitle(),
    WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE  : checker.ItemTitleDiffPageTitle(),
    WARNING_NO_NIKUD_IN_SEC_TITLE  : checker.NoNikudInSecTitle(),
    WARNING_GERSHAIM_IN_MARE_MAKOM : checker.GershaimInMareMakom(),
    WARNING_ERECH_BET_WRONG : checker.ErechBetWrong(),
    WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE : checker.KtzarmarWithoutKtzarmarTemplate(),
    WARNING_SEPARATED_HOMONIMIM : checker.HomonimimSeperated()
}

page_warnings = [ WARNING_PAGE_WITH_TEXT_BEFORE_DEF,
                  WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM,
                  WARNING_PAGE_ACRONYM_NO_GERSHAIM,
                  WARNING_PAGE_WITH_FIRST_LEVEL_TITLE,
                  WARNINGS_PAGE_WITHOUT_TITLE,
                  WARNING_GERSHAIM_IN_MARE_MAKOM ]


# In wikimilon we might more than one entry in each dictionary value.
# This is because there might be different words that pronounced differently but are written the same.
# the checkers in this list need to get the parsed pages to the word entry , so not the text of the whole page but
# only on the entry level.

item_warnings = [ WARNING_2nd_LEVEL_TITLE_FROM_LIST,
                  WARNING_TITLE_WITH_HTML_TAGS,
                  WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE,
                  WARNING_NO_NIKUD_IN_SEC_TITLE,
                  WARNING_PAGE_WITHOUT_GREMMER_BOX,
                  WARNING_ERECH_BET_WRONG,
                  WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER,
                  WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE,
                  WARNING_SEPARATED_HOMONIMIM]

field_warnings = [WARNING_PAGE_WITH_INVALID_FIELD,
                  WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER]

warning_to_page_checker  = {}
warning_to_item_checker  = {}
warning_to_field_checker = {}

def check_part(page_title,title,part_text):

    warnings = collections.defaultdict(list)

    for key, value in warning_to_item_checker.items():
        v = value.rule_break_found(page_title,title,part_text,PAGE_TEXT_PART.WHOLE_ITEM)
        if v:
            warnings[key].extend(v)

    fields = re.compile("(^===[^=]+===\s*\n)",re.MULTILINE).findall(part_text)

    for f in fields:
        field_title =  re.compile("^===\s*([^=]+)\s*===\s*\n").search(f).group(1).strip()

        for key, value in warning_to_field_checker.items():
            v = value.rule_break_found(page_title,'',field_title,PAGE_TEXT_PART.SECTION_TITLE)
            if v:
                warnings[key].extend(v)

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
    warnings = collections.defaultdict(list)

    for key, value in warning_to_page_checker.items():
        value.reset_state()
    for key, value in warning_to_item_checker.items():
        value.reset_state()
    for key, value in warning_to_field_checker.items():
        value.reset_state()

    if page_title.endswith('(שורש)'):
        print("got SHORESH!! %s" % page_title)
        return warnings

    for key, value in warning_to_page_checker.items():
        if value.rule_break_found(page_title,'',page_text,PAGE_TEXT_PART.WHOLE_PAGE):
            warnings[key] = []

    parts_gen = hewiktionary.split_parts(page_text)

    # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
    parts_gen.__next__()

    for part in parts_gen:
        w = check_part(page_title,hewiktionary.lexeme_title_regex_grouped.search(part[0]).group(1).strip() ,part[1])
        for key in w:
                warnings[key].extend(w[key])
    return warnings


def main(args):

    local_args = pywikibot.handle_args(args)

    site = pywikibot.Site('he', 'wiktionary')
    genFactory = pagegenerators.GeneratorFactory()
    options = {}

    warnings = [i for key,val in warning_to_code.items() for i in [val,key[::-1]]]

    parser = argparse.ArgumentParser(description=("main checker, add an issue code to check this issue. The list is:\r\n"+"%s (%s)\r\n"*len(warning_to_code) )% tuple(warnings),epilog="Options include also global pywikibot options and all generators options", formatter_class=RawTextHelpFormatter)

    parser.add_argument("--article",nargs=1, required=False)
    parser.add_argument("-always",action='store_false', required=False,default=True)
    parser.add_argument("--issues",nargs='+',required=False,choices=list(warning_to_code.values()),default=list(warning_to_code.values()))

    args, factory_args = parser.parse_known_args(local_args)

    options['always'] = args.always

    for arg in factory_args:
        genFactory.handleArg(arg)

    genFactory.handleArg('-intersect')
    genFactory.handleArg('-titleregexnot:\(שורש\)')

    print(args)
    issues_to_search = [k for k,v in warning_to_code.items() if v in args.issues]

    global warning_to_page_checker
    global warning_to_item_checker
    global warning_to_field_checker

    warning_to_page_checker  = {k:warnings_to_checker2[k] for k in issues_to_search if k in page_warnings}
    warning_to_item_checker  = {k:warnings_to_checker2[k] for k in issues_to_search if k in item_warnings}
    warning_to_field_checker = {k:warnings_to_checker2[k] for k in issues_to_search if k in field_warnings}

    print(warning_to_page_checker)
    print(warning_to_item_checker)
    print(warning_to_field_checker)

    gen = None
    if args.article:
        article = args.article[0]
        gen = pagegenerators.PreloadingGenerator([pywikibot.Page(site, article)])
    elif os.path.exists('hewiktionary-20180320-pages-meta-current.xml.bz2'):
        print('parsing dump')
        all_wiktionary = XmlDump('hewiktionary-20180320-pages-meta-current.xml.bz2').parse()  # open the dump and parse it.
        print('end parsing dump')

        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0' and not page.isredirect and not page.title.endswith('(שורש)'), all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary if check_page(site, p.title, p.text))
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        gen =  pagegenerators.AllpagesPageGenerator(site = site,includeredirects=False)#this is only namespace 0 by default

    gen = genFactory.getCombinedGenerator(gen)#combine with user args
    gen =  pagegenerators.RegexFilterPageGenerator(gen,hewiktionary.ALEF_TO_TAF_REGEX) # scan only hebrew words

    # a dictionary where the key is the issue and the value is list of pages violates it
    pages_by_issues = collections.defaultdict(list)




    for page in gen:
        try:
            issues = check_page(site, page.title(), page.get())
            for issue in issues:
                if issues[issue] == []:
                    pages_by_issues[issue].append('* [[%s]]' % page.title())
                else:
                    for detailed_issue in issues[issue]:
                        #print(detailed_issue)
                        pages_by_issues[issue].append( ('* [[%s]] :' % page.title()) + detailed_issue)

        except pywikibot.IsRedirectPage:
            print ("%s is redirect page" % page.title())
            continue
        except pywikibot.NoPage:
            print ("%s: NoPage exception" % page.title())
            continue
    # after going over all pages, report it to a maintenance page so human go over it
    for issue, pages in pages_by_issues.items():
        print ('found issue %s' % issue)
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % issue)
        report_content = 'סך הכל %s ערכים\n' % str(len(pages))
        pages.sort()
        report_content +=  '\n'.join(['%s' % p for p in pages])
        report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
        report_page.text = report_content
        report_page.save("סריקה עם בוט ")
    print ('_____________________DONE____________________')
if __name__ == "__main__":
    main(sys.argv)
