# -*- encoding:utf-8 -*-
import sys
import os
from urllib import request, parse
import json
import http.cookiejar
import time
import logging
import logging.config
import base64

logger = logging.getLogger(__name__)

class Timeline:
    tweet_id = 0
    likes_count = 0
    favorites_count = 0
    text = ""
    timeline_id = 0
    hashtag_title = ""
    user_id = 0
    screen_name = ""


class Beluga(object):
    """ belugaのログイン無しで利用出来るAPIコールクラス
    """
    def __init__(self):
        self.opener = request.build_opener()

    def _get_json_api(self, url, param=""):
        """ jsonデータ取得
        """
        data = parse.urlencode(param).encode(encoding='ascii')
        rsp = self.opener.open(url, data).read().decode('utf-8')
        return(json.loads(rsp))

    @staticmethod
    def _is_success(data):
        """ 辞書型のキーに'success'が含まれているか
        　　　含まれている場合、データがTrueか判定
        """
        if 'success' in data.keys():
            if data['success']:
                return True
            else:
                logger.debug("json success is not True: {}".format(data['message']))
        else:
            logger.debug("json data error")

        return False

    def _json_to_timeline(self, jsondata):
        """ json形式の辞書型からTimeline型に整形
            TODO:
        　　　ベルガから返ってくるjsonのパターンが複数ある
        　　　直下に['statuses']があるのと['data']['statuses']構造の2パターン…だといいな
        """
        L = []
        if self._is_success(jsondata):
            if 'statuses' in jsondata:
                for t in jsondata['statuses']:
                    tw = Timeline()
                    tw.tweet_id = t['id']
                    tw.likes_count = t['likes_count']
                    tw.favorites_count = t['favorites_count']
                    tw.timeline_id = t['timeline_id']
                    tw.text = t['text']
                    tw.user_id = t['user']['id']
                    tw.screen_name = t['user']['screen_name']
                    if 'hashtag_title' in t:
                        tw.hashtag_title = t['hashtag_title']
                    L.append(tw)
            elif 'data' in jsondata:
                if 'statuses' in jsondata['data']:
                    for t in jsondata['data']['statuses']:
                        tw = Timeline()
                        tw.tweet_id = t['id']
                        tw.likes_count = t['likes_count']
                        tw.favorites_count = t['favorites_count']
                        tw.timeline_id = t['timeline_id']
                        tw.text = t['text']
                        tw.user_id = t['user']['id']
                        tw.screen_name = t['user']['screen_name']
                        L.append(tw)
                if 'following' in jsondata['data']:
                    for t in jsondata['data']['following']:
                        tw = Timeline()
                        tw.user_id = t['id']
                        tw.screen_name = t['screen_name']
                        L.append(tw)
                elif 'followers' in jsondata['data']:
                    for t in jsondata['data']['followers']:
                        tw = Timeline()
                        tw.user_id = t['id']
                        tw.screen_name = t['screen_name']
                        L.append(tw)
            else:
                logger.debug(jsondata["message"])
        return L

    def get_user_id(self, screen_name):
        """ ユーザー名からユーザーIDを取得する
            取得できない場合-1を返す
        """
        url = 'http://beluga.fm/i/app/user_statuses.json'
        param = {'screen_name': screen_name }
        
        d = self._get_json_api(url, param)
        user_id = -1
        if self._is_success(d):
            user_id = d['data']['user']['id']

        return user_id

    def get_user_timeline(self, screen_name, user_id, since_id=None, max_id=None):
        """ ユーザーの投稿を取得する
        @param user_name 投稿を取得するユーザー名
        @param user_id user_nameに紐付いたユーザーID get_user_id()で取得可能
        @param since_id 読み込む始点の投稿ID. 0の場合は無視
        @param max_id 読み込む終点の投稿ID. 0の場合は無視
        """
        url = 'http://beluga.fm/i/statuses/user_timeline.json'
        param = {
            'screen_name': screen_name,
            'user_id': user_id
        }
        if since_id: param['since_id'] = since_id
        if max_id:   param['max_id'] = max_id

        d = self._get_json_api(url, param)
        return self._json_to_timeline(d)

    def get_room(self, room_name, since_id=None, max_id=None):
        """ ルームの投稿を取得する
        @param room_name 取得先のルーム名 #XXX の#は必要ない
        @param since_id 読み込む始点の投稿ID. 0の場合は無視
        @param max_id 読み込む終点の投稿ID. 0の場合は無視
        """
        url = "http://beluga.fm/i/statuses/hashtag_timeline.json"
        param = {
            'title': room_name
        }
        if max_id: param['max_id'] = max_id

        d = self._get_json_api(url, param)
        return self._json_to_timeline(d)

    def get_public(self, since_id=None, max_id=None, include_hashtags=True, include_home=True):
        """ 全ての投稿を取得する
        @param since_id 読み込む始点の投稿ID. 0の場合は無視
        @param max_id 読み込む終点の投稿ID. 0の場合は無視
        @param include_hashtags ルームへの投稿の取得も含めるか
        @prram include_home ホームへの投稿も含めるか
        """
        url = "http://beluga.fm/i/statuses/public_timeline.json"
        param = {}
        if include_hashtags:
            param['include_public_hashtags'] = True
        if include_home:
            param['include_home'] = True
        if since_id:
            param['since_id'] = since_id
        if max_id:
            param['max_id'] = max_id
        L = self._get_json_api(url, param)
        return self._json_to_timeline(L)

    def get_following(self, screen_name):
        """ フォローしている垢ズ取得
        @param screen_name 対象ユーザー名
        """
        url = "http://beluga.fm/i/app/user_following.json"
        param = {'screen_name': screen_name}
        d = self._get_json_api(url, param)
        return self._json_to_timeline(d)

    def get_followers(self, screen_name):
        """ フォローされている垢ズ取得
        @param screen_name 対象ユーザー名
        """
        url = "http://beluga.fm/i/app/user_followers.json"
        param = {'screen_name': screen_name}
        d = self._get_json_api(url, param)
        return self._json_to_timeline(d)


