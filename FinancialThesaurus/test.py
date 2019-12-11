import xlwt # Write Excel
import xlrd # Read Excel 
import jieba
import jieba.analyse
import math
import re
import json

data = json.load(open('punc.json', encoding='utf-8-sig'))
print(data['puncs'])

