# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
import time
import threading
from slackclient import SlackClient
import settings
import re
import webapi.tell as tell
import webapi.beluga_api as beluga

logger = logging.getLogger(__name__)
AT_MESSAGE_MATCHER = re.compile(r'^\<@(\w+)\>:? (.*)$')


class Bot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._client = SlackClient(
            settings.SLACK_API_TOKEN
        )

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

        # TODO:このチャンネルの頭文字の意味が謎　beluga-snsのチャンネルは全部C 仕様がわからん
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

