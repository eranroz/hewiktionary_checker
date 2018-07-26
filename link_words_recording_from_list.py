#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import re
import pywikibot
import hewiktionary

class TEMPLATE_STATE:
    BEFORE_START = 1
    START = 2
    END = 3
    NEXT_PART = 4

class PagesFromListGenerator:
    def __init__(self, site,file):
        self.site = site
        self.file = open(file, 'r')
    def __iter__(self):
        for line in self.file:
            yield pywikibot.Page(self.site,title = line)


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
                parts_gen = hewiktionary.split_parts(wikt_page.text)

                # the first part will always be either an empty string or a string before the first definition (like {{לשכתוב}})
                final = []
                first  = parts_gen.__next__()[0]

                if first.strip() != '':
                    final += [first]
                state = TEMPLATE_STATE.BEFORE_START
                for part in parts_gen:
                    sec_word = hewiktionary.lexeme_title_regex_grouped.search(part[0]).group(1).strip()
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
                            final += [line+'\n']

                            if state == TEMPLATE_STATE.BEFORE_START and (re.compile(hewiktionary.template_regex).search(line) or re.compile(hewiktionary.verb_template_regex).search(line)):
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

    local_args = pywikibot.handle_args(args)

    file = ''
    try:
        file =  local_args[1]

    except:
        print("You should add a file with a list of audios in commons - see audio_tet.txt for an example")
        sys.exit(1)

    gen = PagesFromListGenerator(site,file)
    bot = HebrewWordsRecordsLinkerBot(generator = gen)
    bot.run()

    print('_____________________DONE____________________')

if __name__ == "__main__":
    main(sys.argv)
