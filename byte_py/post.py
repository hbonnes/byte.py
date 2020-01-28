import aiohttp
import byte_py.account as account
import datetime
import json
import byte_py.config as config


class ActivityCollection:

    def __init__(self, activity_data, headers):
        accounts = {}
        activities = []
        for account_id in activity_data['accounts']:
            account_object = account.Account(activity_data['accounts'][account_id], headers)
            accounts[account_id] = account_object

        for activity in activity_data['activity']:
            activity_object = Activity(activity)
            activities.append(activity_object)

        self.accounts = accounts
        self.activities = activities


class Activity:

    def __init__(self, activity_json):
        self.body = activity_json['body']
        self.date = datetime.datetime.utcfromtimestamp(activity_json['date'])
        self.id = activity_json['id']
        self.is_unread = activity_json['isUnread']
        self.type = activity_json['type']


class PostCollection:

    def __init__(self, post_data, headers):
        accounts = {}
        posts = []
        for account_id in post_data['accounts']:
            account_object = account.Account(post_data['accounts'][account_id], headers)
            accounts[account_id] = account_object

        for post in post_data['posts']:
            post_object = Post(post, headers)
            posts.append(post_object)

        self.accounts = accounts
        self.posts = posts


class Post:

    def __init__(self, json_data, headers):
        self.allow_curation = json_data['allowCuration']
        self.allow_remix = json_data['allowRemix']
        self.caption = json_data['caption']
        self.data = datetime.datetime.utcfromtimestamp(json_data['date'])
        self.id = json_data['id']
        self.like_count = json_data['likeCount']
        self.liked_by_me = json_data['likedByMe']
        self.mentions = json_data['mentions']
        self.rebyted_by_me = json_data['rebytedByMe']
        self.thumb_source = json_data['thumbSrc']
        self.type = json_data['type']
        self.video_source = json_data['videoSrc']

        self.headers = headers

        if 'category' in json_data:
            self.category = json_data['category']
        else:
            self.category = None

        if 'comments' in json_data:
            self.comments = json_data['comments']
        else:
            self.comments = None

    def __repr__(self):
        return 'Post(): id="{0}"'.format(self.id, self.caption)

    async def like(self):
        async with aiohttp.ClientSession() as like_session:
            print(config.POST_LIKE_ENDPOINT.format(self.id))
            async with like_session.put(config.POST_LIKE_ENDPOINT.format(self.id),
                                        headers=self.headers) as like_response:
                if like_response.status == 200:
                    like_json = await like_response.json()
                    if like_json['success'] == 1:
                        return True
                return False

    async def unlike(self):
        async with aiohttp.ClientSession() as like_session:
            print(config.POST_LIKE_ENDPOINT.format(self.id))
            async with like_session.delete(config.POST_LIKE_ENDPOINT.format(self.id),
                                           headers=self.headers) as like_response:
                if like_response.status == 200:
                    like_json = await like_response.json()
                    if like_json['success'] == 1:
                        return True
                return False

    async def comment(self, comment):
        async with aiohttp.ClientSession() as comment_session:
            comment_data = {'body': comment, 'postID': self.id, 'stubId': str(datetime.datetime.utcnow())}

            async with comment_session.post(config.POST_COMMENT_ENDPOINT.format(self.id), data=json.dumps(comment_data),
                                            headers=self.headers) as comment_response:
                if comment_response.status == 200:
                    comment_json = await comment_response.json()
                    if comment_json['success'] == 1:
                        return True
                return False

    async def delete(self):
        async with aiohttp.ClientSession() as delete_session:
            async with delete_session.delete(config.POST_ENDPOINT.format(self.id),
                                             headers=self.headers) as delete_response:
                if delete_response.status == 200:
                    delete_json = await delete_response.json()
                    if delete_json['success'] == 1:
                        return True
                return False