class BelugaUser(Beluga):
    """ belugaのログイン垢のみで利用出来るAPIコールクラス
    @memo ログインできなかった場合、現状では例外投げてる。基本クラスだけでも使えたほうがいいかどうか微妙
    """
    def __init__(self, name, password):
        Beluga.__init__(self)
        self.id = -1
        self.name = name
        self.password = password
        self.authenticity_token = ""
        self.cookiefile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
        self.cj = http.cookiejar.LWPCookieJar()
        if os.path.exists(self.cookiefile):
            self.cj.load(self.cookiefile)

        self.opener = request.build_opener(request.HTTPCookieProcessor(self.cj))

        if not self._login(self.name, self.password):
            raise Exception("Beluga Login Error.")

    def _save_cookie(self):
        self.cj.save(self.cookiefile, True, True)
        logger.debug("cookie save")

    def _login(self, screen_name, password):
        """ Belugaへログインする
        """
        if self._set_authenticity_token(self.name):
            return True

        token = self._get_login_page_token()
        logger.debug("login page token: {}".format(token))

        url = "http://beluga.fm/i/account/login.json"
        param = {
            'screen_name': screen_name,
            'authenticity_token': token,
            "password": password
        }
        d = self._get_json_api(url, param)
        if self._is_success(d):
            if self._set_authenticity_token(self.name):
                self._save_cookie()
                return True

        return False

    def _get_login_page_token(self):
        """ loginページからtokenを取得する(http://beluga.fm/login)
        """
        url = "http://beluga.fm/login"

        d = self.opener.open(url)
        res = d.read().decode('utf-8')

        login_token = ""
        try:
            seekstr = 'authenticity_token = "'
            start_point = res.index(seekstr)
            s = res[start_point + len(seekstr):]
            end_point = s.index('"')
            login_token = s[:end_point]
        except ValueError:
            logger.debug("beluga loginpage token ValueError")
            return None

        return login_token

    def _set_authenticity_token(self, sname):
        """ ユーザー情報からトークンを取得しインスタンス変数にセット
        """
        url = 'http://beluga.fm/i/app/user_statuses.json'
        param = {
            'screen_name': sname
        }
        d = self._get_json_api(url, param)
        if self._is_success(d):
            self.id = d['data']['user']['id']

            # ログイン済みならインスタンス変数にトークンをセット
            if d['data']['authenticity_token'] is not 0:
                self.authenticity_token = d['data']['authenticity_token']
                return True

        return False

    def logout(self):
        """ Belugaからログアウトする
        """
        url = "http://beluga.fm/i/account/logout.json"
        param = {
            'authenticity_token': self.authenticity_token
        }
        self._get_json_api(url, param)
        self._save_cookie()

    def update(self, text):
        """ 投稿
        """
        url = "http://beluga.fm/i/statuses/update.json"
        param = {
            'authenticity_token': self.authenticity_token,
            'text': text
        }
        self._get_json_api(url, param)
        time.sleep(3) #連投規制用タイマー

    def destroy(self, delete_id):
        """ 投稿削除
        """
        url = "http://beluga.fm/i/statuses/destroy.json"
        param = {
            'screen_name': self.name,
            'authenticity_token': self.authenticity_token,
            'status_id': delete_id
        }
        self._get_json_api(url, param)

    def get_reply(self, since_id=None):
        """ リプライ取得
        @note authenticity_tokenを指定しないが
        　　　　　クッキーがないとログインしてくださいと返ってくる
        　　　　　since_idを指定しても意味なし？get_mention_timeline使ったほうが良いっぽい
        """
        url = "http://beluga.fm/i/app/mentions.json"
        param = {}
        if since_id: param = {"since_id": since_id}

        d = self._get_json_api(url)
        return self._json_to_timeline(d)

    def get_mention_timeline(self, since_id=None, max_id=None, count=None, until=None):
        """ リプライ取得　
        @param since_id
        @param max_id
        @param count 意味あるのかこれ1
        @param until 意味あるのかこれ2
        @note authenticity_tokenを指定しないが
        　　　　　クッキーがないとログインしてくださいと返ってくる
        """
        url = "http://beluga.fm/i/statuses/mentions_timeline.json"
        param = {}
        if count:
            param['count'] = count
        if since_id:
            param['since_id'] = since_id
        if max_id:
            param['max_id'] = max_id
        if until:
            param['until'] = until

        d = self._get_json_api(url, param)
        return self._json_to_timeline(d)


    def favorite(self, status_id):
        """ お気に入り登録
        @param status_id ふぁぼりたい投稿ID
        """
        url = "http://beluga.fm/i/favorites/create.json"
        param = {
            'status_id': status_id,
            'authenticity_token': self.authenticity_token
        }
        self._get_json_api(url, param)

    def likes(self, status_id, count=1):
        """ いいね登録
        @param status_id いいねをつけたい投稿ID
        @param count つけたいいねの数　最大10
        """
        url = "http://beluga.fm/i/likes/create.json"
        param = {
            'status_id': status_id,
            'count': count,
            'authenticity_token': self.authenticity_token
        }
        self._get_json_api(url, param)

    def follow(self, user_id):
        """ フォローする
        """
        url = "http://beluga.fm/i/friendships/create.json"
        param = {
            'user_id': user_id,
            'authenticity_token': self.authenticity_token
        }
        self._get_json_api(url, param)


    def set_profile(self, name, description, tags=None):
        """ プロフィールを変更する
        @name 名前
        @description 説明文
        @tags タグ
        @note TODO:tagsの複数指定ってどうやるんだろう　リストやタプルはダメだった
        """
        url = "http://beluga.fm/i/account/update_profile.json"
        param = {'authenticity_token': self.authenticity_token}
        if description:
            param['description'] = description
        if name:
            param['name'] = name
        if tags:
            param['tags'] = tags

        d = self._get_json_api(url, param)

    def set_profile_image(self, file_path):
        """ プロフィール画像を変更する
        @file_patj プロフィール画像に設定したい画像ファイルパス
        """
        if not os.path.exists(file_path):
            logger.debug("image file not found")
            return 

        url = "http://beluga.fm/i/account/update_profile_image.json"
        data_uri = "base64,"
        with open(file_path, 'rb') as f:
            data = base64.b64encode(f.read())
            data_uri += data.decode("ascii")
        param = {
            'authenticity_token': self.authenticity_token,
            'base64_encoded_image' : data_uri
        } 
        d = self._get_json_api(url, param)
        self._is_success(d)

    def set_crop_profile_image(self, file_path, top, left, width, height):
        """ プロフィール画像をクロップ追加で変更する
            TODO:画像を送っても反映されず、現在設定されているアイコンの切り抜きが行われる
        """
        if not os.path.exists(file_path):
            logger.debug("image file not found")
            return 

        url = "http://beluga.fm/i/account/crop_profile_image.json"
        data_uri = "base64,"
        with open(file_path, 'rb') as f:
            data = base64.b64encode(f.read())
            data_uri += data.decode("ascii")
        param = {
            'authenticity_token': self.authenticity_token,
            'base64_encoded_image' : data_uri,
            'top': top,
            'left': left,
            'width': width,
            'height': height
        } 
        d = self._get_json_api(url, param)
        self._is_success(d)

    def get_public_all(self, since_id=None, max_id=None, count=None, until=None, include_hashtags=True, include_home=True):
        """ 全ての投稿を取得する
        @param since_id 読み込む始点の投稿ID. 0の場合は無視
        @param max_id 読み込む終点の投稿ID. 0の場合は無視
        @param include_hashtags ルームへの投稿の取得も含めるか
        @param include_home ホームへの投稿も含めるか
        """
        url = "http://beluga.fm/i/search/all.json"
        param = {}
        if include_hashtags:
            param['include_public_hashtags'] = True
        if include_home:
            param['include_home'] = True
        if since_id:
            param['since_id'] = since_id
        if max_id:
            param['max_id'] = max_id
        if count:
            param['count'] = count
        if until:
            param['until'] = until

        L = self._get_json_api(url, param)
        return self._json_to_timeline(L)


