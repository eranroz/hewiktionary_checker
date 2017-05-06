import hewiktionary_constants
from hewiktionary_constants import PAGE_TEXT_PART
import pywikibot
import re
import pywikibot.textlib

class Checker:
    def __init__(self):
        self._site = pywikibot.Site('he', 'wiktionary')
        return
    def rule_break_found(self,page_title,text_title,text,text_portion):
        """check given text and return "true" (problem found) or "false" (no problem)"""
        raise NotImplementedError('Method %s.rule_break_found() not implemented.'
                                  % self.__class__.__name__)
    def reset_state(self):
        return

class FirstLevelTitleChecker(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
        # look for any string '= x =' where x either:
        # starts with '=' but doesn't ends with '='
        # strats with anyhting but '=' and ends with '='
        # has no '=' at all
        if re.compile('^=([^=]+.*|=[^=]*)=\s*$',re.MULTILINE).match(text):
            return True
        return False

class TextBeforeDefChecker(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
        before = re.compile("^([^=]*)==[^=]+==\s*",re.MULTILINE).search(text)
        if not before:
            return False
        text_before = before.group(1)
        if text_before != u'' and not re.compile("^\n*\{?").match(text_before):
            return True
        return False
    
class NoTitleChecker(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
        text_before = re.compile("^==[^=]+==\s*$",re.MULTILINE).search(text)
        if not text_before:
            return True
        return False
        
class NoGremmerBoxChecker(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
        
        if hewiktionary_constants.KATEGORIA_PITGAMI_REGEX.search(text) or text.endswith("'"):
            return ''
        elif re.compile(hewiktionary_constants.template_regex+'\n').match(text):
            return ''
        elif re.search(hewiktionary_constants.verb_template_regex,text):
            return ''
        elif re.search(hewiktionary_constants.GERSHAIM_REGEX,text_title):
            return ''
        elif re.search('[a-zA-Z]',text_title):
            return ''
        else:
            return ['אין טבלת ניתוח דקדוקי %s' % text_title]
        
class AcronymWithoutGereshChecker(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
        try:
            text_categories = [cat.title(withNamespace=False) for cat in pywikibot.textlib.getCategoryLinks(text, self._site)]
        except pywikibot.InvalidTitle:
            print("AcronymWithoutGereshChecker: invalid category in page %s" % (page_title))
            return False
        if not hewiktionary_constants.GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' in text_categories):
            return True
        return False
    
class NonAcronymWithGereshChecker(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
        try:
            text_categories = [cat.title(withNamespace=False) for cat in pywikibot.textlib.getCategoryLinks(text, self._site)]
        except pywikibot.InvalidTitle:
            print("NonAcronymWithGereshChecker: invalid category in page %s" % (page_title))
            return False
        if hewiktionary_constants.GERSHAIM_REGEX.findall(page_title) and ('ראשי תיבות' not in text_categories):
            return True
        return False


class GershaimInMareMakom(Checker):
    
    def __init__(self):
        super(GershaimInMareMakom,self).__init__()
        self._tsat = u'צט'
        self._tanah = u'תנ"ך'
        
    def rule_break_found(self,page_title,text_title,text,text_portion):
        tsitutim = re.findall(u'\{\{'+self._tsat+u'/'+self._tanah+u'([^{}]*)\}\}',text,re.MULTILINE)
        if tsitutim:
            for tsitut in tsitutim:
                parts = tsitut.split('|')
                
                if hewiktionary_constants.GERSHAIM_GERESH_REGEX.findall(parts[-1]) or hewiktionary_constants.GERSHAIM_GERESH_REGEX.findall(parts[-2]) or hewiktionary_constants.GERSHAIM_GERESH_REGEX.findall(parts[-3]):
                    return True
        return False


#classes that check by definition
            
class SecondLevelTitleField(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
        if text_title in hewiktionary_constants.titles_list:
            return ['סעיף עם כתורת מסדר 2: %s' % text_title]
        return ''
    
class HtmlTagsInTitle(Checker):
        def rule_break_found(self,page_title,text_title,text,text_portion):
            if '<' in text_title:
                return ['%s' % text_title]
            return False
        
class ItemTitleDiffPageTitle(Checker):
        def rule_break_found(self,page_title,text_title,text,text_portion):
            real_title = re.compile('([^\{\}\)\(]*)(\{\{.*\}\})?(\(.*\))?').search(text_title).group(1).strip()
            no_nikud_title = re.sub('[\u0591-\u05c7\u200f]','',real_title)
            no_nikud_title = re.sub('[״]','"',no_nikud_title)
            if no_nikud_title != page_title:
                return ['כותרת משנה ללא ניקוד: %s' % no_nikud_title ]
            return ''

class NoNikudInSecTitle(Checker):
        def rule_break_found(self,page_title,text_title,text,text_portion):
            words_in_title =  re.compile('[\s]+').split(text_title)
            for word in words_in_title:
                nikud_num  = len(re.findall(u'[\u05b0-\u05bc]',word))
                he_num = len(re.findall(u'[\u0591-\u05f4]',word))
                other_num = len(re.findall(u'[\'|}{)("״]',word))
                if len(word)> 2 and  other_num == 0 and  he_num > 0 and nikud_num == 0:
                    return ['כותרת: %s' % text_title ]

class ErechBetWrong:
    
    def rule_break_found(self,page_title,text_title,text,text_portion):

        erech_bet = re.compile(u'^([^=]+ [\u05d0-\u05d6][\'`"״\u0027]?\s*)$',re.MULTILINE).search(text_title)
        if erech_bet:
            print("found erech bet: %s" % text_title)
            return ['ערך נוסף לא תיקני: %s ' % text_title]
            

        erech_bet = re.compile("^([^=]+ </?[Ss]>[\u05d0-\u05d4]</?[Ss]>)$",re.MULTILINE).search(text_title)
        if erech_bet:
            print("2 found erech bet: %s" % text_title)
            return ['ערך נוסף לא תיקני: %s ' % text_title]
           
#classes that check by field:

class InvalidFieldItemChecker(Checker):
    def rule_break_found(self,page_title,text_title,text,text_portion):
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
        
    r"text variable is the title of the field without the '=' sign "
    def rule_break_found(self,page_title,text_title,text,text_portion):
        if text_portion == PAGE_TEXT_PART.WHOLE_PAGE or text_portion == PAGE_TEXT_PART.WHOLE_ITEM:
            self.reset_state()
            return []
        if text not in hewiktionary_constants.titles_to_order:
            return []
        new_state = hewiktionary_constants.titles_to_order[text]
        if new_state < self._state:
            return ['סעיף %s צריך להיות לפני סעיף %s' % (text,self._last_match) ]
        else:
            self._state = new_state
            self._last_match = text

class HomonimimSeperated(Checker):
    def __init__(self):
        super(HomonimimSeperated,self).__init__()
        self.reset_state()

    def reset_state(self):
        self._titles = []

    #v = value.rule_break_found(page_title,title,part_text,PAGE_TEXT_PART.WHOLE_ITEM)
    def rule_break_found(self,page_title,text_title,text,text_portion):
        tmp_title = re.sub('{{[^{}]*}}','',text_title,2).strip()
        #tmp_title = re.sub('{{','',text_title,2)
        #if(tmp_title != text_title):
        #    print("CHANGED %s =>%s"%(tmp_title,text_title))
        #print(tmp_title)
        reg = re.compile(u'([^)(]+)\s*\(גם: ([^)(]+)\)\s*').search(tmp_title)
        if(reg):
            print("found gam title1: %s" % reg.group(1).strip())
            print("found gam title2: %s" % reg.group(2).strip())
        
            
# a ktzarmar is an item that either has no definition or has less than two section (not including "reo gam")
class KtzarmarWithoutKtzarmarTemplate(Checker):
    def __init__(self):
        super(KtzarmarWithoutKtzarmarTemplate,self).__init__()

    def rule_break_found(self,page_title,text_title,text,text_portion):
        
        if re.compile(u'.*{{קצרמר}}.*',re.MULTILINE).search(text) is not None:
            return []

        #see http://stackoverflow.com/questions/19142042/python-regex-to-get-everything-until-the-first-dot-in-a-string
        # need the "?" so the regex won't be greedy
        #hagdarot = re.compile(u"^(.*?)===[^=]+===\s*\n",re.MULTILINE).search(text)

        sections = re.compile("(^===[^=]+===\s*\n)",re.MULTILINE).split(text)
        
        hagdarot = sections.pop(0)
        hagdara = re.compile("^#[^:]",re.MULTILINE).search(hagdarot)
        
        if not hagdara:
            print("found no hagdara %s" % text_title)
            return ['(אין הגדרות) %s' % text_title]
        
        sec_titles = sections[0::2]
        sec_no_reo_gam = [s for s in sec_titles if hewiktionary_constants.REOGAM not in s]

        if len(sec_no_reo_gam) < 2:
            #print("found less than 2 sections %s" % text_title)
            return ['(פחות משני סעיפים (לא כולל ראו גם)) %s' % text_title]

        return []
