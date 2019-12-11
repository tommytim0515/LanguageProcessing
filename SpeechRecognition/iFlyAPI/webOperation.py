import asyncio
import websockets
import hmac
import hashlib
import base64
import json
from urllib.parse import urlencode, unquote, urlparse, parse_qsl, ParseResult
from time import strftime, gmtime

APP_ID = '5dee0b74'
APP_SECRET = '957f11122a782284b3d10b520de6ff32'
API_KEY = 'ff7c2fae0e620b6f71f405d937aaaaaf'
WEB_SOCKET = 'wss://iat-api.xfyun.cn/v2/iat'
HOST = 'iat-api.xfyun.cn'
REQUEST_LINE = 'GET /v2/iat HTTP/1.1'


def generateURL():
    currentTime = strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime())
    signature = 'host: iat-api.xfyun.cn\ndate: ' +\
        currentTime +\
        '\nGET /v2/iat HTTP/1.1'
    print(signature)
    signature = 'host: iat-api.xfyun.cn\ndate: Wed, 10 Jul 2019 07:35:43 GMT\nGET /v2/iat HTTP/1.1'
    signatureSha = hmac.new(bytes(APP_SECRET, 'latin-1'), msg = bytes(signature, 'latin-1'), digestmod = hashlib.sha256).hexdigest()
    print(signatureSha)
    encodedBytes = base64.urlsafe_b64encode(signatureSha.encode('utf-8'))
    encodedSig = str(encodedBytes, 'utf-8')
    print(encodedSig)
    authorizeOrigin = 'api_key="ff7c2fae0e620b6f71f405d937aaaaaf", algorithm="hmac-sha256", headers="host date request-line", signature="' +\
        encodedSig + '"'
    authEncodedBytes = base64.urlsafe_b64encode(authorizeOrigin.encode('utf-8'))
    encodeAuthrize = str(authEncodedBytes, 'utf-8')
    urlParameters = {
        'authorization': encodeAuthrize,
        'data': currentTime,
        'host': HOST
    }
    url = WEB_SOCKET + urlencode(urlParameters)
    print('Ready to send:\n' + url + '\n')
    return url


if __name__ == '__main__':
    print('(' + strftime("%a, %d %b %Y %H:%M:%S GMT", gmtime()) + ')')
    async def hello(url):
        async with websockets.connect(url) as websocket:
            print('Connected')
            await websocket.send("Hello world!")
            await websocket.recv()
    jsonExample = {
        "common": {
            "app_id": "123456"
        },
        "business": {
            "language": "zh_cn",
            "domain": "iat",
            "accent": "mandarin"
        },
        "data": {
            "status": 0,
            "format": "audio/L16;rate=16000",
            "encoding": "raw",
            "audio": "exSI6ICJlbiIsCgkgICAgInBvc2l0aW9uIjogImZhbHNlIgoJf..."
        }
    }
    # print(json.dumps(jsonExample))
    asyncio.get_event_loop().run_until_complete(hello(generateURL()))
