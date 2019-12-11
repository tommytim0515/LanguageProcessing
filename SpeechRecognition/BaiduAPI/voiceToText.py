from aip import AipSpeech
import io # Resolve Unicode encoding error
import os
import sys
import wave
import contextlib

# Information of Web API
APP_ID = '17979193'
API_KEY = '0Dg66Ee200NW9quRvC7RiCIL'
SECRET_KEY = 'FpOqROogGSlolwOTiegSDDpMjBarLSVu'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# Define the path of the files
path = '../source/' 

# Read voice files
def getFileContent(path):
    with open(path, 'rb') as fp:
        return fp.read()

def main():
    for fileName in  os.listdir(path):
        with contextlib.closing(wave.open(path + fileName, 'r')) as timeCheker: # Set time constraints
            frames = timeCheker.getnframes()
            rate = timeCheker.getframerate()
            duration = frames / float(rate)
            if duration > 55:
                print('Time too long')
                continue
        result = client.asr(getFileContent(path + fileName), 'wav', 16000, {'dev_pid': 1537, })
        print(fileName + ' Finished.')
        with open('result.txt', "w", encoding="utf-8") as f: # Reslove Unicode encoding error
            f.write(fileName + ': ' + result['result'][0] + '\n')
            f.close()
    print('Finished Processing.')
    f.close()

if __name__ == '__main__':
    main()

