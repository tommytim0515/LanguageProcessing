import io
import os
import sys
import wave
import contextlib
import wss
import websocket
import ssl
import json
import datetime
import hashlib
import base64
import hmac
import time
import _thread as thread
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from time import mktime
from datetime import datetime

# Define the path of the files
path = '../source/'

APP_ID = '5dee0b74'
APP_SECRET = '957f11122a782284b3d10b520de6ff32'
API_KEY = 'ff7c2fae0e620b6f71f405d937aaaaaf'
WEB_SOCKET = 'wss://iat-api.xfyun.cn/v2/iat'
HOST = 'iat-api.xfyun.cn'
REQUEST_LINE = 'GET /v2/iat HTTP/1.1'

STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2

FILE_NAME = ''


class Ws_Param(object):
    # Initialize
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # Common parameters
        self.CommonArgs = {"app_id": self.APPID}
        # Business parameters
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn",
                             "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    # Generate URL
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # Generate time with format RFC1123
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # Make signature
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # Hmac-sha256 Encryption
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(
            signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # Request authorization
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # Generate URL
        url = url + '?' + urlencode(v)
        return url


# Process the message receiving from websocket
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:
            data = json.loads(message)["data"]["result"]["ws"]
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            with open('result.txt', "a", encoding="utf-8") as f:
                f.write(result)
                if result == '\u3002' or result == '\uff1f':
                    f.write('\n')
                f.close()
    except Exception as e:
        print("receive msg,but parse exception:", e)


# Error warning
def on_error(ws, error):
    print("### error:", error)


# Close notification
def on_close(ws):
    print("### closed ###")


# Websocket connection establishment
def on_open(ws):
    def run(*args):
        frameSize = 8000  # Size of each frame of audio
        intervel = 0.04  # Interval of sending the audio (seconds)
        # Audio status information, identifying whether the audio is the first, continue, or last frame
        status = STATUS_FIRST_FRAME
        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # File finished
                if not buf:
                    status = STATUS_LAST_FRAME
                # Process the first frame
                # Send audio with business parameters
                # APP_ID is needed when sending the first frame
                if status == STATUS_FIRST_FRAME:
                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # Process the middle frame
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # Process the last frame
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # Analog sampling interval
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())


def main():
    global FILE_NAME, wsParam
    while True:
        for fileName in os.listdir(path):
            FILE_NAME = fileName
            with open('result.txt', "a", encoding="utf-8") as f:
                f.write(fileName + ': ')
                f.close()
            with contextlib.closing(wave.open(path + fileName, 'r')) as timeChecker:
                frames = timeChecker.getnframes()
                rate = timeChecker.getframerate()
                duration = frames / float(rate)
                if duration > 55:
                    print(fileName + ': Time too loog.')
                    continue
            wsParam = Ws_Param(APPID=APP_ID, APIKey=API_KEY,
                               APISecret=APP_SECRET, AudioFile=path + fileName)
            websocket.enableTrace(False)
            wsUrl = wsParam.create_url()
            ws = websocket.WebSocketApp(
                wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
            ws.on_open = on_open
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            print(fileName + ': Finished.')


if __name__ == '__main__':
    main()
    print('Recognition Finished.')
