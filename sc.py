import scrapy
import json

"""
RUN WITH THE COMMAND:

scrapy runspider sc.py -s USER_AGENT="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36"
"""
"""
Genus Dict:
  lat_name : <lat_name>
  heb_name: <heb_name>
  url: <url>

Family Dict
   lat_name: <lat_name>
   heb_name: <heb name>
   url: <url>
   gnuses: [Gen1,Gen2, ..]
"""
class FamilySpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ["http://flora.org.il/families/"]
    first1 = True
    first2 = True
    families_list = []

    def parse(self, response):
        print(self)
        print(response)
        for family in response.css('div.family'):
            familes_dict = {}
            heb_name = family.css('span.heb')
            lat_name = family.css('span.lat')
            family_dict = {}
            family_dict["heb_name"] = heb_name.css('a ::text').extract_first()
            family_dict["lat_name"] = lat_name.css('a ::text').extract_first()
            url = heb_name.css('a')
            print("===url===")
            family_dict["url"] = heb_name.css('a ::attr(href)').extract_first()
            family_dict['genuses'] = []
            for li in family.css("li"):
                a = li.css('a')
                heb_genus = a[0]
                lat_genus = a[1]
                gnus_dict = {}
                gnus_dict =  {"lat_name" : lat_genus.css(' ::text').extract_first(),
                                                      "heb_name" : heb_genus.css(' ::text').extract_first(),
                                                      "url" :      heb_genus.css(' ::attr(href)').extract_first()}
                print("genus_dict")
                print(gnus_dict)
                family_dict['genuses'].append(gnus_dict)
            FamilySpider.families_list.append(family_dict)
            print("family dict")
            print(family_dict)
            #print(genuses_div)
            yield family_dict
    def closed( self, reason ):
        with open('all.json','w') as all:
            all.write(json.dumps(FamilySpider.families_list,indent = 4))

        print("----------------- DONE -------------------")

        #for next_page in response.css('div.prev-post > a'):
        #    yield response.follow(next_page, self.parse)
