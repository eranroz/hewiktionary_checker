import re

template_regex='\n*{{ניתוח\s+דקדוקי\s*\|?\s*'
verb_template_regex='\n*{{ניתוח\s+דקדוקי\sלפועל\s*\|?\s*'
 
GERSHAIM_REGEX = re.compile('["״]')

#\[\[קטגוריה:.*(ניבים|ביטויים|פתגמים).*\]\]

KATEGORIA_PITGAMI_REGEX = re.compile(u'\\[\\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:.*(\u05e0\u05d9\u05d1\u05d9\u05dd|\u05d1\u05d9\u05d8\u05d5\u05d9\u05d9\u05dd|\u05e4\u05ea\u05d2\u05de\u05d9\u05dd).*\\]\\]')

ALEF_TO_TAF_REGEX = re.compile('[\u05d0-\u05e0]')

HEBREW_WORD_REGEX = re.compile('[\u0591-\u05f4]+')
GERSHAIM_GERESH_REGEX = re.compile('["״\'\׳]')

lexeme_title_regex = re.compile("^==[^=]+==\s*$",re.MULTILINE)

lexeme_title_regex_grouped = re.compile("^==([^=]+)==\s*$",re.MULTILINE)


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

titles_list  = list(titles_to_order.keys())

class PAGE_TEXT_PART:
    WHOLE_PAGE = 1
    WHOLE_ITEM = 2
    SECTION_TITLE = 3

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
    will create the generator: [('blabla',''),
                               ('== A1 ==','text for defining A1')
                               ('== A2 ==','text for defining A2')]
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
