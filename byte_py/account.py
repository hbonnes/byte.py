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


class Color:

    def __init__(self, json_data):
        self.id = json_data['id']
        self.background = json_data['background']
        self.foreground = json_data['foreground']

    def __repr__(self):
        return 'Color() background="{0}", foreground="{1}"'.format(self.background, self.foreground)
