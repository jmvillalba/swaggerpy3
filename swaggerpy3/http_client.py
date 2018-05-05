import aiohttp
import asyncio
import websockets

class AsyncHttpClient():
    def __init__(self):
        self.auth = None
        self.websockets = set()

    def set_basic_auth(self, host, username, password):
        self.auth = aiohttp.BasicAuth(login=username, password=password)
        self.session = aiohttp.ClientSession(auth=self.auth)

    async def close(self):
        self.session.close()

    async def request(self, method, url, params=None, data=None, headers=None):
        async with self.session.request(
                method, 
                url, 
                params=params, 
                data=data, 
                headers=headers
        ) as response:
            print(dir(response))
            print(response.headers)
            print(await response.text())

            #payload = await response.json()
            #response.raise_for_status()
            return response

    async def ws_connect(self, url, params=None):
        """Websocket-client based implementation.

        :return: WebSocket connection
        :rtype:  websocket.WebSocket
        """
        if params:
            joined_params = "&".join(["%s=%s" % (k, v)
                for (k, v) in list(params.items())])
            url += "?%s" % joined_params

        async with self.session.ws_connect(url) as ws:
            async for msg in ws:
                payload = msg.json()

                self.websockets.add(ws)
                return payload