class BelugaTool(BelugaUser):
    """ Belugaに対して行いたい処理まとめ
    """
    def __init__(self, name, password):
        BelugaUser.__init__(self, name, password)

    def delete_tweet_all(self, stared_delete_flg=False, faved_delete_flg=False):
        """ 投稿全削除
        @param stared_delete_flg いいね！がついた投稿も削除したい場合はTrueに指定する
        @param faved_delete_flg  ふぁぼがついた投稿も削除したい場合はTrueに指定する
        """
        max_id = 0
        endflg = False
        while not endflg:
            L = self.get_user_timeline(self.name, self.id, max_id=max_id)
            if len(L) is 0:
                endflg = True
            for t in L:
                max_id = t.tweet_id
                # いいね！が付いてる投稿は消したくない
                if not stared_delete_flg:
                    if t.likes_count > 0:
                        continue
                # ふぁぼられた投稿は消したくない
                if not faved_delete_flg:
                    if t.favorites_count > 0:
                        continue
                self.destroy(t.tweet_id)

    def get_best_star_and_fav(self, user_name):
        """ ユーザーのふぁぼ数最大の投稿といいね数最大の投稿を取得する
            @memo 指定されたユーザの全投稿を取ってくるため総投稿数に比例して時間がかかる
            @param user_name 取得したいユーザーのscreen_name
            @return いいねベストのTimeline, ふぁぼベストのTimelineの二つと
                    総いいね数、総ふぁぼ数を返す
        """
        user_id = self.get_user_id(user_name)
        max_id = 0
        endflg = False
        like_best = Timeline()
        fav_best = Timeline()
        total_like = 0
        total_fav = 0
        while not endflg:
            time.sleep(0.1)
            L = self.get_user_timeline(user_name, user_id, max_id=max_id)
            if len(L) is 0: endflg = True
            for t in L:
                max_id = t.tweet_id
                if t.favorites_count > fav_best.favorites_count:
                    fav_best = t
                if t.likes_count > like_best.likes_count:
                    like_best = t
                total_like += t.likes_count
                total_fav += t.favorites_count

        if like_best.likes_count is 0:
            like_best = None
        if fav_best.favorites_count is 0:
            fav_best = None
            
        return(like_best, fav_best, total_like, total_fav)

    def likes_all_in_room(self, room_name):
        """ 指定したルームの投稿全てにいいね10個つける
        @param room_name ルーム名（#XXX #は要らない）
        """
        endflg = False
        max_id = 0
        while not endflg:
            L = self.get_room(room_name, max_id=max_id)
            if len(L) is 0: endflg = True
            for t in L:
                max_id = t.tweet_id
                self.likes(t.tweet_id, 10)

    def refollow(self):
        """ フォロー返し
        """
        following_ids = set([t.user_id for t in self.get_following(self.name)])
        followers_ids = set([t.user_id for t in self.get_followers(self.name)])

        # フォローされているがフォローしていないユーザーIDを絞り込む
        not_following_ids = followers_ids - following_ids
        for user_id in not_following_ids:
            self.follow(user_id)

    def get_follow_info(self, screen_name):
        """ フォロー状況取得
        @param user_name 取得したいユーザーのscreen_name
        @return フォローを返されていないTimeline型リスト,
                フォローし返していないTimeline型リストの二つをタプルで返す
        """
        following_tws = self.get_following(screen_name)
        followed_tws = self.get_followers(screen_name)

        # ユーザーIDだけ抜き取る
        following_id = set([t.user_id for t in following_tws])
        followed_id = set([t.user_id for t in followed_tws])

        # フォローしているがフォローを返されていない垢のみ抜き出す            
        no_following_id = following_id - followed_id
        no_following_tw = []
        for user_id in no_following_id:
            no_following_tw += filter(lambda tw: tw.user_id is user_id, following_tws)

        # フォローされているがフォローし返していない垢のみ抜き出す
        no_followed_id = followed_id - following_id
        no_followed_tws = []
        for user_id in no_followed_id:
            no_followed_tws += filter(lambda tw: tw.user_id is user_id, followed_tws) 

        return (no_following_tw, no_followed_tws)

def main():
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG, # logging.INFO
        #'filename': "debug.txt",
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)
    logging.getLogger().setLevel(logging.DEBUG)

    b = BelugaTool("screen_name", "password")

if __name__ == "__main__":
    main()
