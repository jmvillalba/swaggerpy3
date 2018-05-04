import aiohttp
import asyncio
import websockets

class AsyncHttpClient():
    def __init__(self):
        self.auth = None
        self.websockets = set()

    def set_basic_auth(self, host, username, password):
        self.auth = aiohttp.BasicAuth(login=username, password=password)
        self.__session = aiohttp.ClientSession(auth=self.auth)

    async def request(self, method, url):
        async with self.__session.request(method, url) as request:
            print(dir(request))
            print(request.headers)
            print(await request.text())

            payload = await request.json()
            request.raise_for_status()
            return payload

    async def ws_connect(self, url, params=None):
        """Websocket-client based implementation.

        :return: WebSocket connection
        :rtype:  websocket.WebSocket
        """
        if params:
            joined_params = "&".join(["%s=%s" % (k, v)
                for (k, v) in list(params.items())])
            url += "?%s" % joined_params

        async with self.__session.ws_connect(url) as ws:
            async for msg in ws:
                payload = msg.json()

                self.websockets.add(ws)
                return payload

