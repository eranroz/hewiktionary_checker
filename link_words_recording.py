#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)
from pywikibot.tools import issue_deprecation_warning

import re
import os
import sys
import hewiktionary_constants

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

class TEMPLATE_STATE:
    BEFORE_START = 1
    START = 2
    END = 3
    NEXT_PART = 4

x = 0
class HebrewWordsRecordsLinkerBot(pywikibot.CurrentPageBot):

    def treat_page(self):
        global x

        if x >= 20:
            return
        
        """Load the given page, do some changes, and save it."""
        #print(self.current_page.title())
        s = re.compile(u'^File:He-([\u0590-\u05f4\u200f]+)\.ogg$').match(self.current_page.title())
        if s:
            word = s.group(1) 
            site = pywikibot.Site('he','wiktionary')
            word_without_nikud  = re.sub('[\u0590-\u05c7\u200f]','',word)
            #print("WITHOUT")

            wikt_page = pywikibot.Page(site,title = word_without_nikud)
            #print(word)
            #
            if wikt_page.exists():
                parts_gen = split_parts(wikt_page.text)
                
                # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
                final = []
                first  = parts_gen.__next__()[0]

                if first.strip() != '':
                    final += [first]
                state = TEMPLATE_STATE.BEFORE_START    
                for part in parts_gen:
                    sec_word = re.compile("^==\s*([^=]+)\s*==\s*\n*").search(part[0]).group(1).strip()
                    sec_word = re.sub('\u200f','',sec_word)
                    
                    if(sec_word == word):
                        final += [part[0]]
                        print("   FOUND MATCH: "+word)
                        if re.compile("{{נגן").search(part[1]):
                            print("ALREADY HAVE NAGAN")
                            return
                        lines = part[1].splitlines()
                        line_idx = 0
                        for line in lines:
                            line_idx += 1
                            #template_regex='\n*{{ניתוח\s+דקדוקי\s*\|?\s*'
                            #verb_template_regex='\n*{{ניתוח\s+דקדוקי\sלפועל\s*\|?\s*'
                            #if line.strip('\n\r') != '':
                            final += [line+'\n']
                            
                            if state == TEMPLATE_STATE.BEFORE_START and (re.compile(hewiktionary_constants.template_regex).search(line) or re.compile(hewiktionary_constants.verb_template_regex).search(line)):
                                state = TEMPLATE_STATE.START
                                
                            elif state == TEMPLATE_STATE.START:
                                if re.search("}}",line) and not re.search("{{",line):
                                    
                                    state = TEMPLATE_STATE.END
                                    break
                        if state != TEMPLATE_STATE.END:
                            print('PROBLEM 1: seems like problems in page '+word_without_nikud)
                            return
                        mediafile_name = re.compile(u'^File:(He-.*.ogg)$').match(self.current_page.title()).group(1)
                        final += ["{{נגן|קובץ=%s|כתובית=הגיה}}\n" % mediafile_name]
                        final += ['\n'.join(lines[line_idx:])]
                    else:
                        if state == TEMPLATE_STATE.END:
                            final += ['\n']
                            state = TEMPLATE_STATE.NEXT_PART
                        
                        final += [part[0],part[1]]

                new_page_text = ''.join(final)
                x += 1
                if new_page_text != wikt_page.text:
                    print('saving %s' % wikt_page.title())
                    wikt_page.text = new_page_text
                    wikt_page.save('בוט שמוסיף תבנית "נגן"')


def main(args):
    
    site = pywikibot.Site('commons', 'commons')    
    cat = pywikibot.Category(site,'Category:Hebrew_pronunciation')
    gen = pagegenerators.CategorizedPageGenerator(cat)
    
    global_args  = []

    limit = 0
    article = None

    for arg in args:
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        if m:
            limit = int(m.group(1))
        elif a:
            article = a.group(1)
        else:
            global_args.append(arg)

    local_args = pywikibot.handle_args(global_args)
#    if article:
#        gen = [pywikibot.Page(site, article)]
#        gen = pagegenerators.PreloadingGenerator(gen)
        
    bot = HebrewWordsRecordsLinkerBot(generator = gen)
    bot.run()  

    print('_____________________DONE____________________')
    

if __name__ == "__main__":
    main(sys.argv)
