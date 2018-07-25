#!/usr/bin/python3
# -*- coding: utf-8 -*-
r"""
This bot will validate page against list of rules in he-wiktionary

Use get_dump to get the full dump (for developing we are analyzing the full dump)

&params;

"""

import os
import sys
import collections
import argparse
from enum import Enum
import pywikibot

from pywikibot import pagegenerators
from pywikibot.xmlreader import XmlDump
import hewiktionary
from hewiktionary import PAGE_TEXT_PART
import checker

class HeWikiWarning(Enum):

    WARNING_PAGE_WITH_INVALID_FIELD = 1
    WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER = 2
    WARNING_PAGE_WITH_COMMENT = 3
    WARNING_PAGE_WITH_TEXT_BEFORE_DEF = 4
    WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM = 5
    WARNING_PAGE_ACRONYM_NO_GERSHAIM = 6
    WARNING_PAGE_WITHOUT_GREMMER_BOX = 7
    WARNING_PAGE_WITH_FIRST_LEVEL_TITLE = 8
    WARNINGS_PAGE_WITHOUT_TITLE = 9
    WARNING_2nd_LEVEL_TITLE_FROM_LIST  = 10
    WARNING_TITLE_WITH_HTML_TAGS  = 11
    WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE = 12
    WARNING_NO_NIKUD_IN_SEC_TITLE = 13
    WARNING_GERSHAIM_IN_MARE_MAKOM  = 14
    WARNING_ERECH_BET_WRONG  = 15
    WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE = 16
    WARNING_SEPARATED_HOMONIMIM  = 17

warning_to_str = {
    HeWikiWarning.WARNING_PAGE_WITH_INVALID_FIELD : 'דפים עם סעיפים שאינם מהרשימה הסגורה',
    HeWikiWarning.WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER : 'דפים עם סעיפים שאינם בסדר הנכון',
    HeWikiWarning.WARNING_PAGE_WITH_COMMENT : 'דפים בהם לא נמחקה ההערה הדיפולטיבית',
    HeWikiWarning.WARNING_PAGE_WITH_TEXT_BEFORE_DEF : 'דפים עם טקסט לפני ההערה הראשונה',
    HeWikiWarning.WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM : 'דפים עם גרשיים שאינם ראשי תיבות',
    HeWikiWarning.WARNING_PAGE_ACRONYM_NO_GERSHAIM : 'דפים עם ראשי תיבות חסרי גרשיים',
    HeWikiWarning.WARNING_PAGE_WITHOUT_GREMMER_BOX : 'דפים חסרי ניתוח דקדוקי',
    HeWikiWarning.WARNING_PAGE_WITH_FIRST_LEVEL_TITLE :  'דפים עם כותרת מדרגה ראשונה',
    HeWikiWarning.WARNINGS_PAGE_WITHOUT_TITLE : 'דפים ללא כותרת',
    HeWikiWarning.WARNING_2nd_LEVEL_TITLE_FROM_LIST : 'דפים עם כותרת סעיף מסדר 2',
    HeWikiWarning.WARNING_TITLE_WITH_HTML_TAGS : 'דפים עם תגיות היפר-טקסט בכותרת',
    HeWikiWarning.WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE : 'דפים בהם כותרת מסדר 2 ללא ניקוד שונה משם הדף',
    HeWikiWarning.WARNING_NO_NIKUD_IN_SEC_TITLE  : 'דפים עם כותרת משנה לא מנוקדת',
    HeWikiWarning.WARNING_GERSHAIM_IN_MARE_MAKOM : 'דפים עם ציטוט מהתנך עם גרשיים במראי מקום',
    HeWikiWarning.WARNING_ERECH_BET_WRONG : 'ערך משני לא תיקני',
    HeWikiWarning.WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE : 'קצרמר בלי תבנית קצרמר',
    HeWikiWarning.WARNING_SEPARATED_HOMONIMIM : 'הומונימים מופרדים',
}



warning_to_class = {

    HeWikiWarning.WARNING_PAGE_WITH_INVALID_FIELD : checker.InvalidFieldItemChecker,
    HeWikiWarning.WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER : checker.InvalidFieldOrderItemChecker,
    HeWikiWarning.WARNING_PAGE_WITH_TEXT_BEFORE_DEF : checker.TextBeforeDefChecker,
    HeWikiWarning.WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM : checker.NonAcronymWithGereshChecker,
    HeWikiWarning.WARNING_PAGE_ACRONYM_NO_GERSHAIM : checker.AcronymWithoutGereshChecker,
    HeWikiWarning.WARNING_PAGE_WITHOUT_GREMMER_BOX : checker.NoGremmerBoxChecker,
    HeWikiWarning.WARNING_PAGE_WITH_FIRST_LEVEL_TITLE : checker.FirstLevelTitleChecker,
    HeWikiWarning.WARNINGS_PAGE_WITHOUT_TITLE  : checker.NoTitleChecker,
    HeWikiWarning.WARNING_2nd_LEVEL_TITLE_FROM_LIST  : checker.SecondLevelTitleField,
    HeWikiWarning.WARNING_TITLE_WITH_HTML_TAGS  : checker.HtmlTagsInTitle,
    HeWikiWarning.WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE  : checker.ItemTitleDiffPageTitle,
    HeWikiWarning.WARNING_NO_NIKUD_IN_SEC_TITLE  : checker.NoNikudInSecTitle,
    HeWikiWarning.WARNING_GERSHAIM_IN_MARE_MAKOM : checker.GershaimInMareMakom,
    HeWikiWarning.WARNING_ERECH_BET_WRONG : checker.ErechBetWrong,
    HeWikiWarning.WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE : checker.KtzarmarWithoutKtzarmarTemplate,
    HeWikiWarning.WARNING_SEPARATED_HOMONIMIM : checker.HomonimimSeperated
}

