from time import gmtime, strftime
from aip import AipSpeech
import speech_recognition as sr
import io
import os
import pyaudio
import wave
import contextlib

APP_ID = '17979193'
API_KEY = '0Dg66Ee200NW9quRvC7RiCIL'
SECRET_KEY = 'FpOqROogGSlolwOTiegSDDpMjBarLSVu'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def getFileContent(path):
    with open(path, 'rb') as fp:
        return fp.read()

if __name__ == '__main__':
    wavCounter = 0
    while True:
        r = sr.Recognizer()
        mic = sr.Microphone()
        print('Recording Started.')
        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        path = f'history/{wavCounter}.wav'
        with open(path, 'wb') as f:
            f.write(audio.get_wav_data(convert_rate = 16000))
        with contextlib.closing(wave.open(path, 'r')) as f: # Set time constraints
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            if duration > 55:
                wavCounter += 1
                print('Time too long')
                continue
        print('Rcording Stopped.')
        result = client.asr(getFileContent(path), 'wav', 16000, {'dev_pid': 1537, })
        with open('speechScript.txt', "a", encoding="utf-8") as f: # Reslove Unicode encoding error
            currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            try:
                f.write(currentTime + ': ' + result['result'][0] + '\n')
                print(result['result'][0])
            except:
                print('Recogition Failed.')
            f.close()
        wavCounter += 1
