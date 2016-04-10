# -*- coding: utf-8 -*-
from slacker import Slacker
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import datetime
try:
	import settings
except ImportError:
	print("from __main__ start")
import tenki
import time

def post_time_slack():
    d = datetime.datetime.today() 
 
    slack = Slacker(settings.SLACK_API_TOKEN)
    
    slack.chat.post_message('#random',"------------------------------     " + str(d.hour) + "時     ------------------------------", as_user=True)
    if d.hour == 6:
        s = tenki.getTenki(None)
        time.sleep(1)
        slack.chat.post_message('#random', s, as_user=True)

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import settings
    post_time_slack()
