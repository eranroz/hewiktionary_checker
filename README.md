# Scripts that fix, unify and add stuff to the Hebrew Wiktionary.

The scripts are based on [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot).

They ran periodically by [Dafna3.bot](https://he.wiktionary.org/wiki/%D7%9E%D7%A9%D7%AA%D7%9E%D7%A9:Dafna3.bot)   

### Argument available to most scripts:

* `-article:<article name>` - run the script on a specific article instead of scanning all articles.

* `-always` - don't ask to confirm upon editing


## Scripts:

* **section_title_replacer_bot.py**, a bot that scans all articles in the list in [ויקימילון:תחזוקה/דפים_עם_סעיפים_שאינם_מהרשימה_הסגורה](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%A1%D7%A2%D7%99%D7%A4%D7%99%D7%9D_%D7%A9%D7%90%D7%99%D7%A0%D7%9D_%D7%9E%D7%94%D7%A8%D7%A9%D7%99%D7%9E%D7%94_%D7%94%D7%A1%D7%92%D7%95%D7%A8%D7%94) and replaces the wrong subsection title with the right one if it can.

* **fix_bad_order_fields.py**, a bot that reorder the subsections in each lexme according to the agreed order, it scans articles in the list in [ויקימילון:תחזוקה/דפים עם סעיפים שאינם בסדר הנכון](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%A1%D7%A2%D7%99%D7%A4%D7%99%D7%9D_%D7%A9%D7%90%D7%99%D7%A0%D7%9D_%D7%91%D7%A1%D7%93%D7%A8_%D7%94%D7%A0%D7%9B%D7%95%D7%9F)

* **sec_tite_to_third_bot.py**, a bot that replaces the heading from second level to third level for subsections titles. It scans the articles in the list in [ויקימילון:תחזוקה/דפים עם כותרת סעיף מסדר 2](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9B%D7%95%D7%AA%D7%A8%D7%AA_%D7%A1%D7%A2%D7%99%D7%A3_%D7%9E%D7%A1%D7%93%D7%A8_2)

* **link_words_recording.py**, a bot that scans audio files in [commons](https://commons.wikimedia.org/wiki/Category:Hebrew_pronunciation) and add them to the lexeme definition in hewiktionary.

* **rule_checker.py** - a bot that checks all different issues and produce a list of article to each issue.

Run with `-h` to list possible issues codes to check and run with `--issues <code1> <code2> <code3> ..` to check only the listed issues.

The list of issues:

- [wrong order of sections](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%A1%D7%A2%D7%99%D7%A4%D7%99%D7%9D_%D7%A9%D7%90%D7%99%D7%A0%D7%9D_%D7%91%D7%A1%D7%93%D7%A8_%D7%94%D7%A0%D7%9B%D7%95%D7%9F), code is `fwo`

- [a stub without the stub template](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%A7%D7%A6%D7%A8%D7%9E%D7%A8_%D7%91%D7%9C%D7%99_%D7%AA%D7%91%D7%A0%D7%99%D7%AA_%D7%A7%D7%A6%D7%A8%D7%9E%D7%A8), code is `kwkt`

- [homonyms separated](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%94%D7%95%D7%9E%D7%95%D7%A0%D7%99%D7%9E%D7%99%D7%9D_%D7%9E%D7%95%D7%A4%D7%A8%D7%93%D7%99%D7%9D), code is `sh`

- [sections titles not from the predefined list](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%A1%D7%A2%D7%99%D7%A4%D7%99%D7%9D_%D7%A9%D7%90%D7%99%D7%A0%D7%9D_%D7%9E%D7%94%D7%A8%D7%A9%D7%99%D7%9E%D7%94_%D7%94%D7%A1%D7%92%D7%95%D7%A8%D7%94), code is `if`

- [section title heading is 2 level instead of 3]( https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9B%D7%95%D7%AA%D7%A8%D7%AA_%D7%A1%D7%A2%D7%99%D7%A3_%D7%9E%D7%A1%D7%93%D7%A8_2), code is `2ltfl`

- [acronyms without gershaim](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%A8%D7%90%D7%A9%D7%99_%D7%AA%D7%99%D7%91%D7%95%D7%AA_%D7%97%D7%A1%D7%A8%D7%99_%D7%92%D7%A8%D7%A9%D7%99%D7%99%D7%9D), code is `ang`

- [lexeme tile without Nikud is different from the article title](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%91%D7%94%D7%9D_%D7%9B%D7%95%D7%AA%D7%A8%D7%AA_%D7%9E%D7%A1%D7%93%D7%A8_2_%D7%9C%D7%9C%D7%90_%D7%A0%D7%99%D7%A7%D7%95%D7%93_%D7%A9%D7%95%D7%A0%D7%94_%D7%9E%D7%A9%D7%9D_%D7%94%D7%93%D7%A3), code is `stdpt`

- [bible citation with gershaim in reference](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%A6%D7%99%D7%98%D7%95%D7%98_%D7%9E%D7%94%D7%AA%D7%A0%D7%9A_%D7%A2%D7%9D_%D7%92%D7%A8%D7%A9%D7%99%D7%99%D7%9D_%D7%91%D7%9E%D7%A8%D7%90%D7%99_%D7%9E%D7%A7%D7%95%D7%9D), code is `gmm`

- [gremmer box is missing](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%97%D7%A1%D7%A8%D7%99_%D7%A0%D7%99%D7%AA%D7%95%D7%97_%D7%93%D7%A7%D7%93%D7%95%D7%A7%D7%99), code is `wgb`

- [lexeme title without nikud](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9B%D7%95%D7%AA%D7%A8%D7%AA_%D7%9E%D7%A9%D7%A0%D7%94_%D7%9C%D7%90_%D7%9E%D7%A0%D7%95%D7%A7%D7%93%D7%AA), code is `nnst`

- [page without a title](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%9C%D7%9C%D7%90_%D7%9B%D7%95%D7%AA%D7%A8%D7%AA), code is `wt`

- [text before first lexeme](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%98%D7%A7%D7%A1%D7%98_%D7%9C%D7%A4%D7%A0%D7%99_%D7%94%D7%94%D7%A2%D7%A8%D7%94_%D7%94%D7%A8%D7%90%D7%A9%D7%95%D7%A0%D7%94), code is `tbd`

- [wrong subsection](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%A2%D7%A8%D7%9A_%D7%9E%D7%A9%D7%A0%D7%99_%D7%9C%D7%90_%D7%AA%D7%99%D7%A7%D7%A0%D7%99), code is `ebw`

- [html tags inside sections](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%AA%D7%92%D7%99%D7%95%D7%AA_%D7%94%D7%99%D7%A4%D7%A8-%D7%98%D7%A7%D7%A1%D7%98_%D7%91%D7%9B%D7%95%D7%AA%D7%A8%D7%AA), code is `ht`

- [first heading for title](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%A2%D7%9D_%D7%9B%D7%95%D7%AA%D7%A8%D7%AA_%D7%9E%D7%93%D7%A8%D7%92%D7%94_%D7%A8%D7%90%D7%A9%D7%95%D7%A0%D7%94), code is `flt`

- [default comment not erased](https://he.wiktionary.org/wiki/%D7%95%D7%99%D7%A7%D7%99%D7%9E%D7%99%D7%9C%D7%95%D7%9F:%D7%AA%D7%97%D7%96%D7%95%D7%A7%D7%94/%D7%93%D7%A4%D7%99%D7%9D_%D7%91%D7%94%D7%9D_%D7%9C%D7%90_%D7%A0%D7%9E%D7%97%D7%A7%D7%94_%D7%94%D7%94%D7%A2%D7%A8%D7%94_%D7%94%D7%93%D7%99%D7%A4%D7%95%D7%9C%D7%98%D7%99%D7%91%D7%99%D7%AA), code is `c`
  