page_warnings = [ HeWikiWarning.WARNING_PAGE_WITH_TEXT_BEFORE_DEF,
                  HeWikiWarning.WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM,
                  HeWikiWarning.WARNING_PAGE_ACRONYM_NO_GERSHAIM,
                  HeWikiWarning.WARNING_PAGE_WITH_FIRST_LEVEL_TITLE,
                  HeWikiWarning.WARNINGS_PAGE_WITHOUT_TITLE,
                  HeWikiWarning.WARNING_GERSHAIM_IN_MARE_MAKOM ]


# In wikimilon we might more than one entry in each dictionary value.
# This is because there might be different words that pronounced differently but are written the same.
# the checkers in this list need to get the parsed pages to the word entry , so not the text of the whole page but
# only on the entry level.
item_warnings = [ HeWikiWarning.WARNING_2nd_LEVEL_TITLE_FROM_LIST,
                  HeWikiWarning.WARNING_TITLE_WITH_HTML_TAGS,
                  HeWikiWarning.WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE,
                  HeWikiWarning.WARNING_NO_NIKUD_IN_SEC_TITLE,
                  HeWikiWarning.WARNING_PAGE_WITHOUT_GREMMER_BOX,
                  HeWikiWarning.WARNING_ERECH_BET_WRONG,
                  HeWikiWarning.WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER,
                  HeWikiWarning.WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE,
                  HeWikiWarning.WARNING_SEPARATED_HOMONIMIM,
                  HeWikiWarning.WARNING_PAGE_WITH_INVALID_FIELD]


def check_part(page_title,title,part_text, warning_to_item_checker):

    warnings = collections.defaultdict(list)

    for warning, clss in warning_to_item_checker.items():
        v = clss().rule_break_found(page_title,title,part_text,PAGE_TEXT_PART.WHOLE_ITEM)
        if v:
            warnings[warning].extend(v)

    return warnings


def check_page(page_title, page_text, warning_to_page_checker, warning_to_item_checker):
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


    for warning, clss in warning_to_page_checker.items():
        if clss().rule_break_found(page_title,'',page_text,PAGE_TEXT_PART.WHOLE_PAGE):
            warnings[warning] = []

    parts_gen = hewiktionary.split_parts(page_text)

    # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
    parts_gen.__next__()

    for part in parts_gen:
        part_title = hewiktionary.lexeme_title_regex_grouped.search(part[0]).group(1).strip()
        w = check_part(page_title,part_title ,part[1], warning_to_item_checker)
        for key in w:
                warnings[key].extend(w[key])
    return warnings


def main(args):

    local_args = pywikibot.handle_args(args)

    site = pywikibot.Site('he', 'wiktionary')
    genFactory = pagegenerators.GeneratorFactory()
    options = {}

    warnings = sorted([(key.value, val[::-1]) for key,val in warning_to_str.items()])

    warning_list_str = "\r\n".join(["%s. %s" % t for t in warnings])

    parser = argparse.ArgumentParser(description="Add an issue number to check this issue. The list is:\r\n" + warning_list_str,
                                     epilog="Options include also global pywikibot options and all generators options",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--article",nargs=1, required=False)
    parser.add_argument("-always",action='store_false', required=False,default=True)
    parser.add_argument("--issues",nargs='+',required=True,choices=[str(w.value) for w in warning_to_str.keys()])

    args, factory_args = parser.parse_known_args(local_args)

    options['always'] = args.always

    for arg in factory_args:
        genFactory.handleArg(arg)

    genFactory.handleArg('-intersect')
    genFactory.handleArg('-titleregexnot:\(שורש\)')

    issues_to_search = [HeWikiWarning(int(k)) for k in args.issues]

    warning_to_page_checker  = {k: warning_to_class[k] for k in issues_to_search if k in page_warnings}
    warning_to_item_checker  = {k: warning_to_class[k] for k in issues_to_search if k in item_warnings}

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
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary if check_page(p.title, p.text, warning_to_page_checker, warning_to_item_checker))
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        gen =  pagegenerators.AllpagesPageGenerator(site = site,includeredirects=False)#this is only namespace 0 by default

    gen = genFactory.getCombinedGenerator(gen)#combine with user args
    gen =  pagegenerators.RegexFilterPageGenerator(gen,hewiktionary.ALEF_TO_TAF_REGEX) # scan only hebrew words

    # a dictionary where the key is the issue and the value is list of pages violates it
    pages_by_issues = collections.defaultdict(list)

    print(warning_to_item_checker)
    for page in gen:
        try:
            issues = check_page(page.title(), page.get(), warning_to_page_checker, warning_to_item_checker)
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
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % warning_to_str[issue])
        report_content = 'סך הכל %s ערכים\n' % str(len(pages))
        pages.sort()
        report_content +=  '\n'.join(['%s' % p for p in pages])
        report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
        report_page.text = report_content
        report_page.save("סריקה עם בוט ")
    print ('_____________________DONE____________________')
if __name__ == "__main__":
    main(sys.argv)
