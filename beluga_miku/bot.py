# -*- coding:utf-8 -*-
import datetime
import time
import sys, os
import logging
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    import webapi.beluga_api as beluga_api
    import webapi.tell as tell
    import settings
except ImportError:
    print("from __main__ start")

logger = logging.getLogger(__name__)


class Bot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._client = beluga_api.BelugaTool(settings.BELUGA_BOT_NAME, settings.BELUGA_BOT_PASSWORD)
        self._reply_id_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reply_id.txt")
        self._last_reply_id = 0
        try:
            with open(self._reply_id_file, 'r+') as f:
                for s in f:
                    self._last_reply_id = int(s)
        except FileNotFoundError:
            with open(self._reply_id_file, 'w') as f:
                logger.info('Can not open file %s', self._reply_id_file)

    def run(self):
        self.loop()

    def loop(self):
        while True:
            self._check_reply()
            time.sleep(10)

    def _check_reply(self):
        """ リプライで特定の文字に反応させる
        """
        reply_tws = self._client.get_mention_timeline(self._last_reply_id)
        for tw in reversed(reply_tws):
            # 前回取得したリプライよりも新規のリプライかチェック
            if tw.tweet_id > self._last_reply_id:
                if "best" in tw.text:
                    self._post_best_tweet(tw.screen_name)
                if "follow" in tw.text:
                    self._post_follow_info(tw.screen_name)
                if "fortune" in tw.text:
                    self._post_urani(tw)

                self._last_reply_id = tw.tweet_id

        if len(reply_tws) > 0:
            with open(self._reply_id_file, 'w') as f:
                f.write(str(self._last_reply_id))

    def _post_best_tweet(self, screen_name):
        """ いいね、ふぁぼ、それぞれの最多投稿をリプライ相手に飛ばす
            重い、連投されたら死ぬ　でもいいや
        """
        likes_t, favs_t = self._client.get_best_star_and_fav(screen_name)
        post_msg = "@{0} \n".format(screen_name)
        if likes_t:
            post_msg += "likes: {0} \n{{{1}}}\n".format(likes_t.likes_count, likes_t.tweet_id)
        else:
            post_msg += "likes not found.\n"

        if favs_t:
            post_msg += "favs: {0} \n{{{1}}}\n".format(favs_t.favorites_count, favs_t.tweet_id)
        else:
            post_msg += "favs not found.\n"

        self._client.update(post_msg)

    def _post_follow_info(self, screen_name):
        """ リプライ相手のフォロー関係を投稿
        """
        no_following_L, no_followed_L = self._client.get_follow_info(screen_name)

        post_msg = "@{0} \nフォローされていないユーザー\n".format(screen_name)
        for user in no_following_L:
            post_msg += user.screen_name + ", "

        post_msg += "\nフォローしていないユーザー\n".format(screen_name)
        for user in no_followed_L:
            post_msg += user.screen_name + ", "

        self._client.update(post_msg)

    def _post_urani(self, timeline):
        """ 占いを投稿
        """
        text = tell.getUranai(timeline.text)
        post_msg = "@{0} {1}".format(timeline.screen_name, text)
        self._client.update(post_msg)

if __name__ =="__main__":
    # debug用
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import webapi.beluga_api as beluga_api
    import webapi.tell as tell
    import settings

    b = Bot()
    b.run()
