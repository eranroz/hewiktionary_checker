# Scripts that fix, unify and add stuff to the Hebrew Wiktionary.

The scripts are based on [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot).

They ran periodically by [Dafna3.bot](https://he.wiktionary.org/wiki/%D7%9E%D7%A9%D7%AA%D7%9E%D7%A9:Dafna3.bot)   

### Argument available to most scripts:

* `-article:<article name>` - run the script on a specific article instead of scanning all articles.

* `-always` - don't ask to confirm upon editing


## Scripts:

* *section_title_replacer_bot.py* - a bot that scans all articles in the list in [ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%A1%D7%A2%D7%99%D7%A4%D7%99%D7%9D_%D7%A9%D7%90%D7%99%D7%A0%D7%9D_%D7%9E%D7%94%D7%A8%D7%A9%D7%99%D7%9E%D7%94_%D7%94%D7%A1%D7%92%D7%95%D7%A8%D7%94) and replaces the wrong subsection title with the right one if it can.


