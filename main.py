import os
from hemnet_parser import HemnetParser
import unicodecsv as csv

keys = [
    'id',
    'street_address',
    'postal_city',
    'living_area',
    'rooms',
    'price',
    'price_per_m2',
    'borattavgift',
    'driftkostnad',
    'visitors',
    'published',
    'days_up',
    'visitors_per_day',
    'open_house',
    'locations',
    'location',
    'main_location',
    'broker_firm',
    'item_type',
    'status',
    'upcoming_open_houses',
    'home_swapping',
    'images_count',
    'offers_selling_price',
    'has_price_change',
    'new_production',
    'foreign'
]

homes = {
    '11998417' : {}
}

for h in homes.keys():
    homes[h] = HemnetParser.parse(h)

#    for k in keys:
#        if k in homes[h].keys():
#            print('{}: {}'.format(k, homes[h][k]))
#        else:
#            print('{}: -'.format(k))

with open('hemnet.csv', 'wb') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=keys, restval='-')
    writer.writeheader()
    writer.writerows(homes.values())
