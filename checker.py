import hewiktionary_constants
import pywikibot
import re
import pywikibot.textlib


class Checker:
    def __init__(self):
        self._site = pywikibot.Site('he', 'wiktionary')
        return
    def rule_break_found(self,page_title,text_title,text):
        """check given text and return "true" (problem found) or "false" (no problem)"""
        raise NotImplementedError('Method %s.rule_break_found() not implemented.'
                                  % self.__class__.__name__)
    def reset_state(self):
        return

class FirstLevelTitleChecker(Checker):
    def rule_break_found(self,page_title,text_title,text):
        # look for any string '= x =' where x either:
        # starts with '=' but doesn't ends with '='
        # strats with anyhting but '=' and ends with '='
        # has no '=' at all
        if re.compile('^=([^=]+.*|=[^=]*)=\s*$',re.MULTILINE).match(text):
            return True
        return False

class TextBeforeDefChecker(Checker):
    def rule_break_found(self,page_title,text_title,text):
        before = re.compile("^(.*)==[^=]+==\s*",re.MULTILINE).search(text)
        if not before:
            print("TextBeforeDefChecker: not before:")
            return False
        text_before = before.group(1)
        if text_before != u'' and not re.compile("^\n*\{?").match(text_before):
            return True
        print("TextBeforeDefChecker: before: -%s-" % (text_before))
        return False
    
class NoTitleChecker(Checker):
    def rule_break_found(self,page_title,text_title,text):
        text_before = re.compile("^==[^=]+==\s*$",re.MULTILINE).search(text)
        if not text_before:
            return True
        return False
        
class NoGremmerBoxChecker(Checker):
    def rule_break_found(self,page_title,text_title,text):
        
        if hewiktionary_constants.KATEGORIA_PITGAMI_REGEX.search(text) or text.endswith("'"):
            return False
        elif re.compile(hewiktionary_constants.template_regex+'\n').match(text):
            return False
        elif re.search(hewiktionary_constants.verb_template_regex,text):
            return False
        elif re.search(hewiktionary_constants.GERSHAIM_REGEX,text_title):
            return False
        elif re.search('[a-zA-Z]',text_title):
            return False
        else:
            return True
        
class AcronymWithoutGereshChecker(Checker):
    def rule_break_found(self,page_title,text_title,text):
        try:
            text_categories = [cat.title(withNamespace=False) for cat in pywikibot.textlib.getCategoryLinks(text, self._site)]
        except pywikibot.InvalidTitle:
            print("AcronymWithoutGereshChecker: invalid category in page %s" % (page_title))
            return False
        if not hewiktionary_constants.GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' in text_categories):
            return True
        return False
    
class NonAcronymWithGereshChecker(Checker):
    def rule_break_found(self,page_title,text_title,text):
        try:
            text_categories = [cat.title(withNamespace=False) for cat in pywikibot.textlib.getCategoryLinks(text, self._site)]
        except pywikibot.InvalidTitle:
            print("NonAcronymWithGereshChecker: invalid category in page %s" % (page_title))
            return False
        if hewiktionary_constants.GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' not in text_categories):
            return True
        return False

#classes that check by definition
            
class SecondLevelTitleField(Checker):
    def rule_break_found(self,page_title,text_title,text):
        if text_title in hewiktionary_constants.titles_list:
            return ['סעיף עם כתורת מסדר 2: %s' % text_title]
        return ''
    
class HtmlTagsInTitle(Checker):
        def rule_break_found(self,page_title,text_title,text):
            if '<' in text_title:
                return ['%s' % text_title]
            return False
        
class ItemTitleDiffPageTitle(Checker):
        def rule_break_found(self,page_title,text_title,text):
            real_title = re.compile('([^\{\}\)\(]*)(\{\{.*\}\})?(\(.*\))?').search(text_title).group(1).strip()
            no_nikud_title = re.sub('[\u0591-\u05c7\u200f]','',real_title)
            no_nikud_title = re.sub('[״]','"',no_nikud_title)
            if no_nikud_title != page_title:
                return ['כותרת משנה ללא ניקוד: %s' % no_nikud_title ]
            return ''

class NoNikudInSecTitle(Checker):
        def rule_break_found(self,page_title,text_title,text):
            words_in_title =  re.compile('[\s]+').split(text_title)
            for word in words_in_title:
                nikud_num  = len(re.findall(u'[\u05b0-\u05bc]',word))
                he_num = len(re.findall(u'[\u0591-\u05f4]',word))
                other_num = len(re.findall(u'[\'|}{)("״]',word))
                if len(word)> 2 and  other_num == 0 and  he_num > 0 and nikud_num == 0:
                    return ['כותרת: %s' % text_title ]

#classes that check by field:

class InvalidFieldItemChecker(Checker):
    def rule_break_found(self,page_title,text_title,text):
            if text not in hewiktionary_constants.titles_to_order:
                return ['סעיף שאינו מהרשימה: %s' % text]

class InvalidFieldOrderItemChecker(Checker):
    def __init__(self):
        super(InvalidFieldOrderItemChecker,self).__init__()
        self._state = -1
        self._last_match = ''
        
        
    def reset_state(self):
        self._state = -1
        self._last_match = ''
        
        
    def rule_break_found(self,page_title,text_title,text):
        if text not in hewiktionary_constants.titles_to_order:
            return []
        new_state = hewiktionary_constants.titles_to_order[text]
        if new_state < self._state:
            return ['סעיף %s צריך להיות לפני סעיף %s' % (text,self._last_match) ]
        else:
            self._state = new_state
            self._last_match = text

