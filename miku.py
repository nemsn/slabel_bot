# -*- coding:utf-8 -*-
import slacker_miku.bot as slack_bot
import beluga_miku.bot as beluga_bot
import webapi
import settings
import _thread
import sys
import time
import logging
import logging.config

def main():
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout, #filename
    }
    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)

    b_miku = beluga_bot.Bot()
    b_miku.setDaemon(True)
    b_miku.start()

    s_miku = slack_bot.Bot()
    s_miku.setDaemon(True)
    s_miku.start()

    keepactive()

def keepactive():
    while True:
        time.sleep(5)
        # ここでなんかやらせたい

if __name__ =="__main__":
    main()
