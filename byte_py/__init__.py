import aiohttp
import byte_py.config as config
import byte_py.account as account
import byte_py.post as post
import json


class ByteClient:

    def __init__(self, auth_token=None):
        self.user = None
        self.token = auth_token
        self.token_object = None
        self.headers = {'User-Agent': config.USER_AGENT, 'Content-Type': config.CONTENT_TYPE}

        if auth_token:
            self.headers['Authorization'] = auth_token

    async def authenticate(self, google_token):
        async with aiohttp.ClientSession() as auth_session:
            auth_parameters = {'provider': 'google', 'token': google_token}
            auth_headers = {'User-Agent': config.USER_AGENT, 'Content-Type': config.CONTENT_TYPE}

            async with auth_session.post(config.AUTH_ENDPOINT, data=json.dumps(auth_parameters),
                                         headers=auth_headers) as auth_response:
                if auth_response.status == 200:
                    auth_json = await auth_response.json()
                    if auth_json['success'] == 1:
                        user_token = Token(auth_json['data']['token'])
                        self.headers['Authorization'] = user_token.token
                        self.token_object = user_token
                        self.token = user_token.token

                        user = account.User(auth_json['data']['account'], self.headers)

                        self.user = user
                        return True
                return False

    async def get_user_data(self):
        async with aiohttp.ClientSession() as user_data_session:
            async with user_data_session.get(config.ACCOUNT_ENDPOINT, headers=self.headers) as user_data_response:
                if user_data_response.status == 200:
                    user_data_json = await user_data_response.json()
                    if user_data_json['success'] == 1:
                        user = account.User(user_data_json['data'], self.headers)
                        self.user = user

                        return user
                return None

    async def get_activity(self):
        async with aiohttp.ClientSession() as activity_session:
            async with activity_session.get(config.ACCOUNT_ACTIVITY_ENDPOINT,
                                            headers=self.headers) as activity_response:
                if activity_response.status == 200:
                    activity_json = await activity_response.json()
                    if activity_json['success'] == 1:
                        activity_collection = post.ActivityCollection(activity_json['data'], self.headers)
                        return activity_collection
                return None

    async def get_timeline(self):
        async with aiohttp.ClientSession() as timeline_session:
            print(config.ACCOUNT_TIMELINE_ENDPOINT)
            async with timeline_session.get(config.ACCOUNT_TIMELINE_ENDPOINT, headers=self.headers) as timeline_response:
                if timeline_response.status == 200:
                    timeline_json = await timeline_response.json()
                    if timeline_json['success'] == 1:
                        post_collection = post.PostCollection(timeline_json['data'], self.headers)
                        return post_collection
                return None

    async def get_latest(self):
        async with aiohttp.ClientSession() as latest_session:
            async with latest_session.get(config.ACCOUNT_LATEST_ENDPOINT, headers=self.headers) as latest_response:
                if latest_response.status == 200:
                    latest_response = await latest_response.json()
                    if latest_response['success'] == 1:
                        post_collection = post.PostCollection(latest_response['data'], self.headers)
                        return post_collection
                return None

    async def get_account(self, id):
        async with aiohttp.ClientSession() as account_session:
            async with account_session.get(config.OTHER_ACCOUNT_ENDPOINT.format(id), headers=self.headers) as account_response:
                if account_response.status == 200:
                    account_json = await account_response.json()
                    if account_json['success'] == 1:
                        account_object = account.Account(account_json['data'], self.headers)
                        return account_object
                return None


class Token:

    def __init__(self, json_data):
        self.account_id = json_data['accountID']
        self.is_deactivated = json_data['isDeactivated']
        self.is_registered = json_data['isRegistered']
        self.token = json_data['token']
