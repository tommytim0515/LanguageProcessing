from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt 

wordList = {}
stopwords = ''
with open('wordCount.txt', 'r', encoding ='UTF-8') as text:
    counter = 0
    for line in text:
        wordAndFreq = line.split(' ')
        word = wordAndFreq[0]
        freq = int(wordAndFreq[1])
        wordList.update({word: freq})
        counter += 1
        if counter > 100:
            stopwords = word
            break
    
wordcloud = WordCloud(width = 800, height = 800, 
                font_path="C:/Windows/Fonts/simfang.ttf",
                background_color ='white', 
                stopwords = stopwords, 
                min_font_size = 10).generate_from_frequencies(frequencies=wordList) 
  
# plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
  
plt.show() 

wordcloud.to_file('wordcloud.jpg')