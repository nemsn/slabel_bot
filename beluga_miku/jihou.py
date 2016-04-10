# -*- coding:utf-8 -*-
import datetime
import time
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import birthday
try:
    import webapi.beluga_api as beluga_api
    import settings
except ImportError:
    print("from __main__ start")


def post_time_beluga():
    b = beluga_api.BelugaTool(settings.BELUGA_BOT_NAME, settings.BELUGA_BOT_PASSWORD)
    
    d = datetime.datetime.today()

    icon_num = d.hour
    if icon_num >= 12:
        icon_num -= 12
    file_path = "./icon/icon{}.png".format(icon_num)
    b.set_profile_image(file_path)

    s = ""
    if d.hour is 4:
        s = "#もう4時かよん"
    else:
        s = "--------------------- " + str(d.hour) + "時 ---------------------"

    b.update(s)

    # 月初め
    if d.day is 1 and d.hour is 0:
        next_new_year = datetime.datetime(d.year+1, 1, 1)
        now_new_year = datetime.datetime(d.year, 1, 1)
        year_days = next_new_year - now_new_year # 今年の一年の日数
        delta = next_new_year - d
        x = delta / year_days * 100
        month_msg = "{0}月になりました。{1}年、残り{2:.2f}%です。".format(d.month, d.year, x)
        b.update(month_msg)

    # 誕生日おめっせーじ　たぶんキレられる
    if d.hour is 0:
        birth_key = "{0:0>2}{1:0>2}".format(d.month, d.day)
        if birth_key in birthday.birthday_list:
            for name, amalist in birthday.birthday_list[birth_key].items():
                msg = "本日は @{0} 様のお誕生日です。おめでとうございます。\n".format(name)
                if len(amalist):
                    msg += "皆様、さあ → {0}".format(amalist)
                b.update(msg)

    b.refollow() #　リフォロー

if __name__ =="__main__":
    # debug用
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import webapi.beluga_api as beluga_api
    import settings
    post_time_beluga()