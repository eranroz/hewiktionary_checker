#!/usr/bin/python3
# -*- coding: utf-8 -*-
r"""
This bot will validate page against list of rules in he-wiktionary

Use get_dump to get the full dump (for developing we are analyzing the full dump)

&params;

"""

import sys

if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    raise Exception("Must be using >= Python 3.6, current %d.%d" %(sys.version_info[0], sys.version_info[1]))

import os
import re
import collections
import argparse
import enum
import pywikibot

from pywikibot import pagegenerators
from pywikibot.xmlreader import XmlDump
import hewiktionary
from hewiktionary import PAGE_TEXT_PART
import checker


class HeWikiWarning(enum.Enum):
    WARNING_TERGUM_WITH_REF = enum.auto()
    WARNING_PAGE_WITH_INVALID_FIELD = enum.auto()
    WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER = enum.auto()
    WARNING_PAGE_WITH_TEXT_BEFORE_DEF = enum.auto()
    WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM = enum.auto()
    WARNING_PAGE_ACRONYM_NO_GERSHAIM = enum.auto()
    WARNING_PAGE_WITHOUT_GREMMER_BOX = enum.auto()
    WARNING_PAGE_WITH_FIRST_LEVEL_TITLE = enum.auto()
    WARNINGS_PAGE_WITHOUT_TITLE = enum.auto()
    WARNING_2nd_LEVEL_TITLE_FROM_LIST = enum.auto()
    WARNING_TITLE_WITH_HTML_TAGS = enum.auto()
    WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE = enum.auto()
    WARNING_NO_NIKUD_IN_SEC_TITLE = enum.auto()
    WARNING_GERSHAIM_IN_MARE_MAKOM = enum.auto()
    WARNING_ERECH_BET_WRONG = enum.auto()
    WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE = enum.auto()
    WARNING_SEPARATED_HOMONIMIM = enum.auto()


warning_to_str = {
    HeWikiWarning.WARNING_TERGUM_WITH_REF: 'דפים עם תרגום עם רפרפנס לפירושים',
    HeWikiWarning.WARNING_PAGE_WITH_INVALID_FIELD: 'דפים עם סעיפים שאינם מהרשימה הסגורה',
    HeWikiWarning.WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER: 'דפים עם סעיפים שאינם בסדר הנכון',
    HeWikiWarning.WARNING_PAGE_WITH_TEXT_BEFORE_DEF: 'דפים עם טקסט לפני ההערה הראשונה',
    HeWikiWarning.WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM: 'דפים עם גרשיים שאינם ראשי תיבות',
    HeWikiWarning.WARNING_PAGE_ACRONYM_NO_GERSHAIM: 'דפים עם ראשי תיבות חסרי גרשיים',
    HeWikiWarning.WARNING_PAGE_WITHOUT_GREMMER_BOX: 'דפים חסרי ניתוח דקדוקי',
    HeWikiWarning.WARNING_PAGE_WITH_FIRST_LEVEL_TITLE: 'דפים עם כותרת מדרגה ראשונה',
    HeWikiWarning.WARNINGS_PAGE_WITHOUT_TITLE: 'דפים ללא כותרת',
    HeWikiWarning.WARNING_2nd_LEVEL_TITLE_FROM_LIST: 'דפים עם כותרת סעיף מסדר 2',
    HeWikiWarning.WARNING_TITLE_WITH_HTML_TAGS: 'דפים עם תגיות היפר-טקסט בכותרת',
    HeWikiWarning.WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE: 'דפים בהם כותרת מסדר 2 ללא ניקוד שונה משם הדף',
    HeWikiWarning.WARNING_NO_NIKUD_IN_SEC_TITLE: 'דפים עם כותרת משנה לא מנוקדת',
    HeWikiWarning.WARNING_GERSHAIM_IN_MARE_MAKOM: 'דפים עם ציטוט מהתנך עם גרשיים במראי מקום',
    HeWikiWarning.WARNING_ERECH_BET_WRONG: 'ערך משני לא תיקני',
    HeWikiWarning.WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE: 'קצרמר בלי תבנית קצרמר',
    HeWikiWarning.WARNING_SEPARATED_HOMONIMIM: 'הומונימים מופרדים',
}

