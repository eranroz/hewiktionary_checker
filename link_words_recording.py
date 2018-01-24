#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pywikibot
from pywikibot import pagegenerators

import re
import os
import sys
import hewiktionary

class TEMPLATE_STATE:
    BEFORE_START = 1
    START = 2
    END = 3
    NEXT_PART = 4

class HebrewWordsRecordsLinkerBot(pywikibot.CurrentPageBot):

    def treat_page(self):

        """Load the given page, do some changes, and save it."""
        #print(self.current_page.title())

        #\u0590-\u05f4 is the hebrew unicode range
        #\u200f is RIGHT_TO_LEFT mark
        s = re.compile(u'^File:He-(.+)\.ogg$').match(self.current_page.title())
        if s:
            word = s.group(1) 
            site = pywikibot.Site('he','wiktionary')
            word_without_nikud  = re.sub('[\u0590-\u05c7\u05f0-\u05f4\u200f]','',word)
            #print("WITHOUT")

            wikt_page = pywikibot.Page(site,title = word_without_nikud)
            print(word)
            print(word_without_nikud)
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

    local_args = pywikibot.handle_args(global_args)
    for arg in args:
        m = re.compile('^-limit:([0-9]+)$').match(arg)
        a = re.compile('^-article:(.+)$').match(arg)
        if m:
            limit = int(m.group(1))
        elif a:
            article = a.group(1)
        else:
            global_args.append(arg)


    if article:
        gen = [pywikibot.Page(site, article)]
        gen = pagegenerators.PreloadingGenerator(gen)

    bot = HebrewWordsRecordsLinkerBot(generator = gen)
    bot.run()  

    print('_____________________DONE____________________')
    

if __name__ == "__main__":
    main(sys.argv)
