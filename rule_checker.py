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
import pywikibot
from pywikibot import pagegenerators
import re
import pywikibot.textlib
import os
from pywikibot.xmlreader import XmlDump
import requests
import sys



GERSHAIM_REGEX = re.compile('["״]')
KATEGORIA_PITGAMI_REGEX = re.compile(u'\\[\\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:.*(\u05e0\u05d9\u05d1\u05d9\u05dd|\u05d1\u05d9\u05d8\u05d5\u05d9\u05d9\u05dd|\u05e4\u05ea\u05d2\u05de\u05d9\u05dd).*\\]\\]')
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

WARNING_PAGE_WITH_INVALID_FIELD = 'דפים עם סעיפים שאינם מהרשימה הסגורה'
WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER = 'דפים עם סעיפים שאינם בסדר הנכון'
WARNING_PAGE_WITH_COMMENT = 'דפים בהם לא נמחקה ההערה הדיפולטיבית'
WARNING_PAGE_WITH_TEXT_BEFORE_DEF = 'דפים עם טקסט לפני ההערה הראשונה'
WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM = 'דפים עם גרשיים שאינם ראשי תיבות'
WARNING_PAGE_ACRONYM_NO_GERSHAIM = 'דפים עם ראשי תיבות חסרי גרשיים'
WARNING_PAGE_WITHOUT_GREMMER_BOX = 'דפים חסרי ניתוח דקדוקי'
WARNING_PAGE_WITH_FIRST_LEVEL_TITLE =  'דפים עם כותרת מדרגה ראשונה'
WARNINGS_PAGE_WITHOUT_TITLE = 'דפים ללא כותרת'

#ordered_secondary_titles = {
#"גיזרון/מקור",
#"פרשנים מפרשים",
#"צירופים",
#"נגזרות",
#"מילים נרדפות/ביטויים קרובים",
#"ניגודים",
#"תרגום",
#"מידע נוסף",
#"ראו גם",
#קישורים חיצוניים",
#סימוכין",
#הערות שוליים"
#

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

    yield (parts.pop(0),'',PAGE_PART_TYPE.UNKNOWN)


    template_regex='\n*{{ניתוח\s+דקדוקי\s*\|?\s*'
    verb_template_regex='\n*{{ניתוח\s+דקדוקי\sלפועל\s*\|?\s*'
    p = re.compile( template_regex+'\n')

    for i in range(0,len(parts),2):
        
        title = parts[i]
        part = parts[i+1]

        if KATEGORIA_PITGAMI_REGEX.search(part) or part.endswith("'"):
            yield (title,part,PAGE_PART_TYPE.PHRASE)
        elif p.match(part):
            yield (title,part,PAGE_PART_TYPE.NOUN)
        elif re.search(verb_template_regex,part):
            yield (title,part,PAGE_PART_TYPE.VERB)
        elif re.search(GERSHAIM_REGEX,title):
            yield (title,part,PAGE_PART_TYPE.RASHEY_TEVOT)
        elif re.search('[a-zA-Z]',title):
            yield (title,part,PAGE_PART_TYPE.NON_HEBREW)
        else:
            print part
            print [title]
            print title
            yield (title,part,PAGE_PART_TYPE.UNKNOWN)

class PAGE_PART_TYPE:
    NOUN = 1
    VERB = 2
    PHRASE = 3
    UNKNOWN = 4
    RASHEY_TEVOT = 5
    NON_HEBREW = 6
    


def check_noun(page_text):
    warnings = {}
    #print('NOT IMPLEMENTED')
    return warnings


def check_verb(part_type):
    warnings = {}
    #print('NOT IMPLEMENTED')
    return warnings


def check_phrase(part_type):
    warnings = {}
    #print('NOT IMPLEMENTED')
    return warnings


def common_checks(part_type):
    warnings = {}
    #print('NOT IMPLEMENTED')
    return warnings



def check_part(part_text, part_type):
    #print '=========start check_part ==========='

    fields = re.compile("(^===[^=]+===\s*\n)",re.MULTILINE).split(part_text)
    state = -1
    tit = 0
    warnings = {}
    last_match = ''
    for f in fields:
        if tit == 1:
            match =  re.compile("^===\s*([^=]+)\s*===\s*\n").search(f).group(1)
            match = match.strip()

            if not titles_to_order.has_key(match):
                if WARNING_PAGE_WITH_INVALID_FIELD not in warnings:
                    warnings[WARNING_PAGE_WITH_INVALID_FIELD] = []
                warnings[WARNING_PAGE_WITH_INVALID_FIELD] += ['סעיף שאינו מהרשימה: %s' % match]
            else:
                new_state = titles_to_order[match]
                if new_state < state:
                    if WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER not in warnings:
                        warnings[WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER] = []
                    warnings[WARNING_PAGE_WITH_FIELDS_IN_WRONG_ORDER] += ['סעיף %s צריך להיות לפני סעיף %s' % (match,last_match) ]
                else:
                    state = new_state
                    last_match = match
        tit = 1 - tit

    if part_type == PAGE_PART_TYPE.NOUN:
        warnings.update(check_noun(part_type))
    elif part_type == PAGE_PART_TYPE.VERB:
        warnings.update(check_verb(part_type))
    elif part_type == PAGE_PART_TYPE.PHRASE:
        warnings.update(check_phrase(part_type))

    #warnings += common_checks(part_text)
    #if warnings:
    #    print warnings
    #    print '=========end check_part ==========='
    return warnings