warning_to_class = {
    HeWikiWarning.WARNING_TERGUM_WITH_REF: checker.TergumWithReference,
    HeWikiWarning.WARNING_PAGE_WITH_INVALID_FIELD: checker.InvalidFieldItemChecker,
    HeWikiWarning.WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER: checker.InvalidFieldOrderItemChecker,
    HeWikiWarning.WARNING_PAGE_WITH_TEXT_BEFORE_DEF: checker.TextBeforeDefChecker,
    HeWikiWarning.WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM: checker.NonAcronymWithGereshChecker,
    HeWikiWarning.WARNING_PAGE_ACRONYM_NO_GERSHAIM: checker.AcronymWithoutGereshChecker,
    HeWikiWarning.WARNING_PAGE_WITHOUT_GREMMER_BOX: checker.NoGremmerBoxChecker,
    HeWikiWarning.WARNING_PAGE_WITH_FIRST_LEVEL_TITLE: checker.FirstLevelTitleChecker,
    HeWikiWarning.WARNINGS_PAGE_WITHOUT_TITLE: checker.NoTitleChecker,
    HeWikiWarning.WARNING_2nd_LEVEL_TITLE_FROM_LIST: checker.SecondLevelTitleField,
    HeWikiWarning.WARNING_TITLE_WITH_HTML_TAGS: checker.HtmlTagsInTitle,
    HeWikiWarning.WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE: checker.ItemTitleDiffPageTitle,
    HeWikiWarning.WARNING_NO_NIKUD_IN_SEC_TITLE: checker.NoNikudInSecTitle,
    HeWikiWarning.WARNING_GERSHAIM_IN_MARE_MAKOM: checker.GershaimInMareMakom,
    HeWikiWarning.WARNING_ERECH_BET_WRONG: checker.ErechBetWrong,
    HeWikiWarning.WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE: checker.KtzarmarWithoutKtzarmarTemplate,
    HeWikiWarning.WARNING_SEPARATED_HOMONIMIM: checker.HomonimimSeperated
}

page_warnings = [HeWikiWarning.WARNING_PAGE_WITH_TEXT_BEFORE_DEF,
                 HeWikiWarning.WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM,
                 HeWikiWarning.WARNING_PAGE_ACRONYM_NO_GERSHAIM,
                 HeWikiWarning.WARNING_PAGE_WITH_FIRST_LEVEL_TITLE,
                 HeWikiWarning.WARNINGS_PAGE_WITHOUT_TITLE,
                 HeWikiWarning.WARNING_GERSHAIM_IN_MARE_MAKOM,
                 HeWikiWarning.WARNING_SEPARATED_HOMONIMIM]

# In wikimilon we might more than one entry in each dictionary value.
# This is because there might be different words that pronounced differently but are written the same.
# the checkers in this list need to get the parsed pages to the word entry , so not the text of the whole page but
# only on the entry level.
item_warnings = [HeWikiWarning.WARNING_2nd_LEVEL_TITLE_FROM_LIST,
                 HeWikiWarning.WARNING_TITLE_WITH_HTML_TAGS,
                 HeWikiWarning.WARNING_SEC_TITLE_DIFFERENT_THAN_PAGE_TITLE,
                 HeWikiWarning.WARNING_NO_NIKUD_IN_SEC_TITLE,
                 HeWikiWarning.WARNING_PAGE_WITHOUT_GREMMER_BOX,
                 HeWikiWarning.WARNING_ERECH_BET_WRONG,
                 HeWikiWarning.WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER,
                 HeWikiWarning.WARNING_KTZARMAR_WITHOUT_KTZARMAR_TEMPLATE,
                 HeWikiWarning.WARNING_SEPARATED_HOMONIMIM,
                 HeWikiWarning.WARNING_TERGUM_WITH_REF,
                 HeWikiWarning.WARNING_PAGE_WITH_INVALID_FIELD]


def check_part(page_title, title, part_text, warning_to_item_checker):
    warnings = collections.defaultdict(list)

    for warning, clss in warning_to_item_checker.items():
        v = clss.rule_break_found(page_title, title, part_text, PAGE_TEXT_PART.WHOLE_ITEM)
        if v:
            warnings[warning].extend(v)

    return warnings


def check_page(page_title, page_text, warning_to_page_checker, warning_to_item_checker):
    """
    This function checks for violations of the common structure in wiktionary.
    It report the found issues as string
    """

    # warnings is a  dictionary, each key in the dictionary is a string describing the warning.
    # The list of warnings is in the head of this file , they all start with WARNING_
    # the value of each enty is a list of strings , each string is a detailed description of what is wrong
    # if there is no need for detailed description and it is enough to put link to the page, the list will be empty
    warnings = collections.defaultdict(list)

    for warning, clss in warning_to_page_checker.items():
        if clss.rule_break_found(page_title, '', page_text, PAGE_TEXT_PART.WHOLE_PAGE):
            warnings[warning] = []

    parts_gen = hewiktionary.split_parts(page_text)

    # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
    parts_gen.__next__()

    for part in parts_gen:
        part_title = hewiktionary.lexeme_title_regex_grouped.search(part.title).group(1).strip()
        part_warnings = check_part(page_title, part_title, part.content, warning_to_item_checker)
        for w in part_warnings:
            warnings[w].extend(part_warnings[w])
    return warnings


