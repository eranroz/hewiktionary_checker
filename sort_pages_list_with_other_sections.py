import sys
import re
import pywikibot

first =  "סך הכל"
reg = re.compile("שאינו מהרשימה: (.*)")

def cmp(m1,m2):
    if m1.startswith(first):
        return -1
    if m2.startswith(first):
        return 1
    try:
        s1 = reg.search(m1).group(1)
        s2 = reg.search(m2).group(1)
    except:
        print("PROBLEM")
        print(m1)
        print(m2)
        return 0
    if s1 < s2:
        return -1
    if s1 > s2:
        return 1
    return 0




def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K


def main(args):
    pywikibot.handle_args(args)
    site = pywikibot.Site('he', 'wiktionary')
    maintain_page = pywikibot.Page(site, "ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה")

    lines = maintain_page.get().split("\n")

    lines.pop()
    lines.pop()
    lines.sort(key=cmp_to_key(cmp))
    for l in lines:
        print(l)


    lines.append("\n")
    lines.append("[[קטגוריה: ויקימילון - תחזוקה]]")
    sorted_text = '\n'.join(['%s' % l for l in lines])
    maintain_page.text = sorted_text
    maintain_page.save("בוט - מיון לפי שם הסעיף")


if __name__ == "__main__":
    main(sys.argv)
