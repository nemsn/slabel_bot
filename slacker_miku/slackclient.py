# -*- coding: utf-8 -*-
import os
import json
import logging
import time
import slacker

from websocket import (
    create_connection, WebSocketException, WebSocketConnectionClosedException
)

logger = logging.getLogger(__name__)

class SlackClient(object):
    def __init__(self, token, bot_icon=None, bot_emoji=None, connect=True):
        self.token = token
        self.bot_icon = bot_icon
        self.bot_emoji = bot_emoji
        self.username = None
        self.id = None
        self.domain = None
        self.websocket = None
        self.users = {}
        self.channels = {}
        self.connected = False

        if connect:
            self.rtm_connect()

    def rtm_connect(self):
        reply = slacker.Slacker(self.token).rtm.start().body
        self.parse_slack_login_data(reply)

    def reconnect(self):
        while True:
            try:
                self.rtm_connect()
                logger.warning('reconnected to slack rtm websocket')
                return
            except:
                logger.exception('failed to reconnect')
                time.sleep(1)

    def parse_slack_login_data(self, login_data):
        self.domain = login_data['team']['domain']
        self.username = login_data['self']['name']
        self.id = login_data['self']['id']
        self.users = dict((u['id'], u) for u in login_data['users'])
        self.parse_channel_data(login_data['channels'])
        self.parse_channel_data(login_data['groups'])
        self.parse_channel_data(login_data['ims'])
        try:
            self.websocket = create_connection(login_data['url'])
            self.websocket.sock.setblocking(0)
        except:
            raise SlackConnectionError

    def parse_channel_data(self, channel_data):
        self.channels.update({c['id']: c for c in channel_data})

    def send_to_websocket(self, data):
        """Send (data) directly to the websocket."""
        data = json.dumps(data)
        self.websocket.send(data)

    def websocket_safe_read(self):
        """Returns data if available, otherwise ''. Newlines indicate multiple messages """
        data = ''
        while True:
            try:
                data += '{0}\n'.format(self.websocket.recv())
            except WebSocketException as e:
                if isinstance(e, WebSocketConnectionClosedException):
                    logger.warning('lost websocket connection, try to reconnect now')
                else:
                    logger.warning('websocket exception: %s', e)
                self.reconnect()
            except:
                return data.rstrip()

    def rtm_read(self):
        json_data = self.websocket_safe_read()
        data = []
        if json_data != '':
            for d in json_data.split('\n'):
                data.append(json.loads(d))
        return data

    def rtm_send_message(self, channel, message, attachments=None):
        message_json = {
            'type': 'message',
            'channel': channel,
            'text': message,
            'attachments': attachments
            }
        self.send_to_websocket(message_json)

    def send_message(self, channel, message, attachments=None):
        slacker.Slacker(self.token).chat.post_message(
                channel,
                message,
                username=self.username,
                icon_url=self.bot_icon,
                icon_emoji=self.bot_emoji,
                attachments=attachments,
                as_user=True)

    def get_channel(self, channel_id):
        return Channel(self, self.channels[channel_id])

    def find_user_by_name(self, username):
        for userid, user in iteritems(self.users):
            if user['name'] == username:
                return userid

    def react_to_message(self, emojiname, channel, timestamp):
        slacker.Slacker(self.token).reactions.add(
            name=emojiname,
            channel=channel,
            timestamp=timestamp)