def update_dict_lists(dict1,dict2):
    for key in dict2:
        if key in dict1:
            dict1[key] += dict2[key]
        else:
            dict1[key] = dict2[key]


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

    if page_title.endswith('(שורש)'):
        return warnings

    # look for any string '= x =' where x either:
    # starts with '=' but doesn't ends with '='
    # strats with anyhting but '=' and ends with '='
    # has no '=' at all
    if re.compile('^=([^=]+.*|=[^=]*)=\s*$',re.MULTILINE).match(page_text):
        warnings[WARNING_PAGE_WITH_FIRST_LEVEL_TITLE] = []
        print 'page with first level title' + page_title 

    
    parts_gen = split_parts(page_text)

    # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
    first = parts_gen.next()

    if re.compile("<!--יש למחוק את המיותר בסוף מילוי התבנית, כמו את שורה זו למשל-->").match(first[0]):
        warnings[WARNING_PAGE_WITH_COMMENT] = []

    elif first[0] != u'' and not re.compile("^\n*\{?").match(first[0]):
        warnings[WARNING_PAGE_WITH_TEXT_BEFORE_DEF] = []
    
    defs_num = 0

    for part in parts_gen:
        if part[2] ==  PAGE_PART_TYPE.UNKNOWN:
            warnings[WARNING_PAGE_WITHOUT_GREMMER_BOX] = []
        w = check_part(part[1], part[2])
        for key in w:
            if key in warnings:
                warnings[key] += w[key]
            else:
                warnings[key] = w[key]
        defs_num = defs_num + 1

    if defs_num == 0:
        #print 'page' + page_title +'has no defenitions'
        warnings[WARNINGS_PAGE_WITHOUT_TITLE] = []
        
    text_categories = [cat.title(withNamespace=False) for cat in pywikibot.textlib.getCategoryLinks(page_text, site)]

    if GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' not in text_categories):
        warnings[WARNING_NON_ACRONYM_PAGE_WITH_GERSHAIM] = []  # FIX: warning for gershaim which aren't in category
    elif not GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' in text_categories):
        warnings[WARNING_PAGE_ACRONYM_NO_GERSHAIM]  = []# FIX: warning for rashi taivut without gershaim

    return warnings


def main(args):
    
    site = pywikibot.Site('he', 'wiktionary')

    print args
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
        
    if article != '':
        gen = (pywikibot.Page(site, article.decode('utf-8')) for i in range(0,1))
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

    print '#@#@#@#@#@#@##@#@#@#@#@#@#@#@#@##@#@#@#@#@#@#@#@#@##@#@#@#@#@#@#@#@#@##@#@#@'

    # a dictionary where the key is the issue and the value is list of pages violates it
    pages_by_issues = dict()
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
                    #print 'ADDING %s to pages by issues' % page.title()
                    pages_by_issues[issue].append('* [[%s]]' % page.title())
                else:
                    for detailed_issue in issues[issue]:
                        #print 'ADDING detailed issue %s to pages by issues' % detailed_issue
                        pages_by_issues[issue].append( ('* [[%s]] :' % page.title()) + detailed_issue)

        except pywikibot.IsRedirectPage:
            print page.title().encode('utf-8') + "is redirect page".encode('utf-8')
            continue
        except pywikibot.NoPage:
            print page.title().encode('utf-8') + ": NoPage exception".encode('utf-8')
            continue
    # after going over all pages, report it to a maintenance page so human go over it
    for issue, pages in pages_by_issues.items():
        print 'found issue %s' % issue
        report_page = pywikibot.Page(site, 'ויקימילון:תחזוקה/%s' % issue)
         
        report_content = 'סך הכל %s ערכים\n' % str(len(pages))
        #report_content +=  '\n'.join(['* [[%s]]' % p for p in pages])
        report_content +=  '\n'.join(['%s' % p for p in pages])

        f = open('%s.txt' % issue ,'w')
        f.write(report_content.encode('utf-8'))
        #print report_content
                    
        report_page.text = report_content
        report_page.save("סריקה עם בוט ")


    
    print '_____________________DONE____________________'
    

print 
if __name__ == "__main__":
    main(sys.argv)
