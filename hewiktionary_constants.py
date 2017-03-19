import re

template_regex='\n*{{ניתוח\s+דקדוקי\s*\|?\s*'
verb_template_regex='\n*{{ניתוח\s+דקדוקי\sלפועל\s*\|?\s*'
 
GERSHAIM_REGEX = re.compile('["״]')
KATEGORIA_PITGAMI_REGEX = re.compile(u'\\[\\[\u05e7\u05d8\u05d2\u05d5\u05e8\u05d9\u05d4:.*(\u05e0\u05d9\u05d1\u05d9\u05dd|\u05d1\u05d9\u05d8\u05d5\u05d9\u05d9\u05dd|\u05e4\u05ea\u05d2\u05de\u05d9\u05dd).*\\]\\]')

GERSHAIM_GERESH_REGEX = re.compile('["״\'\׳]')

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