def main(args):
    local_args = pywikibot.handle_args(args)

    site = pywikibot.Site('he', 'wiktionary')
    genFactory = pagegenerators.GeneratorFactory()


    warnings = sorted([(key.value, val[::-1]) for key, val in warning_to_str.items()])

    warning_list_str = "\r\n".join(["%s. %s" % t for t in warnings])

    parser = argparse.ArgumentParser(
        description="Add an issue number to check this issue. The list is:\r\n" + warning_list_str +"\r\n"
        "if no issue is chosen then all issues are assumed and checked",
        epilog="Options include also global pywikibot options and all generators options",
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--force-get-dump", required=False, default=False,action="store_true")
    parser.add_argument("--article", required=False)
    parser.add_argument("--issues", nargs='+', required=False, type=int, choices=[w.value for w in warning_to_str])

    args, factory_args = parser.parse_known_args(local_args)
    print(args)

    if args.force_get_dump or not os.path.exists(hewiktionary.LATEST_DUMP):
        res = hewiktionary.download_dump()
        if not res:
            print("could not download dump")
            if args.force_get_dump:
                exit(-1)

    for arg in factory_args:
        genFactory.handleArg(arg)

    genFactory.handleArg('-intersect')
    genFactory.handleArg('-titleregexnot:\(שורש\)')

    #the list of checks that the user wanted
    if not args.issues:
        issues_to_search = warning_to_str.keys()
    else:
        issues_to_search = [HeWikiWarning(int(k)) for k in args.issues]

    # each check (issue) is either a page issue or an item issue (or both)
    # so we have to dict that maps and issue enum to a checker instant
    warning_to_page_checker = {}
    warning_to_item_checker = {}
    for issue in issues_to_search:
        checker_instans = warning_to_class[issue]()
        if issue in page_warnings:
            warning_to_page_checker[issue] = checker_instans
        if issue in item_warnings:
            warning_to_item_checker[issue] = checker_instans

    if args.article:
        gen = pagegenerators.PreloadingGenerator([pywikibot.Page(site, args.article)])
    # running initial check from local dump improves runtime dramatically
    elif os.path.exists(hewiktionary.LATEST_DUMP):
        print('parsing dump')
        all_wiktionary = XmlDump(hewiktionary.LATEST_DUMP).parse()  # open the dump and parse it.
        print('end parsing dump')

        # filter only main namespace
        all_wiktionary = filter(lambda page: page.ns == '0'
                                             and not page.isredirect
                                             and not page.title.endswith('(שורש)')
                                             and re.search(hewiktionary.ALEF_TO_TAF_REGEX,page.title)
                                             and not re.search(r'[a-zA-Z]',page.title), all_wiktionary)
        gen = (pywikibot.Page(site, p.title) for p in all_wiktionary if
               check_page(p.title, p.text, warning_to_page_checker, warning_to_item_checker))
        gen = pagegenerators.PreloadingGenerator(gen)
    else:
        gen = pagegenerators.AllpagesPageGenerator(site=site,
                                                   includeredirects=False)  # this is only namespace 0 by default

    gen = genFactory.getCombinedGenerator(gen)  # combine with user args
    gen = pagegenerators.RegexFilterPageGenerator(gen, hewiktionary.ALEF_TO_TAF_REGEX)  # scan only hebrew words
    gen = pagegenerators.RegexFilterPageGenerator(gen, re.compile(r'[a-zA-Z]'),quantifier='none')

    # a dictionary where the key is the issue and the value is list of pages violates it
    pages_by_issues = collections.defaultdict(list)

    for page in gen:
        try:
            issues = check_page(page.title(), page.get(), warning_to_page_checker, warning_to_item_checker)
            for issue in issues:
                if issues[issue] == []:
                    pages_by_issues[issue].append('* [[%s]]' % page.title())
                else:
                    for detailed_issue in issues[issue]:
                        # print(detailed_issue)
                        pages_by_issues[issue].append('* [[%s]] : %s' % (page.title(), detailed_issue))

        except pywikibot.IsRedirectPage:
            print("%s is redirect page" % page.title())
            continue
        except pywikibot.NoPage:
            print("%s: NoPage exception" % page.title())
            continue
    # after going over all pages, report it to a maintenance page so human go over it
    for issue, pages in pages_by_issues.items():
        print('found issue %s' % issue)
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % warning_to_str[issue])
        report_content = 'סך הכל %s ערכים\n' % str(len(pages))
        pages.sort()
        report_content += '\n'.join(['%s' % p for p in pages])
        report_content += "\n\n[[קטגוריה: ויקימילון - תחזוקה]]"
        report_page.text = report_content
        report_page.save("סריקה עם בוט ")
    print('_____________________DONE____________________')


if __name__ == "__main__":
    main(sys.argv)
