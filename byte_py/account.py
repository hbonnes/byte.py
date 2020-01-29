import datetime
import aiohttp
import byte_py.config as config
import json
import byte_py.post as post


class Account:

    def __init__(self, json_data, headers):

        self.background_color = json_data['backgroundColor']
        self.follower_count = json_data['followerCount']
        self.following_count = json_data['followingCount']
        self.foreground_color = json_data['foregroundColor']
        self.id = json_data['id']
        self.is_channel = json_data['isChannel']
        self.loop_count = json_data['loopCount']
        self.loop_consumed_count = json_data['loopsConsumedCount']
        self.registration_date = datetime.datetime.fromtimestamp(json_data['registrationDate'])
        self.username = json_data['username']
        self.headers = headers

        if 'displayName' in json_data:
            self.display_name = json_data['displayName']
        else:
            self.display_name = None

        if 'avatarURL' in json_data:
            self.avatar_url = json_data['avatarURL']
        else:
            self.avatar_url = None

    def __repr__(self):
        return 'Account(): id="{0}"'.format(self.id, self.username)

    async def follow(self):
        async with aiohttp.ClientSession() as follow_session:
            async with follow_session.put(config.OTHER_ACCOUNT_FOLLOW_ENDPOINT.format(self.id),
                                          headers=self.headers) as follow_response:
                if follow_response.status == 200:
                    follow_json = await follow_response.json()
                    if follow_json['success'] == 1:
                        return True
                return False

    async def unfollow(self):
        async with aiohttp.ClientSession() as follow_session:
            async with follow_session.delete(config.OTHER_ACCOUNT_FOLLOW_ENDPOINT.format(self.id),
                                             headers=self.headers) as follow_response:
                if follow_response.status == 200:
                    follow_json = await follow_response.json()
                    if follow_json['success'] == 1:
                        return True
                return False

    async def report(self):
        async with aiohttp.ClientSession() as report_session:
            report_data = {'reason': 'notinterested'}
            async with report_session.post(config.OTHER_ACCOUNT_REPORT_ENDPOINT.format(self.id), data=json.dumps(report_data), headers=self.headers) as report_response:
                if report_response.status == 200:
                    report_json = await report_response.json()
                    if report_json['success'] == 1:
                        return True
                return False

    async def block(self):
        async with aiohttp.ClientSession() as block_session:
            async with block_session.put(config.OTHER_ACCOUNT_BLOCK_ENDPOINT.format(self.id), headers=self.headers) as block_response:
                if block_response.status == 200:
                    block_json = await block_response.json()
                    if block_json['success'] == 1:
                        return True
                return False

    async def unblock(self):
        async with aiohttp.ClientSession() as block_session:
            async with block_session.delete(config.OTHER_ACCOUNT_BLOCK_ENDPOINT.format(self.id), headers=self.headers) as block_response:
                if block_response.status == 200:
                    block_json = await block_response.json()
                    if block_json['success'] == 1:
                        return True
                return False

    async def get_posts(self):
        async with aiohttp.ClientSession() as post_session:
            async with post_session.get(config.OTHER_ACCOUNT_POSTS_ENDPOINT.format(self.id), headers=self.headers) as post_response:
                if post_response.status == 200:
                    post_json = await post_response.json()
                    if post_json['success'] == 1:
                        post_collection = post.PostCollection(post_json['data'], self.headers)
                        return post_collection
                return None


class User(Account):

    async def set_data(self, data):
        async with aiohttp.ClientSession() as set_data_session:
            async with set_data_session.put(config.ACCOUNT_ENDPOINT, data=json.dumps(data),
                                            headers=self.headers) as set_data_response:
                if set_data_response == 200:
                    set_data_json = await set_data_response.json()
                    print(set_data_json)
                    if set_data_json['success'] == 1:
                        return True
                    else:
                        error_code = set_data_json['error']['code']
                        error_message = set_data_json['error']['message']
                        print('[ERROR] Error code {0}: {1}'.format(error_code, error_message))
                return False

    async def set_color(self, color_id):
        color_set_data = {'colorScheme': color_id}
        return await self.set_data(color_set_data)

    async def set_username(self, username):
        username_set_data = {'username': username}
        return await self.set_data(username_set_data)

    async def set_display_name(self, display_name):
        display_name_set_data = {'displayName': display_name}
        return await self.set_data(display_name_set_data)

    async def set_bio(self, bio):
        bio_set_data = {'bio': bio}
        return await self.set_data(bio_set_data)

    async def get_colors(self):
        async with aiohttp.ClientSession() as color_session:
            async with color_session.get(config.ACCOUNT_COLOR_ENDPOINT, headers=self.headers) as color_response:
                if color_response.status == 200:
                    color_json = await color_response.json()
                    if color_json['success'] == 1:

                        colors = {}
                        for color in color_json['data']['colors']:
                            color_object = Color(color)
                            colors[color_object.id] = color_object

                        return colors

                return None

    async def get_posts(self):
        async with aiohttp.ClientSession() as post_session:
            async with post_session.get(config.ACCOUNT_POST_ENDPOINT, headers=self.headers) as post_response:
                if post_response.status == 200:
                    post_json = await post_response.json()
                    if post_json['success'] == 1:
                        posts = post.PostCollection(post_json['data'], self.headers)

                        return posts
                return None

    async def get_blocking(self):
        async with aiohttp.ClientSession() as blocking_session:
            async with blocking_session.get(config.ACCOUNT_BLOCKING, headers=self.headers) as blocking_response:
                if blocking_response.status == 200:
                    blocking_json = await blocking_response.json()
                    if blocking_json['success'] == 1:
                        accounts = []
                        for account in blocking_json['data']['accounts']:
                            account_object = Account(account, self.headers)
                            accounts.append(account_object)
                        return accounts
                return None


class Color:

    def __init__(self, json_data):
        self.id = json_data['id']
        self.background = json_data['background']
        self.foreground = json_data['foreground']

    def __repr__(self):
        return 'Color() background="{0}", foreground="{1}"'.format(self.background, self.foreground)
