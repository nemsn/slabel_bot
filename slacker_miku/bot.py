# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
import time
from datetime import datetime
from datetime import timedelta
import threading
from slackclient import SlackClient
import re
try:
    import webapi.tell as tell
    import webapi.beluga_api as beluga
except ImportError:
    print("dbug main start")

logger = logging.getLogger(__name__)
AT_MESSAGE_MATCHER = re.compile(r'^\<@(\w+)\>:? (.*)$')


class Bot(threading.Thread):
    def __init__(self, token):
        threading.Thread.__init__(self)
        self._client = SlackClient(token)

    def run(self):
        self._client.rtm_connect()
        logger.info('connected to slack RTM api')
        self.loop()

    def loop(self):
        while True:
            events = self._client.rtm_read()
            logger.debug(events)
            for event in events:
                if event.get('type') != 'message':
                    continue
                self._on_new_message(event)
            time.sleep(1)

    def _on_new_message(self, msg):
        # ignore edits
        subtype = msg.get('subtype', '')
        if subtype == u'message_changed':
            return

        # BOT自身の投稿かチェック
        botname = self._client.username
        try:
            msguser = self._client.users.get(msg['user'])
            username = msguser['name']
        except (KeyError, TypeError):
            if 'username' in msg:
                username = msg['username']  
            else:
                return

        if username == botname or username == u'slackbot':
            return

        msg_respond_to = self.filter_text(msg)
        if msg_respond_to:
            self.check_respond_command(msg_respond_to)
        else:
            self.check_listen_command(msg)

    def filter_text(self, msg):
        text = msg.get('text', '')
        channel = msg['channel']

        # TODO:このチャンネルの頭文字の意味が謎　CはチャンネルだがG？DMはDから始まる
        if channel[0] == 'C' or channel[0] == 'G':
            m = AT_MESSAGE_MATCHER.match(text)
            if not m:
                return
            atuser, text = m.groups()
            if atuser != self._client.id:
                # a channel message at other user
                return
            logger.debug('got an AT message: %s', text)
            msg['text'] = text
        else:
            m = AT_MESSAGE_MATCHER.match(text)
            if m:
                msg['text'] = m.group(2)
        return msg

    def check_respond_command(self, data):
        if "占い" in data['text']:
            text = tell.getUranai(data['text']) 
            self.send_webapi(data, text, True)

        elif "beluga" in data['text']:
            b = beluga.Beluga()
            text = ""
            tws = b.get_public()
            for t in tws:
                text += "\n{} \n{}".format(t.screen_name, t.text)
            self.send_webapi(data, text, True)

        elif "log" in data['text']:
            self.send_dm_with_log(data)

        else:
            self.send_webapi(data, "かわいい～", True)

    def check_listen_command(self, data):
        if "勃起" in data['text']:
            self.send_webapi(data, "いいね～")

    def send_webapi(self, data, text, replyflg=False):
        send_text = ""
        if replyflg:
            send_text = u'<@{}>: {}'.format(data['user'], text)
        else:
            send_text = text
        self._client.send_message(
        data['channel'],
        send_text)

    def send_dm_with_log(self, msg):
        if msg['channel'][0] != 'C' and msg['channel'][0] != 'G':
            return
        try:
            msguser = self._client.users.get(msg['user'])
            username = msguser['name']
        except (KeyError, TypeError):
            if 'username' in msg:
                username = msg['username']  
            else:
                return

        # TODO:oldest指定
        text = self.__make_log_text(msg['channel'], 100)
        if len(text) > 0:
            LOG_FILE_NAME = "log.txt"
            with open(LOG_FILE_NAME, "w", encoding="utf-8") as f:
                f.write(text)
            self._client.upload_file(os.path.abspath(LOG_FILE_NAME), LOG_FILE_NAME, "log" , msg['channel'])
            os.remove(LOG_FILE_NAME)
        else:
            self.send_webapi(msg, "ログがないよ～")

    def __make_log_text(self, channel_id, days_before):
        today = datetime.now()
        oldest = datetime(today.year, 
                          today.month, 
                          today.day,
                          0,0,0,0) - timedelta(days=days_before)
        oldest = time.mktime(oldest.timetuple())
        msg = ""
        readingflg = True
        while readingflg:
            data = self._client.get_history(channel_id, oldest=oldest, count=1000)
            if len(data['messages']) == 1000:
                oldest = data['messages'][0]['ts']
            else:
                readingflg = False 

            for m in reversed(data['messages']):
                if m['type'] == "message":
                    name = 'no name'
                    try:
                        name = self._client.users.get(m['user'])['name']
                    except (KeyError, TypeError):
                        if 'username' in m:
                            # 'bot_message'
                            name = m['username']
                        else:
                            continue
                    ts = datetime.fromtimestamp(float(m['ts']))
                    text = m['text']
                    # TODO:attachments pending 
                    #attachments = m['attachments']
                    msg += "\n{0}:{1}\n{2}\n".format(name, ts, text)
        return msg

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import settings
    import webapi.tell as tell
    import webapi.beluga_api as beluga
    sb = Bot(settings.SLACK_API_TOKEN)
    sb.setDaemon(True)
    sb.start()
    while True:
        time.sleep(1)
