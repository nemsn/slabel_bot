# -*- coding: utf-8 -*-
import urllib.request
import json
import datetime
import re
L = [
    '牡羊座','牡牛座','双子座','蟹座','獅子座','乙女座','天秤座','蠍座','射手座','山羊座','水瓶座','魚座',
    ]

def getUranai(s):
    # 星座の指定を確認
    star_L = []
    for d in L:
        p = re.compile(r'.*{0}.*'.format(d))
        m = p.search(s)
        if m:
            star_L.append(d)
    
    if len(star_L) == 0:
        return("占いたい星座を教えてね！～牡羊座,牡牛座,双子座,蟹座,獅子座,乙女座,天秤座,蠍座,射手座,山羊座,水瓶座,魚座～")
    
    d = datetime.datetime.today()
    day_str = d.strftime('%Y/%m/%d')

    url = 'http://api.jugemkey.jp/api/horoscope/free/' + day_str
    res = urllib.request.urlopen(url).read()
    res = json.loads(res.decode('utf-8'))

    str = ""
    for i in res['horoscope'][day_str]:
        if i['sign'] in star_L:
            str += "{0}\n{1}\nラッキーカラー：{2}\nラッキーアイテム：{3}\n".format(i['sign'],i['content'],i['color'],i['item'])

    return str

if __name__ == "__main__":
    print(getUranai("魚座"))

