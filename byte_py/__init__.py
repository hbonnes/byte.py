import aiohttp
import byte_py.config as config
import byte_py.account as account
import byte_py.post as post


class ByteClient:

    def __init__(self, auth_token):
        self.user = None
        self.headers = {'User-Agent': config.USER_AGENT, 'Content-Type': config.CONTENT_TYPE,
                        'Authorization': auth_token}
        self.http_client = aiohttp.ClientSession()

    async def __aenter__(self):
        await self.get_user_data()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.close()

    async def create_request(self, method, url, data=None):
        async with self.http_client.request(method, url, headers=self.headers, data=data) as request_response:
            if request_response.status == 200:
                request_json = await request_response.json()
                return request_json
            else:
                return {'success': 0}

    async def get_user_data(self):
        user_json = await self.create_request("GET", config.ME_ENDPOINT)
        if user_json['success'] == 1:
            self.user = account.User(user_json['data'], self)
        else:
            self.user = None

    async def get_activity(self):
        async with aiohttp.ClientSession() as activity_session:
            async with activity_session.get(config.ACTIVITY_ENDPOINT,
                                            headers=self.headers) as activity_response:
                if activity_response.status == 200:
                    activity_json = await activity_response.json()
                    if activity_json['success'] == 1:
                        activity_collection = post.ActivityCollection(activity_json['data'], self.headers)
                        return activity_collection
                return None

    async def get_timeline(self):
        async with aiohttp.ClientSession() as timeline_session:
            print(config.TIMELINE_ENDPOINT)
            async with timeline_session.get(config.TIMELINE_ENDPOINT,
                                            headers=self.headers) as timeline_response:
                if timeline_response.status == 200:
                    timeline_json = await timeline_response.json()
                    if timeline_json['success'] == 1:
                        post_collection = post.PostCollection(timeline_json['data'], self.headers)
                        return post_collection
                return None

    async def get_latest(self):
        async with aiohttp.ClientSession() as latest_session:
            async with latest_session.get(config.LATEST_ENDPOINT, headers=self.headers) as latest_response:
                if latest_response.status == 200:
                    latest_response = await latest_response.json()
                    if latest_response['success'] == 1:
                        post_collection = post.PostCollection(latest_response['data'], self.headers)
                        return post_collection
                return None

    async def get_account(self, id):
        account_json = await self.create_request("GET", config.ACCOUNT_ENDPOINT.format(id))
        if account_json['success'] == 1:
            account_object = account.Account(account_json['data'], self)
            return account_object
        else:
            return None


class Token:

    def __init__(self, json_data):
        self.account_id = json_data['accountID']
        self.is_deactivated = json_data['isDeactivated']
        self.is_registered = json_data['isRegistered']
        self.token = json_data['token']

# s1l0x
