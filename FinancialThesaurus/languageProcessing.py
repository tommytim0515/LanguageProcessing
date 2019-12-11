import xlwt # Write Excel
import xlrd # Read Excel 
import jieba
import jieba.analyse
import math
import re
import json

# Load user defined dictionary
jieba.load_userdict('newWords.txt') 

# Symbols to be removed
puncs = json.load(open('punc.json', encoding='utf-8-sig'))['puncs']
partOfSpeech = ('Ag', 'a', 'd', 'c', 'e', 'm', 'q', 'tg', 't', 'u', 'y', 'v', 'vg', 'vd', 'vn', 'ns', )

# Defined the path to be executed
paths = {
    'source/': {
        'Macro_News/': { '10jqka_news_20190114.xlsx': (2, 3),
                        'eastmoney_news_20190114.xlsx': (2, 3),
                        'tushare_clean_news_20190114.xlsx': (2, 3),
                        'wallstreetcn_news_20190114.xlsx': (2, 3),
                        'yuncaijing_news_20190114.xlsx': (2, 3),
        }
    }
}

# path = 'source/Macro_News/10jqka_news_20190114.xlsx'

if __name__ == "__main__":
    wbk = xlwt.Workbook(encoding='ascii')
    sheet = wbk.add_sheet('FinalThresaurus')
    wordList = []
    keyList = []
    for subPath in paths['source/']:
        for fileName in paths['source/'][subPath]:
            workBook = xlrd.open_workbook('source/' + subPath + fileName)
            workSheet = workBook.sheet_by_index(0)
            totalRow = workSheet.nrows
            totalCol = workSheet.ncols
            print('{} rows in total.'.format(str(totalRow)))
            for i in range(totalRow):
                print('Executing {}th row'.format(str(i)))
                for index in paths['source/'][subPath][fileName]:
                    values = workSheet.cell(i, index).value
                    try:
                        item = values.strip('\n\r')
                        keyWords = jieba.cut(item)
                        # Process text with Jieba
                        sentenceSegd = jieba.posseg.cut(item)
                        outStr = ''
                        for word in sentenceSegd:
                            if word.flag not in partOfSpeech:
                                outStr += word.word
                        # Get the total number of words in a text
                        totalWordNum = len(list(jieba.cut(outStr)))
                        # Get the number of keywords to pick
                        getCount = math.ceil(totalWordNum*0.07)
                        keyWords = jieba.analyse.extract_tags(outStr, topK = getCount)
                        for t in keyWords:
                            if (t[-1] != '%') and (not (t in puncs)) and (re.match(r'^-?\d+(?:\.\d+)?$', t) is None):
                                wordList.append(t)
                    except:
                        print('Error Happend.')

    word_dict = {}
    print('Counting Numbers and record results into text file')
    with open('wordCount.txt', 'w', encoding='utf-8') as wf2: 

        for item in wordList:
            if item not in word_dict: 
                word_dict[item] = 1
            else:
                word_dict[item] += 1

        orderList = list(word_dict.values())
        orderList.sort(reverse=True)
        # print orderList
        for i in range(len(orderList)):
            for key in word_dict:
                if word_dict[key] == orderList[i]:
                    wf2.write(key+' '+str(word_dict[key])+'\n') 
                    keyList.append(key)
                    word_dict[key] = 0
    print('Record result in Excel.')
    for i in range(len(keyList)):
        sheet.write(i, 1, label=orderList[i])
        sheet.write(i, 0, label=keyList[i])
    wbk.save('wordCount.xls')  
    print('Finished Processing.')