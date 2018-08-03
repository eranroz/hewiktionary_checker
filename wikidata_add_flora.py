import re
import pywikibot
import json
import pickle

from pywikibot import pagegenerators as pg
from itertools import chain

QUERY = """
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

wikidata_site = pywikibot.Site("wikidata", "wikidata")


try:
    plants = pickle.load(open('plants.pkl','rb'))

except Exception:
    plants = set()
    generator = pg.WikidataSPARQLPageGenerator(QUERY, site=wikidata_site)
    for p in generator:
        print(p)
        p.get()
        plants.add(p)
        print(p.aliases)
    pickle.dump(plants, open("plants.pkl", "wb"))

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

with open('all.json') as f:
    data = json.load(f)
    for family in data:
        found  = False
        lat = family['lat_name']
        if lat in spelling:
            lat = spelling[lat]
        if '(' in lat:
            m = re.match(r"(.*)\s+\((.*)\)",lat)
            lat1 = m.group(1)
            lat2 = m.group(2)
        else:
            lat1 = lat2 = lat
        for plant in plants:
            alias_vals = plant.aliases.values()
            alias_list = set(chain.from_iterable(alias_vals))
            if lat1 in alias_list or lat1 in plant.labels.values() \
               or lat2 in alias_list or lat2 in plant.labels.values():
                print("FOUND")
                if 'he' not in plant.labels:
                    plant.editLabels(labels={'he': family['heb_name']}, summary=u'Add hebrew label')
                found = True
                break

        if not found:
            print("NOT")
            print("#%s#" % lat)
