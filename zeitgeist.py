#!/usr/bin/env python3

# Libraries
from wordcloud import WordCloud
import matplotlib.pyplot as plt
#import requests
#from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as soup
#import sys
#import json
from stop_words import get_stop_words
from urllib.request import urlopen
import feedparser
import PySimpleGUI as sg
import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import collections
import pandas as pd


allArticles = []
counter = int(0)
filename=''

class WhizRssAggregator():
    feedurl = ""

    def __init__(self, paramrssurl):
        self.feedurl = paramrssurl
        self.parse()

    def parse(self):
        thefeed = feedparser.parse(self.feedurl)
        output=''

        for thefeedentry in thefeed.entries:

            output += '{} '.format(thefeedentry.get("title", ""))
            allArticles.append(thefeedentry.get("title", ""))
            allArticles.append(thefeedentry.get("description", ""))
            allArticles.append('--------')

        listOutput=output.split()
        filtered_output = [word for word in listOutput if word not in get_stop_words('italian')]
        string_filtered_output = ' '.join(filtered_output)
        
        # Create the wordcloud object
        wordcloud = WordCloud(width=480, height=480, margin=0).generate(string_filtered_output)
        plt.figure(num='RSS feed')
        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.margins(x=0, y=0)
        plt.savefig(rssfeednameslist[counter]+'_'+filename+'.png')


def googlenews():
    global filename
    #GOOGLE NEWS
    news_url="https://news.google.com/news/rss"
    Client=urlopen(news_url)
    xml_page=Client.read()
    Client.close()
    
    soup_page=soup(xml_page,"xml")
    news_list=soup_page.findAll("item")
    
    output=''
    # Print news title, url and publish date
    for news in news_list:
        output += '{} '.format(news.title.text)

    listOutput=output.split()

    for tmpoutput in output.split("', '"):
        allArticles.append(tmpoutput)
        allArticles.append('--------')

    filtered_output = [word for word in listOutput if word not in get_stop_words('english')]
    string_filtered_output = ' '.join(filtered_output)
    
    # Create the wordcloud object
    wordcloud = WordCloud(width=480, height=480, margin=0).generate(string_filtered_output)
    plt.figure(num='news.google.com')
    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.margins(x=0, y=0)
    plt.savefig('Google_news_'+filename+'.png')

    #PDF
    im = Image('Google_news_'+filename+'.png', 0*inch, 0*inch)
    Story.append(im)
    Story.append(Paragraph('Google_news', styles["Normal"]))       

# Add a touch of color
sg.change_look_and_feel('DarkBrown1')

RSSList = "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml"
RSSList += ",http://xml2.corriereobjects.it/rss/economia.xml"
RSSList += ",http://www.ansa.it/sito/notizie/topnews/topnews_rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/region/europe/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/region/americas/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/region/middle-east/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/region/africa/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/region/asia-pacific/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/topic/health/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/topic/culture-and-education/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/topic/climate-change/feed/rss.xml"
RSSList += ",https://news.un.org/feed/subscribe/en/news/topic/economic-development/feed/rss.xml"


RSSNames = "AnsaMondo"
RSSNames += ",AnsaEconomia"
RSSNames += ",AnsaTopNews"
RSSNames += ",UNEurope"
RSSNames += ",UNAmericas"
RSSNames += ",UNMiddleEast"
RSSNames += ",UNAfrica"
RSSNames += ",UNAsiaPacific"
RSSNames += ",UNhealth"
RSSNames += ",UNCultureAndEducation"
RSSNames += ",UNClimateChange"
RSSNames += ",UNEconomicDevelopment"




# All the stuff inside your window.
layout = [  [sg.Text('Feed RSS List')],[sg.Multiline(RSSList, size=(55,15))],
            [sg.Text('Feed RSS Names')],[ sg.Multiline(RSSNames, size=(55,15))],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Zeitgeist', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        break
    #global filename
    #PDF
    filename=time.strftime("%Y%m%d%H%M%S", time.localtime())
    fileTxt = open(filename+'_analyze_text.txt', 'a', encoding="utf-8")
    doc = SimpleDocTemplate(filename+".pdf",pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)
    Story=[]
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    rssfeedlist=values[0].replace("\n", "").split(",")
    rssfeednameslist=values[1].replace("\n", "").split(",")
    imZeitgeist = Image('Zeitgeist_small.png', 0*inch, 0*inch)
    Story.append(imZeitgeist)
    
    #GOOGLE NEWS
    googlenews()

    #RSS FEED
    for feed in rssfeedlist:
        WhizRssAggregator(feed)
        im = Image(rssfeednameslist[counter]+'_'+filename+'.png', 0*inch, 0*inch)
        Story.append(im)
        Story.append(Paragraph(rssfeednameslist[counter], styles["Normal"]))       
        fileTxt.write(rssfeednameslist[counter])
        counter += 1

    for artic in allArticles:
        Story.append(Paragraph(artic, styles["Normal"]))
        fileTxt.write(str(artic))
    
    # Close the file
    fileTxt.close()
    fileExamine = open(filename+'_analyze_text.txt', encoding='utf8')
    a= fileExamine.read()
    # Stopwords
    stopwords = set(line.strip() for line in open('stopwords.txt'))
    stopwords = stopwords.union(set(['mr','mrs','one','two','said']))
    # Instantiate a dictionary, and for every word in the file, 
    # Add to the dictionary if it doesn't exist. If it does, increase the count.
    wordcount = {}
    # To eliminate duplicates, remember to split by punctuation, and use case demiliters.
    for word in a.lower().split():
        word = word.replace(".","")
        word = word.replace(",","")
        word = word.replace(":","")
        word = word.replace("\"","")
        word = word.replace("!","")
        word = word.replace("â€œ","")
        word = word.replace("â€˜","")
        word = word.replace("*","")
        if word not in stopwords:
            if word not in wordcount:
                wordcount[word] = 1
            else:
                wordcount[word] += 1
    # Print most common word
    n_print = int(30)
    print("\n The {} most common words are as follows\n".format(n_print))
    word_counter = collections.Counter(wordcount)
    for word, count in word_counter.most_common(n_print):
        print(word, ": ", count)
    # Close the file
    fileExamine.close()
    # Create a data frame of the most common words 
    # Draw a bar chart
    lst = word_counter.most_common(n_print)
    df = pd.DataFrame(lst, columns = ['Word', 'Count'])
    anax=df.plot.bar(x='Word',y='Count')
    anax.figure.savefig('analyzedtext_'+filename+'.png', bbox_inches='tight')
    
    #PDF
    imtxt = Image('analyzedtext'+'_'+filename+'.png', 0*inch, 0*inch)
    Story.append(imtxt)
       
    doc.build(Story)
    
    print('All done!')
    break
window.close()
