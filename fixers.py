import pywikibot
from pywikibot import pagegenerators
import re
import hewiktionary

class Fixer:
    def __init__(self):
        self._comment = "bla"
        return
    def fix(self,page_title,text_title,text,text_portion):
        """check given text and return "true" (problem found) or "false" (no problem)"""
        raise NotImplementedError('Method %s.fix() not implemented.'
                                  % self.__class__.__name__)

class SectionTitleLvl2ndTo3rdFixer(pywikibot.CurrentPageBot):

    def __init__(self,article = ''):
        site = pywikibot.Site('he', 'wiktionary')
        if article != '':
            print(article[::-1])
            gen = [pywikibot.Page(site, article)]
            gen = pagegenerators.PreloadingGenerator(gen)
        else:
            page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_כותרת_סעיף_מסדר_2")
            gen = pagegenerators.LinkedPageGenerator(page)
            
        super(SectionTitleLvl2ndTo3rdFixer,self).__init__(generator = gen, content = True)

    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        print("SectionTitleLvl2ndTo3rdFixer treat_page called!! %s\n" % self.current_page.title());
        new_page_text = self.current_page.text

        
        part_titles = re.findall("^==[^=\n]+==[ \r\t]*$",self.current_page.text,re.MULTILINE)
            
        for part_title in part_titles:        
            title = re.compile("==\s*([^=]+)\s*==").search(part_title).group(1).strip()
            if title in hewiktionary.titles_list:
                new_page_text = re.sub('==\s*'+title+'\s*==','==='+title+'===',new_page_text,re.MULTILINE)
            
        if new_page_text != self.current_page.text:
            print('saving %s' % self.current_page.title())
            self.put_current(new_page_text, summary = u'בוט המחליף כותרות סעיפים מסדר 2 לסדר 3')
titles_replacer = {

    "דעת פרשנים" : hewiktionary.PARSHANIM,
    "צרופים" :  hewiktionary.TSERUFIM,
    "ביטויים וצרופים" :  hewiktionary.TSERUFIM,
    "צירופים וביטויים" :  hewiktionary.TSERUFIM,
    "מילים קרובות" : hewiktionary.NIRDAFOT,
    "מלים נרדפות" : hewiktionary.NIRDAFOT,
    "נרדפות" : hewiktionary.NIRDAFOT,
    "מילים מנוגדות" : hewiktionary.NIGUDIM,
    "נגודים" : hewiktionary.NIGUDIM,
    "תרגומים" : hewiktionary.TERGUM,
    "תירגום" : hewiktionary.TERGUM,
    "תירגומים" : hewiktionary.TERGUM,
    "ראה גם" : hewiktionary.REOGAM,
    "הערת שוליים" : hewiktionary.SHULAIM,
    "הערות שוליים" : hewiktionary.SHULAIM,
    "קשורים חיצוניים" : hewiktionary.KISHURIM,
    "מקורות" : hewiktionary.SIMUCHIN,
    "גזרון" : hewiktionary.GIZRON
}

class SectionTitleReplacerBot(pywikibot.CurrentPageBot):

    def __init__(self,article = ''):
        site = pywikibot.Site('he', 'wiktionary')
        if article != '':
            print(article[::-1])
            gen = [pywikibot.Page(site, article)]
            gen = pagegenerators.PreloadingGenerator(gen)
        else:
            page = pywikibot.Page(site,"ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה")
            gen = pagegenerators.LinkedPageGenerator(page)
        super(SectionTitleReplacerBot,self).__init__(generator = gen, content = True)
    
    def treat_page(self):
        """Load the given page, do some changes, and save it."""

        print(self.current_page.title())
        old_page_text = self.current_page.text
        new_page_text = old_page_text

        page_title = self.current_page.title()

        for key, value in titles_replacer.items():
            new_page_text = re.sub("===\s*%s\s*===" % (key), "=== %s ===" % (value), new_page_text, re.MULTILINE )
    
        if(new_page_text != old_page_text):
            print('CHANGED')
            self.put_current(new_page_text, summary = u'בוט המחליף כותרות סעיפים')

class LinkShoreshToTemplateShoresh(Fixer):
    def __init__(self, **kwargs):
        super(LinkShoreshToTemplateShoresh,self).__init__(**kwargs)
        self._shoresh = u'שורש'
        self._kategoria = u'קטגוריה'
        self._summary = u'בוט המחליף לינק לשורש בתבנית שורש'
    def fix(self,page_title,text):
        print('in fix - %s' % page_title)
        return re.sub(u'\[\['+self._kategoria+u':([^\]]*) \('+self._shoresh+u'\)\]\]',u'{{'+self._shoresh+r'|\1}}',text,re.MULTILINE)
        
        
        
r"""
According to Ariel1024 :

החלפה של: {{ש}}{{ש}}{{ש}}{{ש}} וכולי בסוף ערכים לתבנית {{-}}

see:

https://he.wiktionary.org/w/index.php?title=%D7%A9%D7%99%D7%97%D7%AA_%D7%9E%D7%A9%D7%AA%D7%9E%D7%A9:Ariel1024&oldid=255275#.D7.94.D7.99
"""
    
class ShinToMakafBot(pywikibot.CurrentPageBot):

    def __init__(self, **kwargs):
        super(ShinToMakafBot,self).__init__(**kwargs)
        self._summary = u'בוט המחליף תבניות {{ש}} לתבנית {{-}} \u200f'

        def fix(self,page_title,text):

            s = re.compile(u'.*(שורש).*',re.MULTILINE).search(page_title)
            if s is not None:
                return 

            s = re.compile(u'.*#הפניה.*',re.MULTILINE).search(text)
            if s is not None:
                return 

            return re.sub(u'(\{\{ש\}\}\n?){2,}','{{-}}\n',text,re.MULTILINE)




