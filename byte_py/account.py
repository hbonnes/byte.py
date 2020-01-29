import datetime
import aiohttp
import byte_py.config as config
import json
import byte_py.post as post


class Account:
    """
    This class represents a Byte Account object and functions

    Attributes:
        json_data (string): The JSON representation of the data object
        client (ByteClient): The client object that holds the HTTP session
    """

    def __init__(self, json_data, client):

        self.json_data = json_data
        self.client = client

    def __repr__(self):
        return 'Account(): id="{0}"'.format(self.get_id(), self.get_username())

    """
    Returns the string ID of a user.
    """

    def get_id(self):
        return self.json_data['id']

    """
    Returns the string username of a user.
    """

    def get_username(self):
        return self.json_data['username']

    """
    Follows the Byte account.
    
    Returns:
        bool: Returns true if the request succeeded, otherwise returns false.
    """

    async def follow(self):
        follow_json = await self.client.create_request("PUT", config.ACCOUNT_FOLLOW_ENDPOINT.format(self.get_id()))
        if follow_json['success'] == 1:
            return True
        else:
            return False

    """
    Unfollows the Byte account.

    Returns:
        bool: Returns true if the request succeeded, otherwise returns false.
    """

    async def unfollow(self):
        follow_json = await self.client.create_request("DELETE", config.ACCOUNT_FOLLOW_ENDPOINT.format(self.get_id()))
        if follow_json['success'] == 1:
            return True
        else:
            return False

    """
    Reports the Byte account.
    
    Returns:
        bool: Returns true if the request succeeded, otherwise returns false.
    """

    async def report(self):
        report_data = {'reason': 'notinterested'}
        report_json = await self.client.create_request("POST", config.ACCOUNT_REPORT_ENDPOINT.format(self.get_id()),
                                                       json.dumps(report_data))
        if report_json['success'] == 1:
            return True
        else:
            return False

    """
    Blocks the Byte account.
    
    Returns:
        bool: Returns true if the request succeeded, otherwise returns false.
    """

    async def block(self):
        block_json = await self.client.create_request("PUT", config.ACCOUNT_BLOCK_ENDPOINT.format(self.get_id()))
        if block_json['success'] == 1:
            return True
        else:
            return False

    """
    Unblocks the Byte account.
    
    Returns:
        bool: Returns true if the request succeeded, otherwise returns false.
    """

    async def unblock(self):
        block_json = await self.client.create_request("DELETE", config.ACCOUNT_BLOCK_ENDPOINT.format(self.get_id()))
        if block_json['success'] == 1:
            return True
        else:
            return False

    """
    Gets the Posts of the Byte account.
    
    Returns:
        PostCollection: Returns a collection of Accounts and Posts from the user.
    """

    async def get_posts(self):
        async with aiohttp.ClientSession() as post_session:
            async with post_session.get(config.ACCOUNT_POSTS_ENDPOINT.format(self.id),
                                        headers=self.headers) as post_response:
                if post_response.status == 200:
                    post_json = await post_response.json()
                    if post_json['success'] == 1:
                        post_collection = post.PostCollection(post_json['data'], self.headers)
                        return post_collection
                return None


class User(Account):

    async def set_data(self, data):
        request_json = await self.client.create_request("PUT", config.ME_ENDPOINT, json.dumps(data))
        print(request_json)
        if request_json['success'] == 1:
            return True
        else:
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
        color_json = await self.client.create_request("GET", config.ME_COLOR_ENDPOINT)
        if color_json['success'] == 1:

            colors = {}
            for color in color_json['data']['colors']:
                color_object = Color(color)
                colors[color_object.id] = color_object

            return colors
        else:
            return None

    async def get_posts(self):
        async with aiohttp.ClientSession() as post_session:
            async with post_session.get(config.ME_POST_ENDPOINT, headers=self.headers) as post_response:
                if post_response.status == 200:
                    post_json = await post_response.json()
                    if post_json['success'] == 1:
                        posts = post.PostCollection(post_json['data'], self.headers)

                        return posts
                return None

    async def get_blocking(self):
        blocking_json = await self.client.create_request("GET", config.BLOCKING_ENDPOINT)
        if blocking_json['success'] == 1:
            accounts = []
            for account_json in blocking_json['data']['accounts']:
                account = Account(account_json, self.client)
                accounts.append(account)
            return accounts
        else:
            return []


class Color:

    def __init__(self, json_data):
        self.id = json_data['id']
        self.background = json_data['background']
        self.foreground = json_data['foreground']

    def __repr__(self):
        return 'Color() background="{0}", foreground="{1}"'.format(self.background, self.foreground)

# s1l0x
