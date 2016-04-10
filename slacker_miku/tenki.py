# -*- coding: utf-8 -*-
import urllib.request
import json

def getTenki(citycode):
    if citycode is None:
        citycode = '130010'

    url = 'http://weather.livedoor.com/forecast/webservice/json/v1'
    res = urllib.request.urlopen(url + "?city=" + citycode).read()
    res = json.loads(res.decode('utf-8'))
    return res['description']['text']


if __name__ == "__main__":
    print(getTenki(None))
