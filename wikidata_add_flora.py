import os
import re
import pywikibot
import json
import pickle

from pywikibot import pagegenerators as pg
from itertools import chain

wikidata_site = pywikibot.Site("wikidata", "wikidata")
repo = wikidata_site.data_repository()


FAMILY_QUERY = """
SELECT ?item ?desc
WHERE
{
  ?item wdt:P105 wd:Q35409 .
  ?item schema:description ?desc .
  FILTER regex(?desc, "(plants|conifers)", "i")
  filter (lang(?desc) = "en") .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""

QGEN = """
SELECT ?item ?desc
WHERE
{
  ?item wdt:P105 wd:Q34740 .
  ?item schema:description ?desc .
  FILTER regex(?desc, "(plants|conifers)", "i")
  filter (lang(?desc) = "en") .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""

def get_query_output(pkl_file,query):
    if os.path.isfile(pkl_file):
        output = pickle.load(open(pkl_file, 'rb'))

    else:
        output = set()
        generator = pg.WikidataSPARQLPageGenerator(query, site=wikidata_site)
        for p in generator:
            print(p)
            p.get()
            output.add(p)
            print(p.aliases)
        pickle.dump(output, open(pkl_file, "wb"))
    return output



wiki_families = get_query_output('wiki_families.pkl', FAMILY_QUERY)
wiki_genuses = get_query_output('wiki_genuses.pkl', QGEN)


"""
[
    {
        "heb_name": "\u05de\u05e9\u05e4\u05d7\u05ea \u05d4\u05d0\u05d1\u05e8\u05e0\u05d9\u05ea\u05d9\u05d9\u05dd",
        "lat_name": "Hypolepidaceae",
        "url": "http://flora.org.il/systematics/hypolepidaceae",
        "genuses": [
            {
                "lat_name": "Pteridium",
                "heb_name": "\u05d0\u05d1\u05e8\u05e0\u05d9\u05ea",
                "url": "http://flora.org.il/systematics/pteridium"
            }
        ]
    },
...]
"""


spelling = {'Lytheraceae' : 'Lythraceae',
            'Ophioglosaceae' : 'Ophioglossaceae',
            'Simarubiaceae':'Simaroubaceae',
            'Gymnogrammaceae': 'Pteridaceae'}


errs_file = open('errors.txt','w')

wiki_families = set(filter(lambda p: 'he' not in p.labels,wiki_families))
pickle.dump(wiki_families, open("wiki_families.pkl", "wb"))

wiki_genuses = set(filter(lambda g: 'he' not in g.labels,wiki_genuses))
pickle.dump(wiki_genuses, open("wiki_genuses.pkl", "wb"))

with open('all.json') as f:
    data = json.load(f)
    for flora_il_family in data:

        lat = flora_il_family['lat_name']
        if lat in spelling:
            lat = spelling[lat]
        if '(' in lat:
            m = re.match(r"(.*)\s+\((.*)\)",lat)
            lat1 = m.group(1)
            lat2 = m.group(2)
        else:
            lat1 = lat2 = lat
        for wiki_family in wiki_families:
            alias_vals = wiki_family.aliases.values()
            alias_list = set(chain.from_iterable(alias_vals))
            if lat1 in alias_list or lat1 in wiki_family.labels.values() \
               or lat2 in alias_list or lat2 in wiki_family.labels.values():
                current_family = pywikibot.ItemPage(repo, wiki_family.title())
                current_family.get()
                if 'he' not in current_family.labels:
                    try:
                        current_family.editLabels(labels={'he': flora_il_family['heb_name']}, summary=u'Add hebrew label')
                    except pywikibot.OtherPageSaveError:
                        print("already set")
                found_fam = True
                break
        for flora_il_gen in flora_il_family["genuses"]:
            lat = flora_il_gen['lat_name']
            found = False
            for wiki_genus in wiki_genuses:
                alias_vals = wiki_genus.aliases.values()
                alias_list = set(chain.from_iterable(alias_vals))
                if lat in alias_list or lat in wiki_genus.labels.values():
                    current_genus = pywikibot.ItemPage(repo, wiki_genus.title())
                    current_genus.get()
                    if 'he' not in current_genus.labels:
                        try:
                            current_genus.editLabels(labels={'he': flora_il_gen['heb_name']}, summary=u'Add hebrew label')
                        except pywikibot.OtherPageSaveError:
                            print("already set")
                    found = True
                    break

            if not found:
                errs_file.write("wiki genus not found #%s#\n" % lat)
                errs_file.flush()
                print("NOT")
                print("#%s#" % lat)
    errs_file.close()
