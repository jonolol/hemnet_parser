import re
import json
from pytz import reference
import urllib3
from lxml import html
from datetime import datetime
from datetime import timezone, tzinfo
from dateutil import parser as dateparser


class HemnetParser:

    baseUrl = 'https://www.hemnet.se/bostad/{}'

    @staticmethod
    def convert_from_hex_mix(inStr):
        i = 0
        output = []
        for m in re.compile(r'(\\x[a-f0-9]{2})+').finditer(inStr):
            output.append(inStr[i:m.start()])
            output.append(bytearray.fromhex(m.group(0).replace('\\x', '')).decode())
            i = m.end()
        output.append(inStr[i:])
        return ''.join(output)

    @staticmethod
    def parse(number):

        url = HemnetParser.baseUrl.format(number)
        retData = {}

        http = urllib3.PoolManager()

        r = http.request('GET', url)

        page = r.data.decode()
        tree = html.fromstring(page)

        p = tree.findall(r'.//script')

        dataLayerStr = ''
        for s in p:
            o = re.compile(r'(?<=dataLayer = )\[[^\]]+\]').search(str(s.text))
            if o is not None:
                dataLayerStr = o.group(0)
                break

        if dataLayerStr:
            dataLayer = json.loads(HemnetParser.convert_from_hex_mix(dataLayerStr))
            for k, v in dataLayer[2]['property'].items():
                retData[k] = v

        retData['postal_city'] = retData['locations']['postal_city']

        retData['open_house'] = []
        openHouseTags = tree.xpath('//*[@*="{}"]/text()'.format('open-house__time'))
        for t in openHouseTags:
            t = t.strip()
            retData['open_house'].append(HemnetParser.convert_from_hex_mix(t))

        visitors = tree.xpath('//*[@*="{}"]/text()'.format('property-stats__visits'))[0]
        visitors = ''.join(visitors.split())
        retData['visitors'] = visitors

        published = tree.xpath('//span/@datetime')[0] #The whole page only has one datetime span, that's when the item was posted
        published = dateparser.parse(published)
        published.replace(tzinfo=reference.LocalTimezone())
        retData['published'] = published.strftime('%d/%m/%Y')

        days_up = datetime.now(reference.LocalTimezone()) - published
        retData['days_up'] = days_up.days

        daydiv = days_up.days
        if daydiv <= 0: daydiv = 1
        visitors_per_day = int(int(visitors) / daydiv)
        retData['visitors_per_day'] = visitors_per_day

        return retData
