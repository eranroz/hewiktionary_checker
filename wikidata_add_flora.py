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

# Q2 = """
# SELECT ?item ?desc
# WHERE
# {
#   ?item wdt:P105 wd:Q35409 .
#   ?item schema:description ?desc .
#   FILTER regex(?desc, "(plants|conifers)", "i")
#   filter (lang(?desc) = "en") .
#   SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
# }
# """
#
#
# generator2 = pg.WikidataSPARQLPageGenerator(Q2, site=wikidata_site)
# for p in generator2:
#     if p not in plants:
#         p.get()
#         plants.add(p)
#         print("added")
#     else:
#         print('already')
# pickle.dump(plants, open("plants.pkl", "wb"))
# os.exist(1)

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
print(plants)
print(type(plants))
for p in plants:
    #print(p.aliases)
    print(p.labels)

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
                found = True
                break
        if not found:
            print("NOT")
            print("#%s#" % lat)





item = pywikibot.ItemPage(wikidata_site, 'Q3360397')
item.get()
print(item.aliases)
print("sadddddddddddddd")
print(item.labels.values())
print('Paeoniaceae' in item.labels.values())
#vals =
#v =
#print(v)

site = pywikibot.Site('en', 'wikipedia')  # any site will work, this is just an example
page = pywikibot.WikiBasePage(site, 'Douglas Adams')
item = pywikibot.ItemPage.fromPage(page)  # this can be used for any page object

# you can also define an item like this
repo = site.data_repository()  # this is a DataSite object
item = pywikibot.ItemPage(repo, 'Q42')  # This will be functionally the same as the other item we defined
item.get()  # you need to call it to access any data.
sitelinks = item.sitelinks
aliases = item.aliases
if 'en' in item.labels:
    print('The label in English is: ' + item.labels['en'])
if item.claims:
    if 'P31' in item.claims: # instance of
        print(item.claims['P31'][0].getTarget())
        print(item.claims['P31'][0].sources[0])  # let's just assume it has sources.

# Edit an existing item
item.editLabels(labels={'en': 'Douglas Adams'}, summary=u'Edit label')
item.editDescriptions(descriptions={'en': 'English writer'}, summary=u'Edit description')
item.editAliases(aliases={'en':['Douglas Noel Adams', 'another alias']})
item.setSitelink(sitelink={'site': 'enwiki', 'title': 'Douglas Adams'}, summary=u'Set sitelink')
item.removeSitelink(site='enwiki', summary=u'Remove sitelink')

# You can also made this all in one time:
data = {'labels': {'en': 'Douglas Adams'},
  'descriptions': {'en': 'English writer'},
       'aliases': {'en': ['Douglas Noel Adams', 'another alias'], 'de': ['Douglas Noel Adams']},
     'sitelinks': [{'site': 'enwiki', 'title': 'Douglas Adams'}]}
item.editEntity(data, summary=u'Edit item')